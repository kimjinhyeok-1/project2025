import os
import traceback
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_QUESTION_ASSISTANT_ID")

if not OPENAI_API_KEY or not ASSISTANT_ID:
    raise EnvironmentError("❌ .env에 OPENAI_API_KEY 또는 ASSISTANT_ID가 없습니다.")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_expected_questions(summary_text: str) -> list[str]:
    summary = summary_text.strip()
    if not summary or "음성이 감지되지 않았습니다" in summary:
        return ["음성이 인식되지 않았거나 내용이 없습니다."]

    try:
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=summary
        )
        client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        reply = next((m for m in messages.data if m.role == "assistant"), None)

        if not reply or not reply.content:
            return ["질문 생성을 실패했습니다."]

        raw_text = reply.content[0].text.value.strip()
        questions = [
            q.strip("•-–—0123456789). ").strip()
            for q in raw_text.split("\n")
            if q.strip()
        ]
        return questions or ["질문 생성을 실패했습니다."]

    except Exception:
        traceback.print_exc()
        return ["질문 생성을 실패했습니다."]