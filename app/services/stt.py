import os
import subprocess
import torch
import torchaudio
from typing import List, Tuple
import whisper
from silero_vad import VoiceActivityDetector, collect_chunks


# ✅ 1. webm → wav 변환
def convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    command = f"ffmpeg -y -i {webm_path} -ar 16000 -ac 1 {wav_path}"
    subprocess.run(command, shell=True)
    return wav_path


# ✅ 2. Silero로 말한 구간 탐지 → [start, end] (초 단위)
def get_speech_timestamps(wav_path: str) -> List[Tuple[float, float]]:
    # 오디오 불러오기
    wav, sample_rate = torchaudio.load(wav_path)
    if sample_rate != 16000:
        wav = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(wav)

    # 모델 불러오기
    model = VoiceActivityDetector()
    speech_chunks = model.detect_voice(wav[0], sample_rate=16000)

    return speech_chunks


# ✅ 3. Whisper로 말한 구간들만 STT
def transcribe_with_whisper(wav_path: str) -> str:
    print("📦 Whisper 모델 로딩 중...")
    model = whisper.load_model("base")

    print("🔍 말한 구간 추출 중 (Silero)...")
    speech_timestamps = get_speech_timestamps(wav_path)

    if not speech_timestamps:
        return "⚠️ 음성이 감지되지 않았습니다."

    # 전체 오디오 불러오기
    wav, _ = torchaudio.load(wav_path)

    results = []
    for idx, (start_sec, end_sec) in enumerate(speech_timestamps):
        start_sample = int(start_sec * 16000)
        end_sample = int(end_sec * 16000)

        chunk_path = wav_path.replace(".wav", f"_chunk{idx}.wav")
        torchaudio.save(chunk_path, wav[:, start_sample:end_sample], 16000)

        result = model.transcribe(chunk_path, language="ko")
        results.append(result["text"])

    return "\n".join(results)
