"""
Typecast TTS Skill
텍스트를 음성(MP3/WAV)으로 변환하는 스킬.
"""

import requests
import os
from pathlib import Path

API_KEY = "__pltUaT5cx75C5jCgdvyoi7SGwGRY8TPBnJvtyRWnNPx"
DEFAULT_VOICE_ID = "tc_699d27c4b4af39da12bfff46"  # 뽀또
API_URL = "https://api.typecast.ai/v1/text-to-speech"


def text_to_speech(
    text: str,
    output_path: str = "output.mp3",
    voice_id: str = DEFAULT_VOICE_ID,
    audio_format: str = "mp3",
    volume: int = 100,
    audio_pitch: int = 0,
    audio_tempo: float = 1.0,
    model: str = "ssfm-v30",
) -> str:
    """
    텍스트를 Typecast API로 음성 변환 후 파일로 저장.

    Args:
        text: 변환할 텍스트 (1~2000자)
        output_path: 저장할 파일 경로
        voice_id: 사용할 보이스 ID
        audio_format: 오디오 형식 ('mp3' 또는 'wav')
        volume: 볼륨 (0~200, 기본 100)
        audio_pitch: 피치 (-12~12, 기본 0)
        audio_tempo: 속도 (0.5~2.0, 기본 1.0)
        model: 모델 버전 ('ssfm-v30' 또는 'ssfm-v21')

    Returns:
        저장된 파일의 절대 경로
    """
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY,
    }

    payload = {
        "voice_id": voice_id,
        "text": text,
        "model": model,
        "output": {
            "audio_format": audio_format,
            "volume": volume,
            "audio_pitch": audio_pitch,
            "audio_tempo": audio_tempo,
        },
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"API 오류 {response.status_code}: {response.text}"
        )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(response.content)

    return str(output_file.resolve())
