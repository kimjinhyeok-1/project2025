import os

# 환경 변수에서 값 불러오기
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 환경 변수가 설정되지 않은 경우 에러 처리 (선택 사항)
if not ASSISTANT_ID:
    raise ValueError("ASSISTANT_ID 환경 변수가 설정되지 않았습니다.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
