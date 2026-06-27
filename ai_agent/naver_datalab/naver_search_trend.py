# -*- coding: utf-8 -*-
"""
네이버 데이터랩 통합 검색어 트렌드 API
https://developers.naver.com/docs/serviceapi/datalab/search/search.md

[API 명세]
  요청 URL : POST https://openapi.naver.com/v1/datalab/search
  하루 호출 한도 : 1,000회

[요청 헤더]
  X-Naver-Client-Id     : 클라이언트 아이디
  X-Naver-Client-Secret : 클라이언트 시크릿
  Content-Type          : application/json

[요청 파라미터 (JSON body)]
  startDate    (string, 필수) : 조회 시작일 yyyy-mm-dd (2016-01-01 이후)
  endDate      (string, 필수) : 조회 종료일 yyyy-mm-dd
  timeUnit     (string, 필수) : 집계 단위 - date(일간) | week(주간) | month(월간)
  keywordGroups (array, 필수) : 최대 5개 그룹
    - groupName (string, 필수) : 주제어 (그룹 대표 이름)
    - keywords  (array, 필수)  : 해당 주제어의 검색어 목록, 최대 20개
  device       (string, 선택) : "" | "pc" | "mo"
  gender       (string, 선택) : "" | "m" | "f"
  ages         (array,  선택) : [] 또는 "1"(0~12세) ~ "11"(60세 이상) 배열

[응답]
  startDate / endDate / timeUnit
  results[].title    : 주제어(groupName)
  results[].keywords : 검색어 목록
  results[].data[].period : 구간 시작일
  results[].data[].ratio  : 검색량 상대 비율 (최대값=100)
"""

import json
import requests
from config import HEADERS

ENDPOINT = "https://openapi.naver.com/v1/datalab/search"


def get_search_trend(
    start_date: str,
    end_date: str,
    keyword_groups: list,
    time_unit: str = "month",
    device: str = "",
    gender: str = "",
    ages: list = None,
) -> dict:
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups,
        "device": device,
        "gender": gender,
        "ages": ages or [],
    }
    response = requests.post(ENDPOINT, headers=HEADERS, json=body)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    keyword_groups = [
        {"groupName": "인공지능", "keywords": ["인공지능", "AI", "ChatGPT"]},
        {"groupName": "머신러닝", "keywords": ["머신러닝", "딥러닝"]},
    ]

    result = get_search_trend(
        start_date="2025-01-01",
        end_date="2026-06-01",
        keyword_groups=keyword_groups,
        time_unit="month",
    )

    print("=== 통합 검색어 트렌드 API 결과 ===")
    print(f"조회기간: {result.get('startDate')} ~ {result.get('endDate')} ({result.get('timeUnit')})")
    for r in result.get("results", []):
        print(f"\n[{r['title']}] 키워드: {r['keywords']}")
        for d in r.get("data", []):
            print(f"  {d['period']} : {d['ratio']}")
