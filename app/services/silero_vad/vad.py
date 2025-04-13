# app/services/silero_vad/vad.py

import torch
from app.services.silero_vad.utils_vad import get_speech_timestamps, init_jit_model

def detect_voice(audio_tensor, sample_rate=16000):
    model = init_jit_model()
    speech_timestamps = get_speech_timestamps(audio_tensor, model, sampling_rate=sample_rate)
    return speech_timestamps
