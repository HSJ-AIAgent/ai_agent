"""
Agent 2: 네이버 부동산 & 아실 데이터 수집기
- 단지 정보, 매물 리스트, 5년 가격 추이 그래프, 실거래가 통계
"""

import asyncio
import json
import re
import logging
import random
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import (
    PropertyDetails, NaverData, AsilData, LayoutInfo,
    ListingItem, TransactionStat, RecentTransaction,
)
from config import (
    HEADLESS, BROWSER_TIMEOUT, IMAGES_DIR,
    NAVER_LAND_URL, ASIL_URL,
    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX,
)

logger = logging.getLogger("agent2")


class NaverAsilAgent:
    """네이버 부동산 + 아실 데이터 수집 에이전트"""

    def __init__(self, images_dir: Path = IMAGES_DIR):
        self.images_dir = images_dir
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        ctx = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1600, "height": 900},
            locale="ko-KR",
        )
        self.page = await ctx.new_page()
        return self

    async def __aexit__(self, *args):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _delay(self):
        await asyncio.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    # ── 네이버 부동산 ─────────────────────────────────────────────
    async def fetch_naver(
        self, details: PropertyDetails, case_no: str
    ) -> NaverData:
        complex_name = details.complex_name
        naver_data = NaverData(complex_name=complex_name)

        if not complex_name:
            logger.warning("단지명 없음 — 네이버 수집 건너뜀")
            return naver_data

        # ① 네이버 부동산 메인 검색 (SPA 방식)
        try:
            await self.page.goto(
                NAVER_LAND_URL, wait_until="domcontentloaded", timeout=12000
            )
            await asyncio.sleep(2)

            inp = await self.page.query_selector(
                'input[placeholder*=단지], input[placeholder*=검색], '
                'input[type=search], .search-input input'
            )
            if inp:
                await inp.click()
                await asyncio.sleep(0.3)
                await inp.fill(complex_name)
                await asyncio.sleep(3)  # 자동완성 대기

                # 자동완성에서 단지 결과 클릭
                suggestions = await self.page.query_selector_all(
                    '[class*=item], [role=option], [class*=suggest], li[data-id]'
                )
                clicked = False
                for sug in suggestions:
                    txt = (await sug.inner_text()).strip()
                    if complex_name[:3] in txt and len(txt) < 60:
                        await sug.click()
                        await asyncio.sleep(3)
                        clicked = True
                        break

                if not clicked:
                    await self.page.keyboard.press("Enter")
                    await asyncio.sleep(3)

            # 단지 페이지 도달 확인
            url_match = re.search(r"complexNo=(\d+)|/complex/(\d+)", self.page.url)
            if url_match:
                naver_data.complex_id = url_match.group(1) or url_match.group(2)
                naver_data.layout_info = await self._get_layout_info(details, case_no)
                naver_data.listings = await self._get_listings(details, case_no)
                naver_data.price_graph_path = await self._capture_price_graph(case_no, "매매")
                naver_data.jeonse_graph_path = await self._capture_price_graph(case_no, "전세")

                unit_text = await self._extract_text(
                    '.complex_detail .count, .complex_info .total, td:has-text("총세대") + td'
                )
                m = re.search(r"([\d,]+)\s*세대", unit_text)
                if m:
                    naver_data.unit_count = int(m.group(1).replace(",", ""))

                logger.info(f"✓ 네이버 수집 완료: {complex_name} (매물 {len(naver_data.listings)}건)")
            else:
                logger.warning(f"네이버 단지 페이지 도달 실패: {complex_name}")

        except Exception as e:
            logger.warning(f"네이버 수집 오류 ({complex_name}): {e}")

        return naver_data

    async def _get_layout_info(
        self, details: PropertyDetails, case_no: str
    ) -> list[LayoutInfo]:
        layouts = []

        # 타입 탭 클릭
        type_tabs = await self.page.query_selector_all(
            '.type_tab li, .area_tab li, .tab_type a'
        )
        target_area = details.area_private

        for tab in type_tabs:
            tab_text = (await tab.inner_text()).strip()
            area_m = re.search(r"([\d.]+)", tab_text)
            if not area_m:
                continue

            tab_area = float(area_m.group(1))
            # 전용면적 ±5㎡ 범위 내 타입
            if abs(tab_area - target_area) <= 5:
                await tab.click()
                await self._delay()

                layout_type = tab_text
                rooms = await self._extract_int('.rooms, td:has-text("방") + td')
                baths = await self._extract_int('.baths, td:has-text("욕실") + td')
                maint = await self._extract_int('.maintenance, td:has-text("관리비") + td')
                active = await self._extract_int('.active_count, .listing-count')

                # 평면도 캡처
                plan_path = await self._capture_element(
                    '.floor_plan img, .plan_img, .type_img',
                    self.images_dir / f"{case_no}_floor_plan_{layout_type}.png",
                )

                layouts.append(
                    LayoutInfo(
                        layout_type=layout_type,
                        rooms=rooms,
                        bathrooms=baths,
                        maintenance_fee=maint,
                        active_listings=active,
                        floor_plan_path=str(plan_path) if plan_path else "",
                    )
                )

        return layouts

    async def _get_listings(
        self, details: PropertyDetails, case_no: str
    ) -> list[ListingItem]:
        listings = []

        # 매매 탭으로 이동
        for sel in [
            'a:has-text("매매")', '.deal_tab', 'button:has-text("매매")'
        ]:
            try:
                btn = await self.page.query_selector(sel)
                if btn:
                    await btn.click()
                    await self._delay()
                    break
            except Exception:
                pass

        # 타입 필터 (해당 평형)
        await self._filter_by_area(details.area_private)

        # 매물 전체 캡처 (Sheet4 형식)
        rows = await self.page.query_selector_all(
            '.article_list li, .item_list .item, .list_item'
        )

        for i, row in enumerate(rows[:60], start=1):
            try:
                item = await self._parse_listing_row(row, i)
                if item:
                    listings.append(item)
            except Exception as e:
                logger.debug(f"매물 행 파싱 오류: {e}")

        logger.info(f"  네이버 매물 {len(listings)}건 수집")
        return listings

    async def _filter_by_area(self, area: float):
        area_btn_sel = (
            f'.area_filter button:has-text("{int(area)}"), '
            f'.type_filter li:has-text("{int(area)}")'
        )
        try:
            btn = await self.page.query_selector(area_btn_sel)
            if btn:
                await btn.click()
                await self._delay()
        except Exception:
            pass

    async def _parse_listing_row(self, row, seq: int) -> Optional[ListingItem]:
        price_text = await self._elem_text(row, '.price, .cost, .amount')
        if not price_text:
            return None

        price = self._parse_price(price_text)
        building = await self._elem_text(row, '.dong, .building')
        floor_text = await self._elem_text(row, '.floor, .층')
        layout = await self._elem_text(row, '.type, .area_type')
        orientation = await self._elem_text(row, '.direction, .향')
        view = await self._elem_text(row, '.view, .조망')
        notes = await self._elem_text(row, '.desc, .memo, .특이사항')
        reg_date = await self._elem_text(row, '.date, .reg_date')
        agency = await self._elem_text(row, '.agency, .중개사')
        area_text = await self._elem_text(row, '.area, .면적')
        area_m = re.search(r"([\d.]+)", area_text)

        return ListingItem(
            seq=seq,
            building=building,
            layout_type=layout,
            floor=floor_text,
            orientation=orientation,
            view=view,
            price=price,
            notes=notes,
            reg_date=reg_date,
            agency=agency,
            area=float(area_m.group(1)) if area_m else 0.0,
        )

    async def _capture_price_graph(self, case_no: str, trade_type: str) -> str:
        # 실거래가 탭 클릭
        for sel in [
            f'a:has-text("실거래가")', '.price_tab', 'button:has-text("시세")'
        ]:
            try:
                btn = await self.page.query_selector(sel)
                if btn:
                    await btn.click()
                    await self._delay()
                    break
            except Exception:
                pass

        # 매매/전세 선택
        for sel in [
            f'a:has-text("{trade_type}")',
            f'button:has-text("{trade_type}")',
            f'.deal_type:has-text("{trade_type}")',
        ]:
            try:
                btn = await self.page.query_selector(sel)
                if btn:
                    await btn.click()
                    await asyncio.sleep(1.5)
                    break
            except Exception:
                pass

        save_path = self.images_dir / f"{case_no}_price_graph_{trade_type}.png"
        captured = await self._capture_element(
            ".price_graph, .chart_wrap, canvas, .recharts-wrapper",
            save_path,
        )
        return str(captured) if captured else ""

    # ── 아실 (아파트실거래가) ──────────────────────────────────────
    async def fetch_asil(
        self, details: PropertyDetails, case_no: str
    ) -> AsilData:
        complex_name = details.complex_name
        asil_data = AsilData(
            complex_name=complex_name,
            target_area_type=f"{int(details.area_private)}㎡",
        )

        # 아실 메인 → 검색창 입력 방식
        try:
            await self.page.goto(
                f"{ASIL_URL}/asil/index.jsp",
                wait_until="domcontentloaded", timeout=12000
            )
            await asyncio.sleep(2)

            # 검색창 찾아서 입력
            inp = await self.page.query_selector(
                'input[type=text]:not([type=hidden]), input[placeholder*=검색]'
            )
            if inp and await inp.is_visible():
                await inp.fill(complex_name)
                await asyncio.sleep(0.5)
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(3)

            # 결과 클릭
            first = await self.page.query_selector(
                '.search-result li:first-child a, .result-item:first-child a, '
                '[class*=apt_item]:first-child a, ul.srh_lst li:first-child a'
            )
            if first:
                await first.click()
                await asyncio.sleep(3)
        except Exception as e:
            logger.debug(f"아실 검색 오류: {e}")

        # 연간 거래 통계 수집
        asil_data.annual_stats = await self._get_annual_stats()

        # 최근 3년 실거래 수집
        asil_data.recent_transactions = await self._get_recent_transactions(
            details.area_private
        )

        logger.info(
            f"✓ 아실 수집 완료: {complex_name} "
            f"(연간통계 {len(asil_data.annual_stats)}년, "
            f"실거래 {len(asil_data.recent_transactions)}건)"
        )
        return asil_data

    async def _get_annual_stats(self) -> list[TransactionStat]:
        stats = []
        # 연도별 통계 테이블
        rows = await self.page.query_selector_all(
            ".yearly-stats tr, .annual-table tbody tr, table.stats tbody tr"
        )

        for row in rows:
            cells = await row.query_selector_all("td, th")
            texts = [(await c.inner_text()).strip() for c in cells]
            if not texts or not re.match(r"20\d{2}", texts[0]):
                continue

            stats.append(
                TransactionStat(
                    year=int(texts[0]),
                    sale_count=self._to_int(texts[1] if len(texts) > 1 else "0"),
                    jeonse_count=self._to_int(texts[2] if len(texts) > 2 else "0"),
                    avg_sale_price=self._parse_price(texts[3] if len(texts) > 3 else "0"),
                    avg_jeonse_price=self._parse_price(texts[4] if len(texts) > 4 else "0"),
                )
            )

        stats.sort(key=lambda x: x.year, reverse=True)
        return stats[:5]

    async def _get_recent_transactions(
        self, target_area: float
    ) -> list[RecentTransaction]:
        transactions = []

        # 실거래 탭 클릭
        for sel in ['a:has-text("실거래")', '.tab-deal', 'button:has-text("거래")']:
            try:
                btn = await self.page.query_selector(sel)
                if btn:
                    await btn.click()
                    await self._delay()
                    break
            except Exception:
                pass

        rows = await self.page.query_selector_all(
            ".deal-list li, .transaction-item, table.deal tbody tr"
        )

        for row in rows[:50]:
            cells = await row.query_selector_all("td, .cell")
            texts = [(await c.inner_text()).strip() for c in cells]
            if not texts:
                continue

            area_m = re.search(r"([\d.]+)\s*㎡", " ".join(texts))
            if area_m and abs(float(area_m.group(1)) - target_area) > 8:
                continue

            date_m = re.search(r"(\d{4}[.-]\d{1,2})", " ".join(texts))
            floor_m = re.search(r"(\d+)\s*층", " ".join(texts))
            price_text = next((t for t in texts if re.search(r"\d+,?\d+", t)), "")

            transactions.append(
                RecentTransaction(
                    date=date_m.group(1) if date_m else "",
                    floor=floor_m.group(0) if floor_m else "",
                    area=float(area_m.group(1)) if area_m else 0.0,
                    price=self._parse_price(price_text),
                    transaction_type="매매",
                )
            )

        return transactions[:30]

    # ── 유틸 ──────────────────────────────────────────────────────
    async def _extract_text(self, selector: str) -> str:
        try:
            elem = await self.page.query_selector(selector)
            if elem:
                return (await elem.inner_text()).strip()
        except Exception:
            pass
        return ""

    async def _elem_text(self, parent, selector: str) -> str:
        try:
            elem = await parent.query_selector(selector)
            if elem:
                return (await elem.inner_text()).strip()
        except Exception:
            pass
        return ""

    async def _extract_int(self, selector: str) -> int:
        text = await self._extract_text(selector)
        m = re.search(r"[\d,]+", text)
        return int(m.group().replace(",", "")) if m else 0

    def _parse_price(self, text: str) -> int:
        # 억원 처리
        eok = re.search(r"([\d.]+)\s*억", text)
        man = re.search(r"([\d,]+)\s*만", text)
        val = 0
        if eok:
            val += int(float(eok.group(1)) * 10000)
        if man:
            val += int(man.group(1).replace(",", ""))
        if not val:
            clean = re.sub(r"[^\d]", "", text)
            val = int(clean) if clean else 0
        return val

    def _to_int(self, text: str) -> int:
        clean = re.sub(r"[^\d]", "", text)
        return int(clean) if clean else 0

    async def _capture_element(
        self, selector: str, save_path: Path
    ) -> Optional[Path]:
        try:
            elem = await self.page.query_selector(selector)
            if elem:
                await elem.screenshot(path=str(save_path))
                return save_path
        except Exception:
            pass
        try:
            await self.page.screenshot(path=str(save_path), full_page=False)
            return save_path
        except Exception:
            pass
        return None

    # ── 메인 실행 ──────────────────────────────────────────────────
    async def run(self, details_list: list[dict], case_nos: list[str]) -> dict:
        result: dict = {
            "agent": "agent2_naver_asil",
            "status": "success",
            "cases": [],
            "errors": [],
        }

        for d, case_no in zip(details_list, case_nos):
            details = PropertyDetails(
                case_no=case_no,
                complex_name=d.get("complex_name", ""),
                building_no=d.get("building_no", ""),
                unit_no=d.get("unit_no", ""),
                floor=d.get("floor", ""),
                area_supply=float(d.get("area_supply", 0)),
                area_private=float(d.get("area_private", 0)),
                area_land=float(d.get("area_land", 0)),
            )

            case_result: dict = {"case_no": case_no, "naver": None, "asil": None, "error": None}

            try:
                naver = await self.fetch_naver(details, case_no)
                case_result["naver"] = {
                    "complex_name": naver.complex_name,
                    "complex_id": naver.complex_id,
                    "unit_count": naver.unit_count,
                    "layout_info": [
                        {
                            "layout_type": li.layout_type,
                            "rooms": li.rooms,
                            "bathrooms": li.bathrooms,
                            "maintenance_fee": li.maintenance_fee,
                            "active_listings": li.active_listings,
                            "floor_plan_path": li.floor_plan_path,
                        }
                        for li in naver.layout_info
                    ],
                    "listings": [
                        {
                            "seq": li.seq,
                            "listing_no": li.listing_no,
                            "complex_name": li.complex_name,
                            "building": li.building,
                            "area": li.area,
                            "layout_type": li.layout_type,
                            "floor": li.floor,
                            "orientation": li.orientation,
                            "view": li.view,
                            "price": li.price,
                            "reg_date": li.reg_date,
                            "agency": li.agency,
                            "notes": li.notes,
                            "preferred_building": li.preferred_building,
                        }
                        for li in naver.listings
                    ],
                    "price_graph_path": naver.price_graph_path,
                    "jeonse_graph_path": naver.jeonse_graph_path,
                }
            except Exception as e:
                case_result["error"] = f"Naver: {e}"
                result["errors"].append(f"{case_no} Naver: {e}")

            try:
                asil = await self.fetch_asil(details, case_no)
                case_result["asil"] = {
                    "complex_name": asil.complex_name,
                    "target_area_type": asil.target_area_type,
                    "annual_stats": [
                        {
                            "year": s.year,
                            "sale_count": s.sale_count,
                            "jeonse_count": s.jeonse_count,
                            "avg_sale_price": s.avg_sale_price,
                            "avg_jeonse_price": s.avg_jeonse_price,
                        }
                        for s in asil.annual_stats
                    ],
                    "recent_transactions": [
                        {
                            "date": t.date,
                            "floor": t.floor,
                            "area": t.area,
                            "price": t.price,
                            "transaction_type": t.transaction_type,
                        }
                        for t in asil.recent_transactions
                    ],
                }
            except Exception as e:
                case_result["error"] = (case_result["error"] or "") + f" Asil: {e}"
                result["errors"].append(f"{case_no} Asil: {e}")

            result["cases"].append(case_result)

        return result


async def run_agent2(details_list: list[dict], case_nos: list[str]) -> dict:
    async with NaverAsilAgent() as agent:
        return await agent.run(details_list, case_nos)


if __name__ == "__main__":
    sample = [{"complex_name": "테스트아파트", "area_private": 84.99}]
    result = asyncio.run(run_agent2(sample, ["2025-999999"]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
