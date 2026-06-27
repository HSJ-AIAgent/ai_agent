# -*- coding: utf-8 -*-
"""
네이버 데이터랩 쇼핑 인사이트 API
https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md

[API 명세 - 엔드포인트 목록]
  ① 분야별 트렌드       : POST https://openapi.naver.com/v1/datalab/shopping/categories
  ② 분야 내 기기별      : POST https://openapi.naver.com/v1/datalab/shopping/category/device
  ③ 분야 내 성별        : POST https://openapi.naver.com/v1/datalab/shopping/category/gender
  ④ 분야 내 연령별      : POST https://openapi.naver.com/v1/datalab/shopping/category/age
  ⑤ 키워드별 트렌드     : POST https://openapi.naver.com/v1/datalab/shopping/category/keywords
  ⑥ 키워드 기기별       : POST https://openapi.naver.com/v1/datalab/shopping/category/keyword/device
  ⑦ 키워드 성별         : POST https://openapi.naver.com/v1/datalab/shopping/category/keyword/gender
  ⑧ 키워드 연령별       : POST https://openapi.naver.com/v1/datalab/shopping/category/keyword/age
  하루 호출 한도 : 1,000회

[요청 헤더]
  X-Naver-Client-Id / X-Naver-Client-Secret / Content-Type: application/json

[① 분야별 트렌드 파라미터]
  startDate (string, 필수) : yyyy-mm-dd (2017-08-01 이후)
  endDate   (string, 필수) : yyyy-mm-dd
  timeUnit  (string, 필수) : date | week | month
  category  (array,  필수) : 최대 3개
    - name  (string) : 분야 이름
    - param (array)  : 분야 코드 (네이버쇼핑 URL의 cat_id 값)
  device    (string, 선택) : "" | "pc" | "mo"
  gender    (string, 선택) : "" | "m" | "f"
  ages      (array,  선택) : [] 또는 "10"(10~19세) ~ "60"(60세 이상) 배열

[⑤ 키워드별 트렌드 파라미터]
  startDate (string, 필수) : yyyy-mm-dd
  endDate   (string, 필수) : yyyy-mm-dd
  timeUnit  (string, 필수) : date | week | month
  category  (string, 필수) : 단일 분야 코드
  keyword   (array,  필수) : 최대 3개
    - name  (string) : 키워드 그룹명
    - param (array)  : 실제 검색 키워드 목록

[주요 카테고리 코드]
  50000000 - 패션의류   50000001 - 패션잡화   50000002 - 화장품/미용
  50000003 - 디지털/가전 50000004 - 가구/인테리어 50000005 - 출산/육아
  50000006 - 식품       50000007 - 스포츠/레저  50000008 - 생활/건강
"""

import json
import requests
from config import HEADERS

ENDPOINT_CATEGORIES = "https://openapi.naver.com/v1/datalab/shopping/categories"
ENDPOINT_KEYWORDS   = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"


def get_category_trend(
    start_date: str,
    end_date: str,
    categories: list,
    time_unit: str = "month",
    device: str = "",
    gender: str = "",
    ages: list = None,
) -> dict:
    """① 분야별 트렌드 조회"""
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": categories,
        "device": device,
        "gender": gender,
        "ages": ages or [],
    }
    response = requests.post(ENDPOINT_CATEGORIES, headers=HEADERS, json=body)
    response.raise_for_status()
    return response.json()


def get_keyword_trend(
    start_date: str,
    end_date: str,
    category_code: str,
    keywords: list,
    time_unit: str = "month",
    device: str = "",
    gender: str = "",
    ages: list = None,
) -> dict:
    """⑤ 키워드별 트렌드 조회"""
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": category_code,
        "keyword": keywords,
        "device": device,
        "gender": gender,
        "ages": ages or [],
    }
    response = requests.post(ENDPOINT_KEYWORDS, headers=HEADERS, json=body)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    START = "2025-01-01"
    END   = "2026-06-01"

    print("=== [①] 쇼핑인사이트 분야별 트렌드 ===")
    categories = [
        {"name": "패션의류",   "param": ["50000000"]},
        {"name": "화장품/미용", "param": ["50000002"]},
        {"name": "식품",       "param": ["50000006"]},
    ]
    r1 = get_category_trend(START, END, categories, time_unit="month")
    print(f"조회기간: {r1.get('startDate')} ~ {r1.get('endDate')}")
    for item in r1.get("results", []):
        last = item["data"][-1] if item.get("data") else {}
        print(f"  [{item['title']}] 최근 비율: {last.get('ratio')} ({last.get('period')})")

    print("\n=== [⑤] 쇼핑인사이트 키워드별 트렌드 (패션의류 카테고리) ===")
    keywords = [
        {"name": "원피스", "param": ["원피스"]},
        {"name": "청바지", "param": ["청바지"]},
        {"name": "코트",   "param": ["코트"]},
    ]
    r2 = get_keyword_trend(START, END, "50000000", keywords, time_unit="month")
    print(f"조회기간: {r2.get('startDate')} ~ {r2.get('endDate')}")
    for item in r2.get("results", []):
        last = item["data"][-1] if item.get("data") else {}
        print(f"  [{item['title']}] 최근 비율: {last.get('ratio')} ({last.get('period')})")
