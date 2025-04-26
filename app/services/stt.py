# 📄 stt.py (최적화 버전)

import whisper
import subprocess
import os

# 🔥 Whisper 모델 글로벌 캐싱
model = None

def load_model():
    global model
    if model is None:
        print("📦 Whisper 모델 로딩 중...")
        model = whisper.load_model("tiny")  # tiny 또는 small 선택 가능
        print("✅ Whisper 모델 로딩 완료!")

def convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    
    try:
        # ffmpeg로 변환
        command = [
            "ffmpeg", "-i", webm_path,
            "-ar", "16000",  # 샘플링 레이트 16kHz
            "-ac", "1",       # 모노 채널
            wav_path,
            "-y"               # 기존 파일 덮어쓰기
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ ffmpeg 변환 완료: {wav_path}")
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 변환 중 에러 발생:", e)
        raise

    return wav_path

def transcribe_with_whisper(audio_path: str) -> str:
    load_model()  # 🔥 호출할 때마다 모델 존재 여부 확인

    try:
        result = model.transcribe(audio_path)
        transcript = result.get("text", "").strip()

        if not transcript:
            print("⚠️ Whisper 결과가 비어 있습니다.")
            return "음성이 감지되지 않았습니다."

        return transcript

    except Exception as e:
        print("❌ Whisper 변환 실패:", e)
        raise
