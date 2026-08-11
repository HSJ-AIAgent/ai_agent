"""
Agent 5: 엑셀 보고서 생성 에이전트
- 템플릿(쿡희 24-5499 손품1.xlsx) 구조에 맞춰 데이터 및 이미지 삽입
- 섹션: 권리분석/입지분석/평형정보/매물정리/실거래가/거래량통계/가격요인분석
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import (
    Alignment, Border, Font, PatternFill, Side
)
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import (
    AuctionCase, PropertyDetails, NaverData, AsilData,
    SpatialData, ListingItem, PriceAnalysis
)
from config import OUTPUT_DIR, TEMPLATE_PATH

logger = logging.getLogger("agent5")

# 스타일 상수
HEADER_FILL = PatternFill("solid", fgColor="FFE699")
SECTION_FILL = PatternFill("solid", fgColor="D9E1F2")
TABLE_HEADER_FILL = PatternFill("solid", fgColor="BDD7EE")
THIN = Side(style="thin")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
BOLD = Font(bold=True)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)


class ExcelReportBuilder:
    """엑셀 보고서 생성기"""

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.wb: Optional[Workbook] = None
        self.ws_main = None      # 메인 시트
        self.ws_listings = None  # Sheet4 (네이버 전체 매물)
        self.ws_markup = None    # 일별매물스크랩
        self.ws_summary = None   # 매물정리
        self.ws_price = None     # 1차기준가

    def _new_wb(self):
        self.wb = Workbook()
        self.ws_main = self.wb.active
        self.ws_main.title = "메인"
        self.ws_listings = self.wb.create_sheet("Sheet4")
        self.ws_markup = self.wb.create_sheet("일별매물스크랩")
        self.ws_summary = self.wb.create_sheet("매물정리")
        self.ws_price = self.wb.create_sheet("1차기준가")

        # 메인 시트 열 너비 설정
        col_widths = {1: 14, 2: 12, 3: 20, 4: 10, 5: 10, 6: 10, 7: 14, 8: 12, 9: 14}
        for col, w in col_widths.items():
            self.ws_main.column_dimensions[get_column_letter(col)].width = w

    def _cell(self, ws, row, col, value=None, **style):
        c = ws.cell(row=row, column=col, value=value)
        if style.get("bold"):
            c.font = Font(bold=True, size=style.get("font_size", 11))
        if style.get("fill"):
            c.fill = style["fill"]
        if style.get("align", "left") == "center":
            c.alignment = CENTER
        else:
            c.alignment = LEFT
        if style.get("border"):
            c.border = BORDER
        return c

    def _section_header(self, ws, row, text, cols=11):
        c = ws.cell(row=row, column=1, value=text)
        c.font = Font(bold=True, size=13)
        c.fill = SECTION_FILL
        c.alignment = LEFT
        if cols > 1:
            ws.merge_cells(
                start_row=row, start_column=1,
                end_row=row, end_column=cols
            )
        ws.row_dimensions[row].height = 22
        return row + 1

    def _table_header(self, ws, row, headers: list[str], start_col=1):
        for j, h in enumerate(headers, start=start_col):
            c = ws.cell(row=row, column=j, value=h)
            c.font = BOLD
            c.fill = TABLE_HEADER_FILL
            c.alignment = CENTER
            c.border = BORDER
        ws.row_dimensions[row].height = 18
        return row + 1

    def _insert_image(self, ws, img_path: str, anchor: str, max_w=480, max_h=320):
        p = Path(img_path)
        if not p.exists():
            logger.warning(f"이미지 없음: {img_path}")
            return False
        try:
            img = XLImage(str(p))
            img.width = min(img.width, max_w)
            img.height = min(img.height, max_h)
            ws.add_image(img, anchor)
            return True
        except Exception as e:
            logger.warning(f"이미지 삽입 실패 ({img_path}): {e}")
            return False

    # ── 섹션 1: 권리분석 (rows 1-144) ────────────────────────────
    def _write_section1(self, row: int, case: AuctionCase, details: PropertyDetails, assets: dict) -> int:
        ws = self.ws_main

        # 헤더
        ws.cell(row=row, column=1, value="1. 권리분석:").font = Font(bold=True, size=13)
        ws.cell(row=row, column=3, value=case.case_no)
        ws.row_dimensions[row].height = 22
        row += 2

        # 기본 정보 테이블
        info_rows = [
            ("법원", case.court, "단지명", details.complex_name),
            ("소재지", case.address, "동호수", f"{details.building_no} {details.unit_no}"),
            ("물건종류", "아파트", "층", details.floor),
            ("감정가", f"{case.appraisal_value:,}원", "공급면적", f"{details.area_supply}㎡"),
            ("최저입찰가", f"{case.min_bid:,}원", "전용면적", f"{details.area_private}㎡"),
            ("입찰일", case.bid_date, "대지권", f"{details.area_land}㎡"),
            ("상태", case.status, "", ""),
        ]
        headers = ["항목", "내용", "항목", "내용"]
        row = self._table_header(ws, row, headers)

        for label1, val1, label2, val2 in info_rows:
            ws.cell(row=row, column=1, value=label1).border = BORDER
            ws.cell(row=row, column=2, value=val1).border = BORDER
            ws.cell(row=row, column=3, value=label2).border = BORDER
            ws.cell(row=row, column=4, value=val2).border = BORDER
            ws.row_dimensions[row].height = 16
            row += 1
        row += 1

        # 권리 관계 텍스트
        if details.registry_info:
            ws.cell(row=row, column=1, value="【권리관계】").font = BOLD
            row += 1
            ws.cell(row=row, column=1, value=details.registry_info).alignment = LEFT
            ws.row_dimensions[row].height = 60
            row += 2

        if details.tenant_info:
            ws.cell(row=row, column=1, value="【임차인/점유자】").font = BOLD
            row += 1
            ws.cell(row=row, column=1, value=details.tenant_info).alignment = LEFT
            ws.row_dimensions[row].height = 60
            row += 2

        # 1-2 매각물건명세서
        ws.cell(row=row, column=1, value="1-2 매각물건명세서").font = Font(bold=True)
        row += 2
        doc_path = assets.get("docs", {}).get("매각물건명세서", "")
        if doc_path:
            self._insert_image(ws, doc_path, f"A{row}", max_h=400)
            row += 22
        else:
            ws.cell(row=row, column=1, value="(문서 없음)").font = Font(italic=True, color="888888")
            row += 2

        # 1-3 세대열람
        ws.cell(row=row, column=1, value="1-3 세대열람").font = Font(bold=True)
        row += 2
        doc_path = assets.get("docs", {}).get("세대열람", "")
        if doc_path:
            self._insert_image(ws, doc_path, f"A{row}", max_h=300)
            row += 18
        else:
            ws.cell(row=row, column=1, value="(문서 없음)").font = Font(italic=True, color="888888")
            row += 2

        # 1-4 현황조사서
        ws.cell(row=row, column=1, value="1-4 현황조사서").font = Font(bold=True)
        row += 2
        doc_path = assets.get("docs", {}).get("현황조사서", "")
        if doc_path:
            self._insert_image(ws, doc_path, f"A{row}", max_h=300)
            row += 18
        else:
            ws.cell(row=row, column=1, value="(문서 없음)").font = Font(italic=True, color="888888")
            row += 2

        # 권리 분석 요약
        analysis_note = ""
        if "선순위" in (details.tenant_info or ""):
            analysis_note = (
                "말소기준권리보다 전입날짜가 빠른 전입세대가 있으나 "
                "현황조사서상 채무자로 특정되어 있으므로 입찰가능"
            )
        ws.cell(row=row, column=1, value=analysis_note).alignment = LEFT
        ws.row_dimensions[row].height = 40
        row += 3

        return row

    # ── 섹션 2: 입지분석 (rows 145~) ─────────────────────────────
    def _write_section2(self, row: int, spatial: Optional[SpatialData], assets: dict) -> int:
        ws = self.ws_main
        ws.cell(row=row, column=1, value="2. 입지분석").font = Font(bold=True, size=13)
        ws.cell(row=row, column=3, value=spatial.location_summary if spatial else "")
        row += 2

        if spatial:
            # 시설 거리 표
            row = self._table_header(ws, row, ["카테고리", "시설명", "거리(m)", "도보(분)"])
            for f in (spatial.facilities or []):
                ws.cell(row=row, column=1, value=f.category).border = BORDER
                ws.cell(row=row, column=2, value=f.name).border = BORDER
                ws.cell(row=row, column=3, value=f.distance_m).border = BORDER
                ws.cell(row=row, column=4, value=f.walk_time_min).border = BORDER
                row += 1
            row += 1

            # 입지 메모
            if spatial.location_summary:
                ws.cell(row=row, column=1, value=spatial.location_summary).alignment = LEFT
                ws.row_dimensions[row].height = 50
                row += 2

        # 지도 이미지 (전체 지도)
        map_path = (assets.get("images", {}) or {}).get("map_overview_path")
        if map_path:
            ws.cell(row=row, column=1, value="◆ 단지 전체 지도").font = BOLD
            row += 1
            self._insert_image(ws, map_path, f"A{row}", max_w=520, max_h=340)
            row += 20

        # 단위 표시 지도
        unit_map = (assets.get("images", {}) or {}).get("map_unit_path")
        if unit_map:
            ws.cell(row=row, column=1, value="◆ 경매 호수 위치").font = BOLD
            row += 1
            self._insert_image(ws, unit_map, f"A{row}", max_w=520, max_h=340)
            row += 20

        return row

    # ── 섹션 3: 평형/타입별 정보 ──────────────────────────────────
    def _write_section3(self, row: int, naver: Optional[NaverData], assets: dict) -> int:
        ws = self.ws_main
        ws.cell(row=row, column=1, value="평형, 타입별 동호수 확인").font = Font(bold=True, size=12)
        row += 2

        if naver:
            for li in (naver.layout_info or []):
                ws.cell(row=row, column=1, value=f"▶ {li.layout_type} 타입").font = BOLD
                row += 1

                info = [
                    ("방 수", f"{li.rooms}개"),
                    ("욕실", f"{li.bathrooms}개"),
                    ("관리비", f"{li.maintenance_fee:,}원" if li.maintenance_fee else "-"),
                    ("매물 수", f"{li.active_listings}건"),
                ]
                for label, val in info:
                    ws.cell(row=row, column=2, value=label)
                    ws.cell(row=row, column=3, value=val)
                    row += 1

                # 평면도
                if li.floor_plan_path:
                    self._insert_image(ws, li.floor_plan_path, f"E{row-4}", max_w=200, max_h=160)

                row += 2

            # 호갱노노 평면도
            hgnn_plan = (assets.get("images", {}) or {}).get("hogangnono_floor_plan_path")
            if hgnn_plan:
                ws.cell(row=row, column=1, value="◆ 호갱노노 평면도").font = BOLD
                row += 1
                self._insert_image(ws, hgnn_plan, f"A{row}", max_w=480, max_h=300)
                row += 18

            # 호갱노노 세대 배치도
            hgnn_unit = (assets.get("images", {}) or {}).get("hogangnono_unit_map_path")
            if hgnn_unit:
                ws.cell(row=row, column=1, value="◆ 호갱노노 세대 배치도").font = BOLD
                row += 1
                self._insert_image(ws, hgnn_unit, f"A{row}", max_w=480, max_h=300)
                row += 18

            # 단지 정보 요약
            ws.cell(row=row, column=1, value="단지정보").font = Font(bold=True)
            row += 1
            ws.cell(row=row, column=2, value="총 세대수")
            ws.cell(row=row, column=3, value=f"{naver.unit_count:,}세대" if naver.unit_count else "-")
            row += 2

        return row

    # ── 섹션 4: 매물 정리 ─────────────────────────────────────────
    def _write_section4(self, row: int, naver: Optional[NaverData], date_str: str) -> int:
        ws = self.ws_main
        ws.cell(row=row, column=1, value="매물 수 정리").font = Font(bold=True, size=12)
        row += 1

        # 날짜/매매/전세/변동 요약
        listing_count = len(naver.listings) if naver else 0
        jeonse_count = sum(1 for li in (naver.listings if naver else []) if "전세" in li.notes)
        sale_count = listing_count - jeonse_count

        headers = ["날짜", "매매", "전세", "변동사항", "", "매물리스트"]
        for j, h in enumerate(headers, 1):
            if h:
                ws.cell(row=row, column=j, value=h).font = BOLD
        row += 1
        ws.cell(row=row, column=1, value=date_str)
        ws.cell(row=row, column=2, value=sale_count)
        ws.cell(row=row, column=3, value=jeonse_count)
        row += 2

        # 5년 가격 추이 그래프
        ws.cell(row=row, column=1, value="실거래가").font = Font(bold=True, size=12)
        row += 1

        return row

    # ── 섹션 5: 실거래가 & 5년 그래프 ──────────────────────────────
    def _write_section5(self, row: int, naver: Optional[NaverData], asil: Optional[AsilData], assets: dict) -> int:
        ws = self.ws_main

        # 5년 가격 그래프 (매매)
        graph_매매 = (assets.get("images", {}) or {}).get("price_graph_매매")
        if graph_매매:
            ws.cell(row=row, column=1, value="◆ 5년 매매 실거래 추이").font = BOLD
            row += 1
            self._insert_image(ws, graph_매매, f"A{row}", max_w=540, max_h=280)
            row += 17

        # 5년 전세 그래프
        graph_전세 = (assets.get("images", {}) or {}).get("price_graph_전세")
        if graph_전세:
            ws.cell(row=row, column=1, value="◆ 5년 전세 실거래 추이").font = BOLD
            row += 1
            self._insert_image(ws, graph_전세, f"A{row}", max_w=540, max_h=280)
            row += 17

        if asil:
            area_label = asil.target_area_type or "해당평형"
            ws.cell(row=row, column=11, value=f"{area_label}").font = BOLD
            row += 1
            ws.cell(row=row, column=11, value="실거래 내역").font = BOLD
            row += 2

        return row

    # ── 섹션 6: 거래량 연도별 통계 (아실) ────────────────────────
    def _write_section6(self, row: int, asil: Optional[AsilData], details: Optional[PropertyDetails]) -> int:
        ws = self.ws_main
        ws.cell(row=row, column=1, value="거래량 년도별 통계 (아실)").font = Font(bold=True, size=12)
        area_label = (
            f"{int(details.area_private)}평형" if details and details.area_private else "해당평형"
        )
        ws.cell(row=row, column=4, value=area_label)
        row += 2

        if asil and asil.annual_stats:
            headers = ["연도", "매매", "전세", "평균매매가(만원)", "평균전세가(만원)"]
            row = self._table_header(ws, row, headers)
            for s in asil.annual_stats:
                ws.cell(row=row, column=1, value=s.year).border = BORDER
                ws.cell(row=row, column=2, value=s.sale_count).border = BORDER
                ws.cell(row=row, column=3, value=s.jeonse_count).border = BORDER
                ws.cell(row=row, column=4, value=s.avg_sale_price).border = BORDER
                ws.cell(row=row, column=5, value=s.avg_jeonse_price).border = BORDER
                row += 1
            row += 2

            # 최근 3년 실거래 내역
            if asil.recent_transactions:
                ws.cell(row=row, column=1, value="최근 실거래 내역").font = BOLD
                row += 1
                headers2 = ["거래일", "층", "전용면적(㎡)", "거래가(만원)", "거래종류"]
                row = self._table_header(ws, row, headers2)
                for t in asil.recent_transactions[:20]:
                    ws.cell(row=row, column=1, value=t.date).border = BORDER
                    ws.cell(row=row, column=2, value=t.floor).border = BORDER
                    ws.cell(row=row, column=3, value=t.area).border = BORDER
                    ws.cell(row=row, column=4, value=t.price).border = BORDER
                    ws.cell(row=row, column=5, value=t.transaction_type).border = BORDER
                    row += 1
                row += 2
        else:
            ws.cell(row=row, column=1, value="(아실 데이터 없음)").font = Font(italic=True)
            row += 3

        return row

    # ── 섹션 7: 가격요인별 매물 정리 ─────────────────────────────
    def _write_section7(self, row: int, case: AuctionCase, details: Optional[PropertyDetails], analysis: Optional[PriceAnalysis]) -> int:
        ws = self.ws_main
        ws.cell(row=row, column=1, value="가격요인별 매물 정리").font = Font(bold=True, size=12)
        row += 2

        # 경매 매물 정보
        ws.cell(row=row, column=1, value="경매매물").font = BOLD
        row += 1
        headers = ["동", "층", "향", "조망", "선호동"]
        row = self._table_header(ws, row, headers)
        if details:
            bldg = details.building_no.replace("동", "")
            ws.cell(row=row, column=1, value=bldg).border = BORDER
            ws.cell(row=row, column=2, value=details.floor).border = BORDER
            ws.cell(row=row, column=3, value="").border = BORDER
            ws.cell(row=row, column=4, value="X").border = BORDER
            ws.cell(row=row, column=5, value="X").border = BORDER
            row += 2

        LISTING_HEADERS = ["순번", "동", "타입", "층", "방향", "조망", "선호동", "가격(만원)", "특이사항"]

        if analysis:
            # 가장 유사한 조건의 매물
            ws.cell(row=row, column=1, value="가장 유사한 조건의 매물").font = BOLD
            row += 1
            row = self._table_header(ws, row, LISTING_HEADERS)
            for li in (analysis.comparable_listings or [])[:5]:
                self._write_listing_row(ws, row, li)
                row += 1
            row += 2

            # 층별 가격 차이
            ws.cell(row=row, column=1, value="층별 가격 차이 비교").font = BOLD
            if analysis.floor_adjust:
                ws.cell(row=row, column=3, value=f"1단계 {analysis.floor_adjust:+,}만원")
            row += 1
            row = self._table_header(ws, row, LISTING_HEADERS)
            for li in (analysis.floor_comparison or [])[:5]:
                self._write_listing_row(ws, row, li)
                row += 1
            row += 2

            # 향별 가격 차이
            ws.cell(row=row, column=1, value="향별 가격 차이 비교").font = BOLD
            if analysis.orientation_adjust:
                ws.cell(row=row, column=3, value=f"정남↔남동 {analysis.orientation_adjust:+,}만원")
            row += 1
            row = self._table_header(ws, row, LISTING_HEADERS)
            for li in (analysis.orientation_comparison or [])[:5]:
                self._write_listing_row(ws, row, li)
                row += 1
            row += 2

            # 선호동별 가격 차이
            ws.cell(row=row, column=1, value="선호동별 가격 차이 비교").font = BOLD
            row += 1
            row = self._table_header(ws, row, LISTING_HEADERS)
            for li in (analysis.preferred_comparison or [])[:5]:
                self._write_listing_row(ws, row, li)
                row += 1
            row += 3

            # 판단기준 & 기준가
            ws.cell(row=row, column=1, value="판단기준").font = Font(bold=True, size=12)
            row += 1
            headers_judge = ["층", "금액", "향", "금액", "조망", "금액", "선호동", "금액"]
            row = self._table_header(ws, row, headers_judge)

            factors = [
                ("로얄층", analysis.floor_adjust, "정남", analysis.orientation_adjust,
                 "뻥뷰", analysis.view_adjust, "O", analysis.preferred_building_adjust),
                ("저층", 0, "남동", 0, "X", 0, "X", 0),
                ("탑층", 0, "", 0, "", 0, "", 0),
                ("1층", 0, "", 0, "", 0, "", 0),
            ]
            for vals in factors:
                for j, v in enumerate(vals, 1):
                    ws.cell(row=row, column=j, value=v).border = BORDER
                row += 1
            row += 2

            ws.cell(row=row, column=1, value="가성비 1차 기준가:").font = Font(bold=True, size=12)
            final = analysis.final_price
            ws.cell(row=row, column=3, value=f"{final:,}만원" if final else "분석 필요")
            row += 2

            if analysis.analysis_notes:
                ws.cell(row=row, column=1, value=f"임장시 확인할 것 // {analysis.analysis_notes}")
                row += 2

        return row

    def _write_listing_row(self, ws, row: int, li: ListingItem):
        ws.cell(row=row, column=1, value=li.seq).border = BORDER
        ws.cell(row=row, column=2, value=li.building).border = BORDER
        ws.cell(row=row, column=3, value=li.layout_type).border = BORDER
        ws.cell(row=row, column=4, value=li.floor).border = BORDER
        ws.cell(row=row, column=5, value=li.orientation).border = BORDER
        ws.cell(row=row, column=6, value=li.view).border = BORDER
        ws.cell(row=row, column=7, value=li.preferred_building).border = BORDER
        ws.cell(row=row, column=8, value=li.price).border = BORDER
        ws.cell(row=row, column=9, value=li.notes).border = BORDER

    # ── Sheet4: 전체 매물 리스트 ──────────────────────────────────
    def _write_sheet4(self, naver: Optional[NaverData]):
        ws = self.ws_listings
        headers = [
            "순번", "매물번호", "단지명", "동", "면적(㎡)", "타입",
            "층", "향구", "조망", "방향", "가격(만원)", "등록일", "중개사명", "특이사항"
        ]
        for j, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=j, value=h)
            c.font = BOLD
            c.fill = TABLE_HEADER_FILL
            c.border = BORDER
            c.alignment = CENTER

        if not naver:
            return

        for i, li in enumerate(naver.listings, 1):
            ws.cell(row=i + 1, column=1, value=li.seq)
            ws.cell(row=i + 1, column=2, value=li.listing_no)
            ws.cell(row=i + 1, column=3, value=li.complex_name or naver.complex_name)
            ws.cell(row=i + 1, column=4, value=li.building)
            ws.cell(row=i + 1, column=5, value=li.area)
            ws.cell(row=i + 1, column=6, value=li.layout_type)
            ws.cell(row=i + 1, column=7, value=li.floor)
            ws.cell(row=i + 1, column=8, value=li.orientation)
            ws.cell(row=i + 1, column=9, value=li.view)
            ws.cell(row=i + 1, column=10, value=li.direction)
            ws.cell(row=i + 1, column=11, value=li.price)
            ws.cell(row=i + 1, column=12, value=li.reg_date)
            ws.cell(row=i + 1, column=13, value=li.agency)
            ws.cell(row=i + 1, column=14, value=li.notes)

    # ── 매물정리 시트 (유사조건 비교) ────────────────────────────
    def _write_sheet_summary(self, analysis: Optional[PriceAnalysis]):
        ws = self.ws_summary
        if not analysis:
            return
        headers = ["순번", "동", "타입", "층", "향구", "조망", "가격(만원)", "특이사항"]
        for j, h in enumerate(headers, 1):
            ws.cell(row=1, column=j, value=h).font = BOLD
        for i, li in enumerate(analysis.comparable_listings or [], 2):
            ws.cell(row=i, column=1, value=li.seq)
            ws.cell(row=i, column=2, value=li.building)
            ws.cell(row=i, column=3, value=li.layout_type)
            ws.cell(row=i, column=4, value=li.floor)
            ws.cell(row=i, column=5, value=li.orientation)
            ws.cell(row=i, column=6, value=li.view)
            ws.cell(row=i, column=7, value=li.price)
            ws.cell(row=i, column=8, value=li.notes)

    # ── 1차기준가 시트 ────────────────────────────────────────────
    def _write_sheet_price(self, analysis: Optional[PriceAnalysis]):
        ws = self.ws_price
        if not analysis:
            return
        headers = ["순번", "동", "층", "방향", "호환여부", "가격(만원)", "희망기준가"]
        for j, h in enumerate(headers, 1):
            ws.cell(row=1, column=j, value=h).font = BOLD
        for i, li in enumerate(analysis.comparable_listings or [], 2):
            ws.cell(row=i, column=1, value=li.seq)
            ws.cell(row=i, column=2, value=li.building)
            ws.cell(row=i, column=3, value=li.floor)
            ws.cell(row=i, column=4, value=li.orientation)
            ws.cell(row=i, column=5, value="X")
            ws.cell(row=i, column=6, value=li.price)

        last = len(analysis.comparable_listings or []) + 3
        ws.cell(row=last, column=7, value="가성비 기준가")
        ws.cell(row=last + 1, column=7, value=analysis.final_price)

    # ── 일별매물스크랩 시트 ───────────────────────────────────────
    def _write_sheet_markup(self, date_str: str, naver: Optional[NaverData]):
        ws = self.ws_markup
        ws.cell(row=1, column=1, value=date_str)

    # ── 메인 빌더 ─────────────────────────────────────────────────
    def build(
        self,
        case: AuctionCase,
        details: Optional[PropertyDetails],
        naver: Optional[NaverData],
        asil: Optional[AsilData],
        spatial: Optional[SpatialData],
        analysis: Optional[PriceAnalysis],
        assets: dict,
    ) -> str:
        self._new_wb()
        ws = self.ws_main
        today = datetime.now().strftime("%y%m%d")

        row = 1
        row = self._write_section1(row, case, details or PropertyDetails(
            case_no=case.case_no, complex_name="", building_no="",
            unit_no="", floor="", area_supply=0, area_private=0, area_land=0,
        ), assets)

        row = self._write_section2(row, spatial, assets)
        row = self._write_section3(row, naver, assets)
        row = self._write_section4(row, naver, today)
        row = self._write_section5(row, naver, asil, assets)
        row = self._write_section6(row, asil, details)
        row = self._write_section7(row, case, details, analysis)

        self._write_sheet4(naver)
        self._write_sheet_summary(analysis)
        self._write_sheet_price(analysis)
        self._write_sheet_markup(today, naver)

        safe_no = case.case_no.replace("-", "_")
        out_path = self.output_dir / f"{safe_no}_경매분석_{today}.xlsx"
        self.wb.save(str(out_path))
        logger.info(f"✓ 보고서 저장: {out_path}")
        return str(out_path)


def run_agent5(pipeline_data: dict) -> dict:
    result: dict = {
        "agent": "agent5_excel",
        "status": "success",
        "reports": [],
        "errors": [],
    }

    builder = ExcelReportBuilder()
    a1_cases = {c["case_no"]: c for c in pipeline_data.get("agent1", {}).get("cases", [])}
    a2_cases = {c["case_no"]: c for c in pipeline_data.get("agent2", {}).get("cases", [])}
    a3_cases = {c["case_no"]: c for c in pipeline_data.get("agent3", {}).get("cases", [])}
    a4_cases = {c["case_no"]: c for c in pipeline_data.get("agent4", {}).get("cases", [])}

    for case_no, a1 in a1_cases.items():
        try:
            # AuctionCase 복원
            case = AuctionCase(
                case_no=case_no,
                court=a1.get("court", ""),
                address=a1.get("address", ""),
                detail_url=a1.get("detail_url", ""),
                min_bid=a1.get("min_bid", 0),
                appraisal_value=a1.get("appraisal_value", 0),
                bid_date=a1.get("bid_date", ""),
                status=a1.get("status", ""),
            )

            # PropertyDetails 복원
            d = a1.get("details") or {}
            details = PropertyDetails(
                case_no=case_no,
                complex_name=d.get("complex_name", ""),
                building_no=d.get("building_no", ""),
                unit_no=d.get("unit_no", ""),
                floor=d.get("floor", ""),
                area_supply=float(d.get("area_supply", 0)),
                area_private=float(d.get("area_private", 0)),
                area_land=float(d.get("area_land", 0)),
                land_status=d.get("land_status", ""),
                building_status=d.get("building_status", ""),
                tenant_info=d.get("tenant_info", ""),
                registry_info=d.get("registry_info", ""),
                doc_paths=d.get("doc_paths", {}),
            ) if d else None

            # NaverData 복원
            a2 = a2_cases.get(case_no, {})
            nv = a2.get("naver") or {}
            naver = None
            if nv:
                from models import LayoutInfo, ListingItem
                naver = NaverData(
                    complex_name=nv.get("complex_name", ""),
                    complex_id=nv.get("complex_id", ""),
                    unit_count=nv.get("unit_count", 0),
                    layout_info=[
                        LayoutInfo(
                            layout_type=li["layout_type"],
                            rooms=li.get("rooms", 0),
                            bathrooms=li.get("bathrooms", 0),
                            maintenance_fee=li.get("maintenance_fee", 0),
                            active_listings=li.get("active_listings", 0),
                            floor_plan_path=li.get("floor_plan_path", ""),
                        )
                        for li in nv.get("layout_info", [])
                    ],
                    listings=[
                        ListingItem(
                            seq=li["seq"],
                            listing_no=li.get("listing_no", ""),
                            complex_name=li.get("complex_name", ""),
                            building=li.get("building", ""),
                            area=float(li.get("area", 0)),
                            layout_type=li.get("layout_type", ""),
                            floor=li.get("floor", ""),
                            orientation=li.get("orientation", ""),
                            view=li.get("view", ""),
                            price=li.get("price", 0),
                            reg_date=li.get("reg_date", ""),
                            agency=li.get("agency", ""),
                            notes=li.get("notes", ""),
                            preferred_building=li.get("preferred_building", ""),
                        )
                        for li in nv.get("listings", [])
                    ],
                    price_graph_path=nv.get("price_graph_path", ""),
                    jeonse_graph_path=nv.get("jeonse_graph_path", ""),
                )

            # AsilData 복원
            av = a2.get("asil") or {}
            asil = None
            if av:
                from models import TransactionStat, RecentTransaction
                asil = AsilData(
                    complex_name=av.get("complex_name", ""),
                    target_area_type=av.get("target_area_type", ""),
                    annual_stats=[
                        TransactionStat(
                            year=s["year"],
                            sale_count=s.get("sale_count", 0),
                            jeonse_count=s.get("jeonse_count", 0),
                            avg_sale_price=s.get("avg_sale_price", 0),
                            avg_jeonse_price=s.get("avg_jeonse_price", 0),
                        )
                        for s in av.get("annual_stats", [])
                    ],
                    recent_transactions=[
                        RecentTransaction(
                            date=t["date"],
                            floor=t.get("floor", ""),
                            area=float(t.get("area", 0)),
                            price=t.get("price", 0),
                            transaction_type=t.get("transaction_type", "매매"),
                        )
                        for t in av.get("recent_transactions", [])
                    ],
                )

            # SpatialData 복원
            a3 = a3_cases.get(case_no, {})
            sp = a3.get("spatial") or {}
            spatial = None
            if sp:
                from models import Facility
                spatial = SpatialData(
                    case_no=case_no,
                    address=a1.get("address", ""),
                    lat=sp.get("lat", 0.0),
                    lng=sp.get("lng", 0.0),
                    location_summary=sp.get("location_summary", ""),
                    facilities=[
                        Facility(
                            name=f["name"],
                            category=f["category"],
                            distance_m=f.get("distance_m", 0),
                            walk_time_min=f.get("walk_time_min", 0),
                        )
                        for f in sp.get("facilities", [])
                    ],
                    map_overview_path=sp.get("map_overview_path", ""),
                    map_unit_path=sp.get("map_unit_path", ""),
                    hogangnono_floor_plan_path=sp.get("hogangnono_floor_plan_path", ""),
                    hogangnono_unit_map_path=sp.get("hogangnono_unit_map_path", ""),
                )

            # PriceAnalysis 자동 생성
            analysis = _build_price_analysis(naver, details)

            # 자산 인덱스
            a4 = a4_cases.get(case_no, {})
            assets = {
                "docs": a4.get("docs", {}),
                "images": a4.get("images", {}),
            }
            # spatial 이미지 추가
            if spatial:
                assets["images"].update({
                    "map_overview_path": spatial.map_overview_path,
                    "map_unit_path": spatial.map_unit_path,
                    "hogangnono_floor_plan_path": spatial.hogangnono_floor_plan_path,
                    "hogangnono_unit_map_path": spatial.hogangnono_unit_map_path,
                })
            if naver:
                if naver.price_graph_path:
                    assets["images"]["price_graph_매매"] = naver.price_graph_path
                if naver.jeonse_graph_path:
                    assets["images"]["price_graph_전세"] = naver.jeonse_graph_path
            if details and details.doc_paths:
                assets["docs"].update(details.doc_paths)

            out_path = builder.build(case, details, naver, asil, spatial, analysis, assets)
            result["reports"].append({"case_no": case_no, "path": out_path})

        except Exception as e:
            result["errors"].append(f"{case_no}: {e}")
            logger.error(f"Agent5 오류 ({case_no}): {e}", exc_info=True)

    return result


def _build_price_analysis(
    naver: Optional[NaverData], details: Optional[PropertyDetails]
) -> Optional[PriceAnalysis]:
    """네이버 매물 데이터로 가격 요인 분석 자동 생성"""
    if not naver or not naver.listings:
        return None

    listings = naver.listings

    # 기준가 = 중간값 가격
    prices = sorted([li.price for li in listings if li.price > 0])
    if not prices:
        return None
    base = prices[len(prices) // 2]

    # 층별 비교
    low_floor = [li for li in listings if "저" in li.floor or "1/" in li.floor]
    high_floor = [li for li in listings if "중" in li.floor or "고" in li.floor]
    floor_adj = 0
    if low_floor and high_floor:
        avg_low = sum(li.price for li in low_floor) / len(low_floor)
        avg_high = sum(li.price for li in high_floor) / len(high_floor)
        floor_adj = int((avg_high - avg_low) / 100) * 100

    # 향별 비교
    south = [li for li in listings if "정남" in li.orientation]
    south_east = [li for li in listings if "남동" in li.orientation]
    orient_adj = 0
    if south and south_east:
        avg_s = sum(li.price for li in south) / len(south)
        avg_se = sum(li.price for li in south_east) / len(south_east)
        orient_adj = int((avg_s - avg_se) / 100) * 100

    # 선호동 비교
    preferred = [li for li in listings if li.preferred_building == "O"]
    non_preferred = [li for li in listings if li.preferred_building == "X"]
    preferred_adj = 0
    if preferred and non_preferred:
        avg_p = sum(li.price for li in preferred) / len(preferred)
        avg_np = sum(li.price for li in non_preferred) / len(non_preferred)
        preferred_adj = int((avg_p - avg_np) / 100) * 100

    # 경매 대상 조건 적용 조정
    target_floor = details.floor if details else ""
    floor_factor = 0
    if "저" in target_floor or "1층" in target_floor:
        floor_factor = -floor_adj
    elif "중" in target_floor:
        floor_factor = 0
    else:
        floor_factor = floor_adj // 2

    final = base + floor_factor + (orient_adj if orient_adj < 0 else -orient_adj // 2)

    return PriceAnalysis(
        base_price=base,
        floor_adjust=floor_adj,
        orientation_adjust=orient_adj,
        view_adjust=0,
        preferred_building_adjust=preferred_adj,
        final_price=max(0, final),
        comparable_listings=listings[:10],
        floor_comparison=(low_floor + high_floor)[:6],
        orientation_comparison=(south + south_east)[:6],
        preferred_comparison=(preferred + non_preferred)[:6],
    )


if __name__ == "__main__":
    print("Agent5 단독 실행 — orchestrator를 통해 사용하세요.")
