import os
import subprocess
import torch
import torchaudio
from typing import List, Tuple
import whisper
from app.services.silero_vad.vad import detect_voice


# ✅ 1. webm → wav 변환
def convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    command = f"ffmpeg -y -i {webm_path} -ar 16000 -ac 1 {wav_path}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 변환 실패:", e)
        raise
    return wav_path

# ✅ 2. Silero로 말한 구간 탐지
def get_speech_timestamps(wav_path: str) -> List[Tuple[float, float]]:
    print(f"🔎 VAD 분석 시작: {wav_path}")
    wav, sample_rate = torchaudio.load(wav_path)

    if sample_rate != 16000:
        wav = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(wav)

    model = VoiceActivityDetector()
    speech_chunks = model.detect_voice(wav[0], sample_rate=16000)

    print(f"🧩 감지된 음성 구간 개수: {len(speech_chunks)}")
    return speech_chunks

# ✅ 3. Whisper로 말한 구간 STT
def transcribe_with_whisper(wav_path: str) -> str:
    print("📦 Whisper 모델 로딩 중...")
    model = whisper.load_model("base")

    print("🔍 말한 구간 추출 중 (Silero)...")
    speech_timestamps = get_speech_timestamps(wav_path)

    if not speech_timestamps:
        return "⚠️ 음성이 감지되지 않았습니다."

    wav, _ = torchaudio.load(wav_path)
    results = []

    for idx, (start_sec, end_sec) in enumerate(speech_timestamps):
        start_sample = int(start_sec * 16000)
        end_sample = int(end_sec * 16000)

        chunk_path = wav_path.replace(".wav", f"_chunk{idx}.wav")
        torchaudio.save(chunk_path, wav[:, start_sample:end_sample], 16000)

        print(f"🧠 Whisper STT 중: {chunk_path}")
        result = model.transcribe(chunk_path, language="ko")
        results.append(result["text"])

    full_text = "\n".join(results)
    print("📝 전체 변환 결과:", full_text)
    return full_text
