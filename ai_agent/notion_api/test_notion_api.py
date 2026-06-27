"""
Notion API 연결 및 기능 테스트 스크립트
- Internal Integration Token (ntn_...) 사용
- 인증, 사용자 조회, 페이지 검색, 페이지 읽기/생성 등 핵심 기능 테스트
"""

import requests
import json

NOTION_TOKEN = "YOUR_NOTION_API_TOKEN"  # 환경 변수로 관리 권장: os.environ.get("NOTION_TOKEN")
BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def print_result(title, response):
    print(f"\n{'='*60}")
    print(f"[테스트] {title}")
    print(f"상태코드: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        print(response.text)
    return response.status_code == 200


def test_auth():
    """인증 및 봇 사용자 정보 조회"""
    r = requests.get(f"{BASE_URL}/users/me", headers=HEADERS)
    return print_result("인증 확인 (GET /users/me)", r)


def test_list_users():
    """워크스페이스 사용자 목록 조회"""
    r = requests.get(f"{BASE_URL}/users", headers=HEADERS)
    return print_result("사용자 목록 조회 (GET /users)", r)


def test_search_pages():
    """페이지/데이터베이스 검색"""
    body = {"filter": {"value": "page", "property": "object"}, "page_size": 5}
    r = requests.post(f"{BASE_URL}/search", headers=HEADERS, json=body)
    ok = print_result("페이지 검색 (POST /search)", r)
    # 검색된 페이지 ID 반환 (이후 테스트에 활용)
    if ok:
        results = r.json().get("results", [])
        if results:
            return results[0]["id"]
    return None


def test_search_databases():
    """데이터베이스 검색"""
    body = {"filter": {"value": "database", "property": "object"}, "page_size": 5}
    r = requests.post(f"{BASE_URL}/search", headers=HEADERS, json=body)
    ok = print_result("데이터베이스 검색 (POST /search - database)", r)
    if ok:
        results = r.json().get("results", [])
        if results:
            return results[0]["id"]
    return None


def test_get_page(page_id):
    """특정 페이지 정보 조회"""
    if not page_id:
        print("\n[건너뜀] 조회할 페이지 ID 없음")
        return False
    r = requests.get(f"{BASE_URL}/pages/{page_id}", headers=HEADERS)
    return print_result(f"페이지 조회 (GET /pages/{page_id})", r)


def test_get_page_blocks(page_id):
    """페이지 블록(내용) 조회"""
    if not page_id:
        print("\n[건너뜀] 조회할 페이지 ID 없음")
        return False
    r = requests.get(f"{BASE_URL}/blocks/{page_id}/children", headers=HEADERS)
    return print_result(f"페이지 블록 조회 (GET /blocks/{page_id}/children)", r)


def test_query_database(db_id):
    """데이터베이스 쿼리"""
    if not db_id:
        print("\n[건너뜀] 조회할 데이터베이스 ID 없음")
        return False
    r = requests.post(f"{BASE_URL}/databases/{db_id}/query", headers=HEADERS, json={"page_size": 5})
    return print_result(f"데이터베이스 쿼리 (POST /databases/{db_id}/query)", r)


def main():
    print("=" * 60)
    print("  Notion API 테스트 시작")
    print("=" * 60)

    results = {}

    # 1. 인증 확인
    results["인증"] = test_auth()

    # 2. 사용자 목록
    results["사용자목록"] = test_list_users()

    # 3. 페이지 검색
    page_id = test_search_pages()
    results["페이지검색"] = page_id is not None

    # 4. 데이터베이스 검색
    db_id = test_search_databases()
    results["DB검색"] = db_id is not None

    # 5. 페이지 상세 조회
    results["페이지조회"] = test_get_page(page_id)

    # 6. 페이지 블록 조회
    results["블록조회"] = test_get_page_blocks(page_id)

    # 7. 데이터베이스 쿼리
    results["DB쿼리"] = test_query_database(db_id)

    # 결과 요약
    print(f"\n{'='*60}")
    print("  테스트 결과 요약")
    print("=" * 60)
    for name, ok in results.items():
        status = "[OK] 성공" if ok else "[NG] 실패"
        print(f"  {status}  {name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
