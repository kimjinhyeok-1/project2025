# app/config.py

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 환경변수가 없습니다.")
if not OPENAI_ASSISTANT_ID:
    raise ValueError("OPENAI_ASSISTANT_ID 환경변수가 없습니다.")
