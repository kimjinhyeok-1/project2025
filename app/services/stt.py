import os
import subprocess
import whisper

# ✅ Whisper 모델을 지연 로딩 (캐시)
_model = None

# ✅ ffmpeg 설치 확인
if subprocess.run("which ffmpeg", shell=True, capture_output=True).returncode != 0:
    raise EnvironmentError("❌ ffmpeg가 설치되어 있지 않습니다. 서버에 ffmpeg를 설치해주세요.")

# ✅ webm → wav 변환
def convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    try:
        subprocess.run(f"ffmpeg -y -i {webm_path} -ar 16000 -ac 1 {wav_path}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 변환 실패:", e)
        raise
    return wav_path

# ✅ Whisper STT 수행
def transcribe_with_whisper(wav_path: str) -> str:
    global _model
    try:
        if _model is None:
            print("📦 Whisper 모델 로딩 중 (지연 로딩)...")
            _model = whisper.load_model("small")  # small 모델 사용

        result = _model.transcribe(wav_path, language="ko")
        return result["text"]

    except Exception as e:
        print("❌ Whisper STT 실패:", e)
        return "음성을 변환하지 못했습니다."
