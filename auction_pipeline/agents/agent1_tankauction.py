"""
Agent 1: TankAuction 스크래퍼 & 문서 다운로더
- 로그인, 검색, 목록 파싱, 상세 정보 추출, 문서 다운로드
"""

import asyncio
import json
import re
import logging
import random
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import SearchCriteria, AuctionCase, PropertyDetails
from config import (TANK_ID, TANK_PW, TANK_BASE_URL, HEADLESS,
                    BROWSER_TIMEOUT, DOCS_DIR, IMAGES_DIR,
                    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)

logger = logging.getLogger("agent1")

MAX_CASES = 1  # 테스트: 1건만 처리


class TankAuctionAgent:
    """TankAuction 스크래퍼 에이전트"""

    def __init__(self, docs_dir: Path = DOCS_DIR):
        self.base_url = TANK_BASE_URL
        self.docs_dir = docs_dir
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=HEADLESS,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
            ],
        )
        self.context = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="ko-KR",
            accept_downloads=True,
            ignore_https_errors=True,
        )
        self.page = await self.context.new_page()
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
            window.chrome = {runtime: {}};
        """)
        return self

    async def __aexit__(self, *args):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _delay(self):
        await asyncio.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    # ── 로그인 ────────────────────────────────────────────────────
    async def login(self) -> bool:
        if not TANK_ID or not TANK_PW:
            raise ValueError(".env에 TANK_ID, TANK_PW 설정 필요")

        logger.info("탱크옥션 메인 접속...")
        await self.page.goto(self.base_url, wait_until="networkidle", timeout=BROWSER_TIMEOUT)
        await asyncio.sleep(2.0)

        content = await self.page.content()
        if "로그아웃" in content and "client_id" not in content:
            logger.info("이미 로그인 상태")
            return True

        # 로그인 팝업 오픈
        popup_btn = await self.page.query_selector('[data-action="loginDivBtn"]')
        if popup_btn:
            await popup_btn.click()
            await asyncio.sleep(1.5)

        try:
            id_elem = await self.page.wait_for_selector(
                'input[name="client_id"], #client_id', timeout=8000, state="visible"
            )
        except Exception:
            logger.error("ID 입력 필드를 찾지 못했습니다")
            logs_dir = Path(__file__).parent.parent / "logs"
            logs_dir.mkdir(exist_ok=True)
            await self.page.screenshot(path=str(logs_dir / "login_fail.png"))
            return False

        await id_elem.fill(TANK_ID)
        await asyncio.sleep(0.3)

        pw_elem = await self.page.query_selector('input[name="passwd"], #passwd')
        if not pw_elem:
            logger.error("PW 입력 필드를 찾지 못했습니다")
            return False
        await pw_elem.fill(TANK_PW)
        await asyncio.sleep(0.3)

        login_btn = await self.page.query_selector('#loginBtn')
        if login_btn:
            await login_btn.click()
        else:
            await self.page.keyboard.press("Enter")

        # AJAX 로그인 대기 (networkidle이 너무 빨리 완료됨)
        try:
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        await asyncio.sleep(4.0)

        content = await self.page.content()
        if "로그아웃" in content or "마이페이지" in content:
            logger.info("TankAuction 로그인 성공")
            return True

        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        await self.page.screenshot(path=str(logs_dir / "login_fail.png"))
        logger.error("로그인 실패 -- logs/login_fail.png 확인")
        return False

    # ── 검색 ────────────────────────────────────────────────────
    async def search(self, criteria: SearchCriteria) -> list[AuctionCase]:
        search_url = f"{self.base_url}/ca/caList.php"
        logger.info(f"검색 페이지: {search_url}")

        await self.page.goto(search_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
        await asyncio.sleep(2.0)

        await self._set_search_filters(criteria)

        # 검색 버튼 클릭 (#btnSrch - SPAN 요소)
        btn = await self.page.query_selector('#btnSrch')
        if btn:
            await btn.click()
        else:
            logger.warning("#btnSrch 를 찾지 못함")
        await asyncio.sleep(3.0)
        try:
            await self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await asyncio.sleep(2.0)

        all_cases: list[AuctionCase] = []
        page_num = 0

        while len(all_cases) < MAX_CASES:
            page_num += 1
            cases = await self._parse_list_page()
            logger.info(f"  페이지 {page_num}: {len(cases)}건")
            all_cases.extend(cases)

            if len(all_cases) >= MAX_CASES:
                all_cases = all_cases[:MAX_CASES]
                break

            # 다음 페이지 버튼 탐색
            next_btn = await self.page.query_selector(
                'a.next:not(.disabled), a[class*="next"]:not([class*="disabled"])'
            )
            if not next_btn:
                # 숫자 페이지 링크 방식
                current_page_el = await self.page.query_selector('.pagination .active, .paging .on')
                if current_page_el:
                    current_txt = (await current_page_el.inner_text()).strip()
                    next_page_link = await self.page.query_selector(
                        f'.pagination a:has-text("{int(current_txt)+1}")'
                        if current_txt.isdigit() else ""
                    )
                    if next_page_link:
                        await next_page_link.click()
                        await asyncio.sleep(2.5)
                        continue
                break

            await next_btn.click()
            await asyncio.sleep(2.5)

        logger.info(f"검색 완료: 총 {len(all_cases)}건 (상한 {MAX_CASES})")
        return all_cases

    async def _set_search_filters(self, criteria: SearchCriteria):
        # 시도 선택 (select[name="siCd"])
        try:
            await self.page.select_option('select[name="siCd"]', label=criteria.city)
            logger.info(f"  시도 선택: {criteria.city}")
        except Exception as e:
            logger.warning(f"  siCd 선택 실패: {e}")

        # guCd AJAX 로딩 대기 (option[value!="0"] 가 나타날 때까지)
        await asyncio.sleep(2.0)
        opts = []
        for _ in range(5):
            opts = await self.page.evaluate(
                "() => { return Array.from(document.querySelectorAll('select[name=\"guCd\"] option')).filter(function(o){return o.value && o.value !== '0';}).map(function(o){return {v:o.value,t:o.textContent.trim()};}); }"
            )
            if opts:
                break
            await asyncio.sleep(1.0)

        # 시군구 선택 (label로 먼저, 실패 시 텍스트 포함 값으로)
        try:
            await self.page.select_option('select[name="guCd"]', label=criteria.district)
            await asyncio.sleep(0.5)
            logger.info(f"  시군구 선택: {criteria.district}")
        except Exception:
            # label 매칭 실패 시 텍스트 포함 옵션 value 직접 지정
            try:
                match_val = next(
                    (o["v"] for o in opts if criteria.district in o["t"]), None
                )
                if match_val:
                    await self.page.select_option('select[name="guCd"]', value=match_val)
                    await asyncio.sleep(0.5)
                    logger.info(f"  시군구 선택(value={match_val}): {criteria.district}")
                else:
                    logger.warning(f"  guCd 에서 {criteria.district}를 찾지 못함")
            except Exception as e2:
                logger.warning(f"  guCd 선택 실패: {e2}")

        # 물건종류 선택 (select[name="ctgr"])
        type_label = criteria.property_type  # 예: "아파트"
        try:
            await self.page.select_option('select[name="ctgr"]', label=type_label)
            await asyncio.sleep(0.5)
            logger.info(f"  물건종류 선택: {type_label}")
        except Exception as e:
            logger.warning(f"  ctgr 선택 실패: {e}")

        # 물건상태 선택 (select[name="stat"]) — "진행물건"
        try:
            await self.page.select_option('select[name="stat"]', label="진행물건")
            await asyncio.sleep(0.5)
            logger.info("  상태 선택: 진행물건")
        except Exception as e:
            logger.warning(f"  stat 선택 실패: {e}")

    async def _parse_list_page(self) -> list[AuctionCase]:
        # JavaScript로 브라우저 내에서 직접 DOM 파싱 (selector 이슈 우회)
        items_data: list[dict] = await self.page.evaluate("""
            () => {
                const items = document.querySelectorAll('.js-open-pn[data-tid]');
                return Array.from(items).map(item => {
                    const tid  = item.getAttribute('data-tid') || '';
                    const row  = item.getAttribute('data-row') || '0';
                    const saNo = item.querySelector('[id^="saNo_"]');
                    const ctgr = item.querySelector('[id^="ctgr_"]');
                    const addr = item.querySelector('.f13');
                    const area = item.querySelector('.blue.f12');
                    // 금액 정보
                    const apprEl  = item.querySelector('.appr, [class*="appr"]');
                    const bidEl   = item.querySelector('.minbid, [class*="minbid"], .min_bid');
                    const dateEl  = item.querySelector('.date, [class*="date"]');
                    return {
                        tid:      tid,
                        row:      row,
                        case_no:  saNo ? saNo.textContent.trim() : '',
                        prop_type: ctgr ? ctgr.textContent.trim() : '',
                        address:  addr ? addr.textContent.replace(/\\n/g,' ').trim() : '',
                        area_text: area ? area.textContent.trim() : '',
                        appr_text: apprEl ? apprEl.textContent.trim() : '',
                        bid_text:  bidEl  ? bidEl.textContent.trim()  : '',
                        date_text: dateEl ? dateEl.textContent.trim()  : ''
                    };
                }).filter(x => x.case_no !== '');
            }
        """)

        cases: list[AuctionCase] = []
        base = self.base_url
        for item in items_data:
            tid = item["tid"]
            case_no = item["case_no"]
            if not case_no:
                continue

            detail_url = (
                f"{base}/ca/inc/component/popup/caView.php"
                f"?tid={tid}&chkNo={item['row']}&TotNo=20&opener_1st_no={tid}"
            )

            # 면적 파싱: "건물 84.98㎡(25.706평), 대지권 45.774㎡(13.847평)"
            areas = re.findall(r"([\d.]+)\s*(?:㎡|m²)", item.get("area_text", ""))
            area_supply  = float(areas[0]) if len(areas) > 0 else 0.0
            area_land    = float(areas[1]) if len(areas) > 1 else 0.0

            cases.append(AuctionCase(
                case_no=case_no,
                court="",
                address=item.get("address", ""),
                detail_url=detail_url,
                min_bid=self._to_int(item.get("bid_text", "")),
                appraisal_value=self._to_int(item.get("appr_text", "")),
                bid_date=item.get("date_text", ""),
                status="진행",
                tid=tid,
                area_supply=area_supply,
                area_land=area_land,
            ))

        return cases

    def _to_int(self, text: str) -> int:
        clean = re.sub(r"[^\d]", "", text)
        return int(clean) if clean else 0

    # ── 상세 정보 ─────────────────────────────────────────────────
    async def get_property_details(self, case: AuctionCase) -> PropertyDetails:
        detail_page = await self.context.new_page()
        try:
            logger.info(f"  상세 페이지 접속: tid={case.tid}")
            await detail_page.goto(
                case.detail_url, wait_until="networkidle", timeout=30000
            )
            await asyncio.sleep(2.0)

            # 전체 텍스트 추출
            content = await detail_page.content()

            # 단지명
            complex_name = await self._page_text(
                detail_page,
                'td:has-text("단지명") + td, .complex-name, [class*="complex"]'
            ) or self._complex_from_address(case.address)

            # 동/호
            building_no, unit_no = self._parse_building_unit(case.address, content)

            # 층 (주소에서 직접 파싱)
            floor = self._parse_floor(case.address, content)

            # 면적
            areas = re.findall(r"([\d.]+)\s*(?:㎡|m²)", content)
            area_supply  = float(areas[0]) if len(areas) > 0 else case.area_supply
            area_private = float(areas[1]) if len(areas) > 1 else 0.0
            area_land    = float(areas[2]) if len(areas) > 2 else case.area_land

            # 감정가 / 최저가 (목록에서 가져옴)
            appr_text = await self._page_text(
                detail_page, 'td:has-text("감정가") + td, .appraisal'
            )
            bid_text = await self._page_text(
                detail_page, 'td:has-text("최저") + td, .min-bid'
            )
            if appr_text:
                case.appraisal_value = self._to_int(appr_text)
            if bid_text:
                case.min_bid = self._to_int(bid_text)

            # 문서 다운로드
            case_dir = self.docs_dir / case.case_no.replace("-", "_")
            case_dir.mkdir(parents=True, exist_ok=True)
            doc_paths = await self.download_documents(detail_page, case, case_dir)

            return PropertyDetails(
                case_no=case.case_no,
                complex_name=complex_name,
                building_no=building_no,
                unit_no=unit_no,
                floor=floor,
                area_supply=area_supply,
                area_private=area_private,
                area_land=area_land,
                land_status=await self._page_text(
                    detail_page,
                    'td:has-text("토지현황") + td, td:has-text("토지이용") + td'
                ),
                building_status=await self._page_text(
                    detail_page,
                    'td:has-text("건물현황") + td, td:has-text("건물이용") + td'
                ),
                tenant_info=await self._page_text(
                    detail_page,
                    'td:has-text("임차인") + td, td:has-text("세입자") + td'
                ),
                registry_info=await self._page_text(
                    detail_page,
                    'td:has-text("등기") + td, td:has-text("권리관계") + td'
                ),
                doc_paths=doc_paths,
            )
        finally:
            await detail_page.close()

    async def _page_text(self, page: Page, selector: str) -> str:
        try:
            elem = await page.query_selector(selector)
            if elem:
                return (await elem.inner_text()).strip()
        except Exception:
            pass
        return ""

    def _complex_from_address(self, address: str) -> str:
        # 패턴1: (동이름,단지명) 형식 — 괄호 내 쉼표 뒤
        m = re.search(r'\(([^,)]+),([^)]+)\)', address)
        if m:
            name = m.group(2).strip()
            if name and not re.match(r'^대[전구광]', name):
                return name
        # 패턴2: 아파트·하늘채·마을·힐·파크 등 키워드 포함 단어
        m = re.search(
            r'([가-힣a-zA-Z0-9]+(?:아파트|APT|apt|하늘채|마을|힐스|파크|타운|뷰|리버|시티|캐슬|자이|래미안|푸르지오|아이파크))',
            address
        )
        if m:
            return m.group(1)
        # 패턴3: 지번 다음, X동 앞에 오는 단어 (예: "4-7 스마트시티 501동")
        m = re.search(r'\d+(?:-\d+)?\s+([가-힣a-zA-Z0-9]+(?:시티|타워|빌|하우스)?)\s+\d+동', address)
        if m and len(m.group(1)) >= 2:
            return m.group(1)
        return ""

    def _parse_building_unit(self, address: str, content: str) -> tuple[str, str]:
        building, unit = "", ""
        for text in [address, content[:3000]]:
            # 동 추출
            mb = re.search(r"(\d+)동", text)
            # 호 추출 (층 번호와 구분: 1층1401호 → 호는 1401)
            mu = re.search(r"(?:\d+층)?(\d+)호", text)
            if mb:
                building = mb.group(1) + "동"
            if mu:
                unit = mu.group(1) + "호"
            if building and unit:
                break
        return building, unit

    def _parse_floor(self, address: str, content: str) -> str:
        for text in [address, content[:3000]]:
            m = re.search(r"(\d+)층", text)
            if m:
                return m.group(1) + "층"
        return ""

    # ── 문서 다운로드 ───────────────────────────────────────────────
    async def download_documents(
        self, page: Page, case: AuctionCase, save_dir: Path
    ) -> dict[str, str]:
        doc_types = {
            "현황조사서": ["현황조사서", "현황조사"],
            "매각물건명세서": ["매각물건명세서", "물건명세서"],
            "건물등기": ["건물등기부", "등기사항", "등기부등본"],
            "세대열람": ["세대열람", "전입세대", "세대확인"],
        }

        downloaded: dict[str, str] = {}

        # 모든 링크 수집
        links = await page.query_selector_all(
            'a[href*=".pdf"], a[href*="download"], a[href*="doc"],'
            ' a[onclick*="pdf"], a[onclick*="down"]'
        )

        for doc_type, keywords in doc_types.items():
            for link in links:
                try:
                    text = (await link.inner_text()).strip()
                    href = (await link.get_attribute("href")) or ""
                    onclick = (await link.get_attribute("onclick")) or ""
                    combined = text + href + onclick
                    if not any(kw in combined for kw in keywords):
                        continue

                    path = await self._download_link(page, link, save_dir, doc_type)
                    if path:
                        downloaded[doc_type] = str(path)
                        logger.info(f"    다운로드: {doc_type} -> {path.name}")
                        break
                except Exception as e:
                    logger.debug(f"    {doc_type} 링크 처리 오류: {e}")

        # 다운로드 안 된 문서 → 스크린샷 fallback
        for doc_type in doc_types:
            if doc_type not in downloaded:
                shot_path = save_dir / f"{doc_type}_screenshot.png"
                try:
                    await page.screenshot(path=str(shot_path), full_page=True)
                    downloaded[doc_type] = str(shot_path)
                    logger.info(f"    스크린샷 fallback: {doc_type}")
                except Exception:
                    pass

        return downloaded

    async def _download_link(
        self, page: Page, link_elem, save_dir: Path, doc_type: str
    ) -> Optional[Path]:
        href = (await link_elem.get_attribute("href")) or ""
        url = f"{self.base_url}{href}" if href.startswith("/") else href

        # 다운로드 시도
        try:
            async with page.expect_download(timeout=15000) as dl_info:
                await link_elem.click()
            dl = await dl_info.value
            file_path = save_dir / f"{doc_type}.pdf"
            await dl.save_as(str(file_path))
            return file_path
        except Exception:
            pass

        # 새 탭에서 스크린샷
        if url and url.startswith("http"):
            try:
                page2 = await self.context.new_page()
                await page2.goto(url, timeout=15000)
                await asyncio.sleep(1.5)
                shot = save_dir / f"{doc_type}_view.png"
                await page2.screenshot(path=str(shot), full_page=True)
                await page2.close()
                return shot
            except Exception:
                pass

        return None

    # ── 메인 실행 ──────────────────────────────────────────────────
    async def run(self, criteria: SearchCriteria) -> dict:
        result: dict = {
            "agent": "agent1_tankauction",
            "status": "success",
            "criteria": {
                "city": criteria.city,
                "district": criteria.district,
                "property_type": criteria.property_type,
                "status": criteria.status,
                "min_area": criteria.min_area,
            },
            "cases": [],
            "errors": [],
        }

        try:
            logged_in = await self.login()
            if not logged_in:
                result["status"] = "blocked"
                result["errors"].append("로그인 실패")
                return result

            cases = await self.search(criteria)

            for i, case in enumerate(cases, 1):
                entry = self._case_to_dict(case)
                logger.info(f"[{i}/{len(cases)}] {case.case_no} 상세 수집 중...")
                try:
                    details = await self.get_property_details(case)
                    entry["details"] = self._details_to_dict(details)
                except Exception as e:
                    entry["error"] = str(e)
                    result["errors"].append(f"{case.case_no}: {e}")
                    logger.warning(f"  상세 수집 오류: {e}")

                result["cases"].append(entry)
                await self._delay()

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))
            logger.error(f"Agent1 오류: {e}", exc_info=True)

        return result

    def _case_to_dict(self, c: AuctionCase) -> dict:
        return {
            "case_no": c.case_no,
            "court": c.court,
            "address": c.address,
            "detail_url": c.detail_url,
            "min_bid": c.min_bid,
            "appraisal_value": c.appraisal_value,
            "bid_date": c.bid_date,
            "status": c.status,
            "tid": c.tid,
            "area_supply": c.area_supply,
            "area_land": c.area_land,
            "details": None,
            "error": None,
        }

    def _details_to_dict(self, d: PropertyDetails) -> dict:
        return {
            "complex_name": d.complex_name,
            "building_no": d.building_no,
            "unit_no": d.unit_no,
            "floor": d.floor,
            "area_supply": d.area_supply,
            "area_private": d.area_private,
            "area_land": d.area_land,
            "land_status": d.land_status,
            "building_status": d.building_status,
            "tenant_info": d.tenant_info,
            "registry_info": d.registry_info,
            "doc_paths": d.doc_paths,
        }


async def run_agent1(criteria: SearchCriteria) -> dict:
    async with TankAuctionAgent() as agent:
        return await agent.run(criteria)


if __name__ == "__main__":
    criteria = SearchCriteria(city="대전", district="유성구")
    result = asyncio.run(run_agent1(criteria))
    print(json.dumps(result, ensure_ascii=False, indent=2))
