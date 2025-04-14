import os
import subprocess
import whisper

# ✅ webm → wav 변환 (FFmpeg 사용)
def convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    command = f"ffmpeg -y -i {webm_path} -ar 16000 -ac 1 {wav_path}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 변환 실패:", e)
        raise
    return wav_path

# ✅ Whisper로 전체 음성 STT
def transcribe_with_whisper(wav_path: str) -> str:
    print("📦 Whisper 모델 로딩 중...")
    model = whisper.load_model("base")

    print(f"🧠 Whisper STT 수행 중: {wav_path}")
    result = model.transcribe(wav_path, language="ko")

    full_text = result["text"]
    print("📝 전체 변환 결과:", full_text)
    return full_text
