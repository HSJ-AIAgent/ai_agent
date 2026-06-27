import re

def clean_text(text):
    """불필요한 공백 및 특수문자 제거"""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def format_date(date_str):
    """YYYYMMDD -> YYYY-MM-DD 변환"""
    if len(date_str) == 8 and date_str.isdigit():
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return date_str
