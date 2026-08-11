"""
경매 분석 멀티에이전트 파이프라인 오케스트레이터
사용법: python orchestrator.py "대전 유성구 아파트 분석해줘"
"""

import asyncio
import io
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

# Windows CP949 인코딩 문제 해결 - stdout을 UTF-8로 강제 설정
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from config import LOGS_DIR, OUTPUT_DIR
from models import SearchCriteria

# 에이전트 임포트
from agents.agent1_tankauction import run_agent1
from agents.agent2_naver_asil import run_agent2
from agents.agent3_spatial import run_agent3
from agents.agent4_assets import run_agent4
from agents.agent5_excel import run_agent5

# ── 로깅 설정 ─────────────────────────────────────────────────────
def setup_logging(run_id: str) -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"pipeline_{run_id}.log"

    fmt = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.stream = sys.stdout
    handlers = [
        stream_handler,
        logging.FileHandler(log_file, encoding="utf-8"),
    ]
    logging.basicConfig(level=logging.INFO, format=fmt, handlers=handlers)
    return logging.getLogger("orchestrator")


# ── 사용자 입력 파싱 ──────────────────────────────────────────────
CITY_MAP = {
    "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시",
    "인천": "인천광역시", "광주": "광주광역시", "대전": "대전광역시",
    "울산": "울산광역시", "세종": "세종특별자치시", "경기": "경기도",
    "강원": "강원도", "충북": "충청북도", "충남": "충청남도",
    "전북": "전라북도", "전남": "전라남도", "경북": "경상북도",
    "경남": "경상남도", "제주": "제주특별자치도",
}


def parse_user_input(text: str) -> SearchCriteria:
    """
    자연어 → SearchCriteria 변환
    예시: "대전 유성구 아파트 40㎡ 이상 분석해줘"
          "경기도 수원시 영통구 오피스텔"
    """
    city = ""
    district = ""
    property_type = "아파트"
    min_area = 40.0

    # 시도 추출
    for short, full in CITY_MAP.items():
        if short in text:
            city = short
            break

    # 시군구 추출 (XX구, XX시, XX군)
    district_m = re.search(r"([가-힣]+(?:구|시|군))", text)
    if district_m:
        district = district_m.group(1)

    # 물건 종류
    for pt in ["아파트", "오피스텔", "빌라", "상가", "토지"]:
        if pt in text:
            property_type = pt
            break

    # 면적 하한
    area_m = re.search(r"(\d+)\s*(?:㎡|m²|평)", text)
    if area_m:
        val = float(area_m.group(1))
        # 평 → ㎡ 변환
        if "평" in text[area_m.start():area_m.end() + 2]:
            val *= 3.306
        min_area = val

    if not city:
        raise ValueError(f"도시를 인식할 수 없습니다: '{text}'\n예) '대전 유성구 아파트 분석'")
    if not district:
        raise ValueError(f"구/군/시를 인식할 수 없습니다: '{text}'\n예) '대전 유성구 아파트 분석'")

    return SearchCriteria(
        city=city,
        district=district,
        property_type=property_type,
        min_area=min_area,
    )


# ── 파이프라인 상태 저장/로드 ─────────────────────────────────────
def save_state(run_id: str, state: dict):
    state_path = LOGS_DIR / f"state_{run_id}.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_state(run_id: str) -> dict:
    state_path = LOGS_DIR / f"state_{run_id}.json"
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ── 실행 로그 출력 ────────────────────────────────────────────────
def print_banner(text: str):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_summary(result: dict):
    print_banner("파이프라인 실행 결과")
    cases = result.get("cases", [])
    reports = result.get("reports", [])

    print(f"  처리 사건 수   : {len(cases)}")
    print(f"  생성 보고서 수  : {len(reports)}")

    if result.get("errors"):
        print(f"\n  ⚠ 오류 ({len(result['errors'])}건):")
        for e in result["errors"]:
            print(f"    - {e}")

    print("\n  생성된 파일:")
    for r in reports:
        print(f"    ✓ [{r['case_no']}] {r['path']}")


