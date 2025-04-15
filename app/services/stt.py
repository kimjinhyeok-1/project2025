import os
import subprocess
import whisper

# ✅ ffmpeg 설치 확인 (서버가 실행될 때만 1회 체크)
if subprocess.run("which ffmpeg", shell=True, capture_output=True).returncode != 0:
    raise EnvironmentError("❌ ffmpeg가 설치되어 있지 않습니다. 서버에 ffmpeg를 설치해주세요.")

# ✅ webm → wav 변환
def convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    command = f"ffmpeg -y -i {webm_path} -ar 16000 -ac 1 {wav_path}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 변환 실패:", e)
        raise
    return wav_path

# ✅ Whisper로 전체 음성 STT (Lazy Load 방식)
def transcribe_with_whisper(wav_path: str) -> str:
    print("📦 Whisper 모델 로딩 중...")
    try:
        model = whisper.load_model("base")  # ❗ 필요할 때만 로딩하여 메모리 절약
        result = model.transcribe(wav_path, language="ko")
        full_text = result["text"]
        print("📝 전체 변환 결과:", full_text)
        return full_text
    except Exception as e:
        print("❌ Whisper STT 실패:", e)
        return "⚠️ 음성을 텍스트로 변환하지 못했습니다."
