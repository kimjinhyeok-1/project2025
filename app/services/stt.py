import os
import subprocess
import torch
import torchaudio
import whisper
from typing import List
from silero_vad import get_speech_timestamps

# ✅ 1. webm → wav 변환
def convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    command = f"ffmpeg -y -i {webm_path} -ar 16000 -ac 1 {wav_path}"
    subprocess.run(command, shell=True)
    return wav_path

# ✅ 2. Whisper로 말한 구간만 STT
def transcribe_with_whisper(wav_path: str) -> str:
    model = whisper.load_model("base")
    waveform, sample_rate = torchaudio.load(wav_path)

    # Silero VAD 모델 불러오기 (자동 다운로드)
    vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', trust_repo=True)
    get_speech_ts = utils['get_speech_timestamps']

    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)
        sample_rate = 16000

    speech_timestamps = get_speech_ts(waveform[0], vad_model, sampling_rate=sample_rate)

    if not speech_timestamps:
        return "⚠️ 음성이 감지되지 않았습니다."

    results = []
    for i, ts in enumerate(speech_timestamps):
        start = ts['start']
        end = ts['end']
        chunk = waveform[:, start:end]

        chunk_path = wav_path.replace(".wav", f"_chunk{i}.wav")
        torchaudio.save(chunk_path, chunk, sample_rate)

        result = model.transcribe(chunk_path, language="ko")
        results.append(result["text"])

    return "\n".join(results)
