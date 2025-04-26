import os
import subprocess
import whisper

# ✅ 지연 로딩을 위한 모델 전역 변수 선언 (처음엔 None)
_model = None

# ✅ 서버 시작 시 ffmpeg 설치 확인
def check_ffmpeg_installed():
    result = subprocess.run(
        ["which", "ffmpeg"], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise EnvironmentError("❌ ffmpeg가 설치되어 있지 않습니다. 서버에 ffmpeg를 설치해주세요.")
    else:
        print("✅ ffmpeg 설치 확인 완료")

check_ffmpeg_installed()

# ✅ webm → wav 변환
def convert_webm_to_wav(webm_path: str) -> str:
    if not os.path.exists(webm_path):
        raise FileNotFoundError(f"❌ 변환하려는 webm 파일이 존재하지 않습니다: {webm_path}")

    wav_path = webm_path.replace(".webm", ".wav")
    command = [
        "ffmpeg",
        "-y",
        "-i", webm_path,
        "-ar", "16000",
        "-ac", "1",
        wav_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ ffmpeg 변환 완료: {wav_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ ffmpeg 변환 실패: {e}")
        raise RuntimeError(f"ffmpeg 변환 실패: {e}")

    return wav_path

# ✅ Whisper로 전체 음성 STT
def transcribe_with_whisper(wav_path: str) -> str:
    global _model

    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"❌ 변환하려는 wav 파일이 존재하지 않습니다: {wav_path}")

    try:
        if _model is None:
            print("📦 Whisper 모델 로딩 중 (지연 로딩)...")
            _model = whisper.load_model("tiny")
            print("✅ Whisper 모델 로딩 완료")

        result = _model.transcribe(wav_path, language="ko")
        full_text = result.get("text", "").strip()

        if not full_text:
            print("⚠️ 변환 결과가 비어 있습니다.")
            return "음성을 변환하지 못했습니다."

        print("📝 전체 변환 결과:", full_text)
        return full_text

    except Exception as e:
        print("❌ Whisper STT 실패:", e)
        return "음성을 변환하지 못했습니다."
