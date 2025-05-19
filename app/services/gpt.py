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


# ✅ 질문 생성 함수 (Assistant API 기반)
def generate_expected_questions(summary_text: str) -> list[str]:
    summary = summary_text.strip()

    if not summary or "음성이 감지되지 않았습니다" in summary:
        return ["음성이 인식되지 않았거나 내용이 비었습니다."]

    try:
        # 1️⃣ 새 thread 생성
        thread = client.beta.threads.create()

        # 2️⃣ 사용자 메시지 등록
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=summary
        )

        # 3️⃣ Assistant run 실행 + 완료 대기 (자동 polling)
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # 4️⃣ 응답 메시지 추출
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # 가장 마지막 메시지 (보통 assistant 응답이 최신)
        assistant_reply = next(
            (msg for msg in messages.data if msg.role == "assistant"),
            messages.data[0] if messages.data else None
        )

        if not assistant_reply or not assistant_reply.content:
            return ["질문 생성을 실패했습니다. (빈 응답)"]

        raw_text = assistant_reply.content[0].text.value.strip()

        # 5️⃣ 질문 파싱 및 정제
        questions = [
            q.strip("•-–—0123456789). ").strip()
            for q in raw_text.split("\n")
            if q.strip()
        ]

        return questions if questions else ["질문 생성을 실패했습니다."]

    except Exception as e:
        print("❌ Assistant API 질문 생성 실패:")
        traceback.print_exc()
        return ["질문 생성을 실패했습니다."]
