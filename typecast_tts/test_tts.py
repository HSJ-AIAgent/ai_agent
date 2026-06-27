"""
Typecast TTS 스킬 테스트 스크립트
테스트 문장: "안녕하세요 저는 홍승재입니다"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from tts_skill import text_to_speech

TEST_TEXT = "안녕하세요 저는 홍승재입니다"
OUTPUT_FILE = "output_test.mp3"


def run_test():
    print("=" * 50)
    print("Typecast TTS 스킬 테스트")
    print("=" * 50)
    print(f"변환 텍스트 : {TEST_TEXT}")
    print(f"보이스 ID   : tc_699d27c4b4af39da12bfff46 (뽀또)")
    print(f"출력 파일   : {OUTPUT_FILE}")
    print("-" * 50)

    try:
        saved_path = text_to_speech(
            text=TEST_TEXT,
            output_path=OUTPUT_FILE,
            audio_format="mp3",
        )
        file_size = os.path.getsize(saved_path)
        print(f"[성공] 음성 파일 생성 완료!")
        print(f"  경로   : {saved_path}")
        print(f"  크기   : {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    except RuntimeError as e:
        print(f"[실패] {e}")
        sys.exit(1)

    print("=" * 50)


if __name__ == "__main__":
    run_test()
