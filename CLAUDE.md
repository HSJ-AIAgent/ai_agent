# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소에서 작업할 때 참고하는 가이드입니다.

## 언어 설정

모든 대답은 반드시 한국어로 작성한다. 사용자가 영어로 질문하더라도 한국어로 응답한다.

## 프로젝트 개요

`data.csv`를 읽어 `name` 및 `memo` 필드의 불필요한 공백과 특수문자를 제거한 뒤 `output.csv`로 저장하는 Python 데이터 정리 스크립트입니다.

## 실행 방법

```bash
cd my_project
python main.py
```

실행 전 의존성 설치:

```bash
pip install -r my_project/requirements.txt
```

## 아키텍처

- `main.py` — 진입점. `csv.DictReader`로 `data.csv`를 읽고, `name`과 `memo` 컬럼에 정제 함수를 적용한 후 `output.csv`를 작성한다.
- `utils.py` — 순수 유틸리티 함수 모음: `clean_text`(앞뒤 공백 제거 및 연속 공백 단일화), `format_date`(YYYYMMDD → YYYY-MM-DD). 부작용 없음.
- `config.json` — 런타임 설정(`output_dir`, `log_level`, `max_rows`, `input_encoding`). 현재 **`main.py`에 연동되지 않음** — 추후 이 설정을 실제로 로드하여 적용해야 한다.

## 미완성 사항 (notes.txt 기준)

- `utils.py`의 `format_date` 엣지케이스 테스트 미완료.
- `config.json`의 `output_dir`가 `main.py`에서 사용되지 않음.
- 설정에 `log_level`이 정의되어 있으나 로깅 미구현.
- 단위 테스트 없음.
