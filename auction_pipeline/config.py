import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
DOCS_DIR = ASSETS_DIR / "docs"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATE_PATH = BASE_DIR / "template.xlsx"

for d in [IMAGES_DIR, DOCS_DIR, OUTPUT_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TANK_ID = os.getenv("TANK_ID", "")
TANK_PW = os.getenv("TANK_PW", "")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
BROWSER_TIMEOUT = 30000
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY", "")

TANK_BASE_URL = "https://www.tankauction.com"
NAVER_LAND_URL = "https://land.naver.com"
HOGANGNONO_URL = "https://hogangnono.com"
ASIL_URL = "https://asil.kr"
KAKAO_MAP_URL = "https://map.kakao.com"

DEFAULT_PROPERTY_TYPE = "아파트"
DEFAULT_STATUS = "진행물건"
DEFAULT_MIN_AREA = 40.0

REQUEST_DELAY_MIN = 1.0
REQUEST_DELAY_MAX = 3.0