# ── 메인 파이프라인 ───────────────────────────────────────────────
async def run_pipeline(user_input: str, run_id: str) -> dict:
    logger = logging.getLogger("orchestrator")
    final_result: dict = {
        "run_id": run_id,
        "user_input": user_input,
        "criteria": {},
        "cases": [],
        "reports": [],
        "errors": [],
        "started_at": datetime.now().isoformat(),
        "finished_at": "",
    }

    # ─── 입력 파싱 ──────────────────────────────────────────────
    try:
        criteria = parse_user_input(user_input)
        final_result["criteria"] = {
            "city": criteria.city,
            "district": criteria.district,
            "property_type": criteria.property_type,
            "min_area": criteria.min_area,
        }
        logger.info(
            f"검색 기준: {criteria.city} {criteria.district} "
            f"{criteria.property_type} ≥{criteria.min_area}㎡"
        )
    except ValueError as e:
        final_result["errors"].append(str(e))
        logger.error(str(e))
        return final_result

    pipeline_state: dict = {}

    # ─── Agent 1: TankAuction 스크래핑 ──────────────────────────
    print_banner("Agent 1: TankAuction 경매 목록 수집 중...")
    try:
        a1_result = await run_agent1(criteria)
        pipeline_state["agent1"] = a1_result
        save_state(run_id, pipeline_state)

        if a1_result["status"] == "blocked":
            logger.error("Agent1 차단 — 수동 로그인 필요")
            final_result["errors"].extend(a1_result["errors"])
            final_result["finished_at"] = datetime.now().isoformat()
            return final_result

        cases_raw = a1_result.get("cases", [])
        final_result["cases"] = [c["case_no"] for c in cases_raw]
        logger.info(f"Agent1 완료: {len(cases_raw)}건")

    except Exception as e:
        logger.error(f"Agent1 치명적 오류: {e}", exc_info=True)
        final_result["errors"].append(f"Agent1: {e}")
        final_result["finished_at"] = datetime.now().isoformat()
        return final_result

    # 이후 에이전트에 넘길 details 목록 구성
    details_for_agents = []
    case_nos = []
    for c in cases_raw:
        d = c.get("details") or {}
        details_for_agents.append({
            "address": c.get("address", ""),
            "complex_name": d.get("complex_name", ""),
            "building_no": d.get("building_no", ""),
            "unit_no": d.get("unit_no", ""),
            "floor": d.get("floor", ""),
            "area_supply": d.get("area_supply", 0),
            "area_private": d.get("area_private", 0),
            "area_land": d.get("area_land", 0),
        })
        case_nos.append(c["case_no"])

    if not case_nos:
        logger.warning("수집된 경매 물건이 없습니다.")
        final_result["finished_at"] = datetime.now().isoformat()
        return final_result

    # ─── Agent 2 & 3 병렬 실행 ──────────────────────────────────
    print_banner("Agent 2+3: 네이버/아실/입지 데이터 병렬 수집 중...")
    try:
        a2_task = asyncio.create_task(
            run_agent2(details_for_agents, case_nos)
        )
        a3_task = asyncio.create_task(
            run_agent3(details_for_agents, case_nos)
        )
        a2_result, a3_result = await asyncio.gather(a2_task, a3_task, return_exceptions=True)

        if isinstance(a2_result, Exception):
            logger.error(f"Agent2 오류: {a2_result}")
            a2_result = {"agent": "agent2_naver_asil", "status": "error", "cases": [], "errors": [str(a2_result)]}
        if isinstance(a3_result, Exception):
            logger.error(f"Agent3 오류: {a3_result}")
            a3_result = {"agent": "agent3_spatial", "status": "error", "cases": [], "errors": [str(a3_result)]}

        pipeline_state["agent2"] = a2_result
        pipeline_state["agent3"] = a3_result
        save_state(run_id, pipeline_state)

        logger.info(
            f"Agent2 완료: {len(a2_result.get('cases', []))}건  "
            f"Agent3 완료: {len(a3_result.get('cases', []))}건"
        )
        final_result["errors"].extend(a2_result.get("errors", []))
        final_result["errors"].extend(a3_result.get("errors", []))

    except Exception as e:
        logger.error(f"Agent2/3 오류: {e}", exc_info=True)
        final_result["errors"].append(f"Agent2/3: {e}")
        pipeline_state["agent2"] = {"cases": [], "errors": [str(e)]}
        pipeline_state["agent3"] = {"cases": [], "errors": [str(e)]}

    # ─── Agent 4: 자산 정리 ──────────────────────────────────────
    print_banner("Agent 4: 파일 자산 정리 및 검증 중...")
    try:
        a4_result = run_agent4(pipeline_state)
        pipeline_state["agent4"] = a4_result
        save_state(run_id, pipeline_state)
        logger.info(f"Agent4 완료: {len(a4_result.get('cases', []))}건")
        final_result["errors"].extend(a4_result.get("errors", []))
    except Exception as e:
        logger.error(f"Agent4 오류: {e}", exc_info=True)
        pipeline_state["agent4"] = {"cases": [], "errors": [str(e)]}

    # ─── Agent 5: 엑셀 보고서 생성 ──────────────────────────────
    print_banner("Agent 5: 엑셀 보고서 생성 중...")
    try:
        a5_result = run_agent5(pipeline_state)
        pipeline_state["agent5"] = a5_result
        save_state(run_id, pipeline_state)

        final_result["reports"] = a5_result.get("reports", [])
        final_result["errors"].extend(a5_result.get("errors", []))
        logger.info(f"Agent5 완료: {len(final_result['reports'])}개 보고서 생성")
    except Exception as e:
        logger.error(f"Agent5 오류: {e}", exc_info=True)
        final_result["errors"].append(f"Agent5: {e}")

    final_result["finished_at"] = datetime.now().isoformat()
    return final_result


# ── 엔트리포인트 ──────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("사용법: python orchestrator.py \"대전 유성구 아파트 분석해줘\"")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    logger = setup_logging(run_id)
    print_banner(f"경매 분석 파이프라인 시작 [{run_id}]")
    print(f"  입력: {user_input}")

    result = asyncio.run(run_pipeline(user_input, run_id))
    print_summary(result)

    # 최종 결과 JSON 저장
    result_path = LOGS_DIR / f"result_{run_id}.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  실행 로그: {LOGS_DIR}/pipeline_{run_id}.log")
    print(f"  결과 JSON: {result_path}\n")

    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
