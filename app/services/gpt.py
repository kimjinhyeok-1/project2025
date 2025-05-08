import os
import traceback
from openai import OpenAI
from dotenv import load_dotenv

# ✅ 환경 변수 로딩
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_QUESTION_ASSISTANT_ID")

if not OPENAI_API_KEY:
    raise EnvironmentError("❌ OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
if not ASSISTANT_ID:
    raise EnvironmentError("❌ OPENAI_QUESTION_ASSISTANT_ID가 .env에 설정되어 있지 않습니다.")

client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ 질문 생성 함수 (Assistant API 기반, thread 재사용 없음)
def generate_expected_questions(summary_text: str) -> list[str]:
    try:
        summary = summary_text.strip()
        if not summary or "음성이 감지되지 않았습니다" in summary:
            return ["음성이 인식되지 않았거나 내용이 비었습니다."]

        # 1️⃣ Thread 생성 (매번 새로)
        thread = client.beta.threads.create()

        # 2️⃣ 사용자 메시지 등록
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=summary
        )

        # 3️⃣ Run 실행 및 완료 대기 (자동 polling)
        client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # 4️⃣ 응답 메시지 확인
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        content = messages.data[0].content[0].text.value.strip()

        # 5️⃣ 질문 정제 (- 질문 1\n- 질문 2 형태)
        questions = [
            q.strip("-•0123456789. )").strip()
            for q in content.split("\n")
            if q.strip()
        ]

        return questions if questions else ["질문 생성을 실패했습니다."]

    except Exception:
        print("❌ Assistant API 질문 생성 실패:")
        traceback.print_exc()
        return ["질문 생성을 실패했습니다."]
