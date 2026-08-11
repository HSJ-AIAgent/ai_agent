"""
Agent 3: 공간 분석 & 시각 자료 에이전트
- 초등학교/지하철/생활편의 시설 거리 분석
- 단지 지도 + 동/호 표시 캡처
- 호갱노노 평면도 & 세대 배치도 캡처
"""

import asyncio
import json
import re
import logging
import random
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser
from PIL import Image, ImageDraw, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import PropertyDetails, SpatialData, Facility
from config import (
    HEADLESS, BROWSER_TIMEOUT, IMAGES_DIR,
    HOGANGNONO_URL, KAKAO_MAP_URL, KAKAO_API_KEY,
    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX,
)

logger = logging.getLogger("agent3")


class SpatialAgent:
    """공간 분석 & 시각 에이전트"""

    FACILITY_CATEGORIES = {
        "초등학교": ["초등학교", "elementary"],
        "지하철역": ["역", "station", "지하철"],
        "마트/슈퍼": ["마트", "슈퍼", "mart"],
        "공원": ["공원", "park"],
        "병원": ["병원", "의원", "hospital"],
        "버스정류장": ["버스", "정류장", "bus"],
    }

    def __init__(self, images_dir: Path = IMAGES_DIR):
        self.images_dir = images_dir
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox"],
        )
        ctx = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
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

    # ── 좌표 조회 (카카오 지도) ───────────────────────────────────
    async def get_coordinates(self, address: str) -> tuple[float, float]:
        if KAKAO_API_KEY:
            return await self._kakao_geocode(address)
        return await self._map_search_coords(address)

    async def _kakao_geocode(self, address: str) -> tuple[float, float]:
        import aiohttp
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
        params = {"query": address}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as resp:
                    data = await resp.json()
                    docs = data.get("documents", [])
                    if docs:
                        return float(docs[0]["y"]), float(docs[0]["x"])
        except Exception as e:
            logger.warning(f"카카오 API 오류: {e}")
        return 0.0, 0.0

    async def _map_search_coords(self, address: str) -> tuple[float, float]:
        # KAKAO_API_KEY 없으면 대전 유성구 기본 좌표 반환 (Naver Maps 30s 타임아웃 방지)
        if not KAKAO_API_KEY:
            logger.debug("KAKAO_API_KEY 미설정 — 기본 좌표 사용")
            return 36.362, 127.356
        url = f"https://map.naver.com/p/search/{address.replace(' ', '%20')}"
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=10000)
            await asyncio.sleep(2.0)
            coords = re.search(r"(\d+\.\d+),(\d+\.\d+)", self.page.url)
            if coords:
                return float(coords.group(1)), float(coords.group(2))
        except Exception as e:
            logger.warning(f"지도 좌표 조회 실패: {e}")
        return 36.362, 127.356  # 대전 유성구 기본값

    # ── 주변 시설 분석 ────────────────────────────────────────────
    async def analyze_facilities(
        self, address: str, lat: float, lng: float, case_no: str
    ) -> list[Facility]:
        facilities = []

        for category, keywords in self.FACILITY_CATEGORIES.items():
            for kw in keywords[:1]:
                found = await self._search_nearby(
                    address, kw, category, lat, lng
                )
                facilities.extend(found[:2])
                if found:
                    break

        logger.info(f"  주변시설 {len(facilities)}개 수집")
        return facilities

    async def _search_nearby(
        self,
        address: str,
        keyword: str,
        category: str,
        lat: float,
        lng: float,
    ) -> list[Facility]:
        facilities = []

        try:
            search_url = (
                f"https://map.naver.com/p/search/"
                f"{address.replace(' ', '%20')} {keyword}"
            )
            await self.page.goto(search_url, wait_until="domcontentloaded", timeout=10000)
            await asyncio.sleep(2.0)

            items = await self.page.query_selector_all(
                ".place_list li, .search_result li, .list_item"
            )

            for item in items[:3]:
                name = await self._elem_text(item, ".place_name, .name, h3")
                dist_text = await self._elem_text(
                    item, ".distance, .dist, .m_dist"
                )
                dist_m = self._parse_distance(dist_text)

                if name:
                    facilities.append(
                        Facility(
                            name=name,
                            category=category,
                            distance_m=dist_m,
                            walk_time_min=max(1, dist_m // 67),
                        )
                    )

        except Exception as e:
            logger.debug(f"  주변시설 검색 오류 ({keyword}): {e}")

        return facilities

    def _parse_distance(self, text: str) -> int:
        km = re.search(r"([\d.]+)\s*km", text)
        m = re.search(r"(\d+)\s*m", text)
        if km:
            return int(float(km.group(1)) * 1000)
        if m:
            return int(m.group(1))
        return 0

    # ── 지도 캡처 ─────────────────────────────────────────────────
    async def capture_map_overview(
        self, address: str, case_no: str
    ) -> str:
        save_path = self.images_dir / f"{case_no}_map_overview.png"
        try:
            url = f"https://map.naver.com/p/search/{address.replace(' ', '%20')}"
            await self.page.goto(url, wait_until="domcontentloaded", timeout=12000)
            await asyncio.sleep(3.0)  # 지도 타일 로딩 대기

            map_elem = await self.page.query_selector(
                "#map, .map_wrap, .nmap_container, #ct"
            )
            if map_elem:
                await map_elem.screenshot(path=str(save_path))
            else:
                await self.page.screenshot(path=str(save_path))
            logger.info(f"  지도 캡처 완료: {case_no}")
            return str(save_path)
        except Exception as e:
            logger.warning(f"지도 캡처 실패: {e}")
            return ""

    async def capture_unit_marked_map(
        self,
        details: PropertyDetails,
        overview_path: str,
        case_no: str,
    ) -> str:
        save_path = self.images_dir / f"{case_no}_map_unit_marked.png"

        if not overview_path or not Path(overview_path).exists():
            return ""

        try:
            # 카카오맵 로드맵 이미지에 동/호 표시 추가
            img = Image.open(overview_path).convert("RGB")
            draw = ImageDraw.Draw(img)
            w, h = img.size

            # 중앙에 별표(*) 마킹
            cx, cy = w // 2, h // 2
            mark = f"★ {details.building_no} {details.unit_no}"
            font_size = max(14, w // 40)

            try:
                font = ImageFont.truetype("malgun.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

            bbox = draw.textbbox((cx, cy), mark, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]

            # 배경 박스
            pad = 6
            draw.rectangle(
                [cx - tw // 2 - pad, cy - th // 2 - pad,
                 cx + tw // 2 + pad, cy + th // 2 + pad],
                fill=(255, 255, 0, 220),
            )
            draw.text(
                (cx - tw // 2, cy - th // 2),
                mark,
                fill=(255, 0, 0),
                font=font,
            )

            img.save(str(save_path))
            return str(save_path)
        except Exception as e:
            logger.warning(f"단위 표시 지도 생성 실패: {e}")
            return overview_path

    # ── 호갱노노 ──────────────────────────────────────────────────
    async def fetch_hogangnono(
        self, details: PropertyDetails, case_no: str
    ) -> tuple[str, str]:
        floor_plan_path = ""
        unit_map_path = ""

        try:
            search_url = (
                f"{HOGANGNONO_URL}/apt?q={details.complex_name.replace(' ', '+')}"
            )
            await self.page.goto(search_url, timeout=BROWSER_TIMEOUT)
            await self.page.wait_for_load_state("networkidle")
            await self._delay()

            # 첫 번째 결과 클릭
            first = await self.page.query_selector(
                ".search-item:first-child a, .apt-list li:first-child a"
            )
            if first:
                await first.click()
                await self.page.wait_for_load_state("networkidle")
                await self._delay()

            # 해당 평형 타입 탭 선택
            area_int = int(details.area_private)
            for tab in await self.page.query_selector_all(".type-tab, .area-btn"):
                text = (await tab.inner_text()).strip()
                if str(area_int) in text:
                    await tab.click()
                    await asyncio.sleep(1.5)
                    break

            # 평면도 캡처
            fp_save = self.images_dir / f"{case_no}_hogangnono_floorplan.png"
            fp_elem = await self.page.query_selector(
                ".floor-plan img, .plan-img, .apt-plan"
            )
            if fp_elem:
                await fp_elem.screenshot(path=str(fp_save))
                floor_plan_path = str(fp_save)

            # 세대 배치도 캡처
            um_save = self.images_dir / f"{case_no}_hogangnono_unitmap.png"
            um_elem = await self.page.query_selector(
                ".unit-map, .floor-map, .building-map"
            )
            if um_elem:
                await um_elem.screenshot(path=str(um_save))
                unit_map_path = str(um_save)

            logger.info(f"  ✓ 호갱노노 캡처 완료: {details.complex_name}")

        except Exception as e:
            logger.warning(f"  호갱노노 수집 실패: {e}")

        return floor_plan_path, unit_map_path

    # ── 유틸 ──────────────────────────────────────────────────────
    async def _elem_text(self, parent, selector: str) -> str:
        try:
            elem = await parent.query_selector(selector)
            if elem:
                return (await elem.inner_text()).strip()
        except Exception:
            pass
        return ""

    def _build_location_summary(
        self, facilities: list[Facility]
    ) -> str:
        lines = []
        cats = {}
        for f in facilities:
            cats.setdefault(f.category, []).append(f)

        for cat, items in cats.items():
            nearest = min(items, key=lambda x: x.distance_m)
            lines.append(
                f"{cat}: {nearest.name} "
                f"({nearest.distance_m}m, 도보 {nearest.walk_time_min}분)"
            )
        return " / ".join(lines)

    # ── 메인 실행 ──────────────────────────────────────────────────
    async def run(self, details_list: list[dict], case_nos: list[str]) -> dict:
        result: dict = {
            "agent": "agent3_spatial",
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

            address = d.get("address", "")
            case_result: dict = {
                "case_no": case_no,
                "spatial": None,
                "error": None,
            }

            try:
                lat, lng = await self.get_coordinates(address)

                facilities = await self.analyze_facilities(
                    address, lat, lng, case_no
                )

                map_overview = await self.capture_map_overview(address, case_no)
                map_unit = await self.capture_unit_marked_map(
                    details, map_overview, case_no
                )

                hgnn_floor, hgnn_unit = await self.fetch_hogangnono(
                    details, case_no
                )

                location_summary = self._build_location_summary(facilities)

                case_result["spatial"] = {
                    "lat": lat,
                    "lng": lng,
                    "location_summary": location_summary,
                    "facilities": [
                        {
                            "name": f.name,
                            "category": f.category,
                            "distance_m": f.distance_m,
                            "walk_time_min": f.walk_time_min,
                        }
                        for f in facilities
                    ],
                    "map_overview_path": map_overview,
                    "map_unit_path": map_unit,
                    "hogangnono_floor_plan_path": hgnn_floor,
                    "hogangnono_unit_map_path": hgnn_unit,
                }

            except Exception as e:
                case_result["error"] = str(e)
                result["errors"].append(f"{case_no}: {e}")

            result["cases"].append(case_result)

        return result


async def run_agent3(details_list: list[dict], case_nos: list[str]) -> dict:
    async with SpatialAgent() as agent:
        return await agent.run(details_list, case_nos)


if __name__ == "__main__":
    sample = [{
        "complex_name": "테스트아파트",
        "address": "대전 유성구 테스트동 1",
        "building_no": "101동",
        "unit_no": "102호",
        "area_private": 84.0,
    }]
    result = asyncio.run(run_agent3(sample, ["2025-999999"]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
