import os
import subprocess

def convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    command = f"ffmpeg -y -i {webm_path} -ar 16000 -ac 1 {wav_path}"
    subprocess.run(command, shell=True)
    return wav_path

def transcribe_with_whisper(wav_path: str) -> str:
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(wav_path, language="ko")
    return result["text"]
