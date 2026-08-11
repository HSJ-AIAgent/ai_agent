@echo off
echo ===================================================
echo  경매 분석 파이프라인 환경 설정
echo ===================================================

REM Python 패키지 설치
pip install -r requirements.txt

REM Playwright 브라우저 설치
playwright install chromium

REM .env 파일 생성 안내
if not exist .env (
    echo.
    echo [안내] .env 파일을 생성해 주세요:
    copy .env.example .env
    echo .env.example 을 .env 로 복사했습니다. 내용을 수정하세요.
)

echo.
echo 설정 완료! 다음 명령으로 실행하세요:
echo   python orchestrator.py "대전 유성구 아파트 분석해줘"
pause
