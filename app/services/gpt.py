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

def generate_expected_questions(summary_text: str) -> list[str]:
    """
    Assistant API를 사용하여 입력 텍스트 기반 예상 질문 목록을 반환합니다.
    오류 발생 시 안내 메시지 1개만 포함한 리스트를 반환합니다.
    """
    summary = summary_text.strip()
    if not summary or "음성이 감지되지 않았습니다" in summary:
        return ["음성이 인식되지 않았거나 내용이 비었습니다."]

    try:
        # 1. 새 thread 생성 및 메시지 등록
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=summary
        )

        # 2. Assistant run 실행 및 완료 대기
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # 3. 응답 메시지 추출
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        # 최신 assistant 응답 찾기
        assistant_reply = next(
            (msg for msg in messages.data if msg.role == "assistant"),
            messages.data[0] if messages.data else None
        )

        if not assistant_reply or not assistant_reply.content:
            return ["질문 생성을 실패했습니다. (빈 응답)"]

        raw_text = assistant_reply.content[0].text.value.strip()

        # 4. 질문 파싱 (번호, 불릿 제거 등)
        questions = [
            q.strip("•-–—0123456789). ").strip()
            for q in raw_text.split("\n")
            if q.strip()
        ]
        if not questions:
            return ["질문 생성을 실패했습니다."]
        return questions

    except Exception:
        traceback.print_exc()
        return ["질문 생성을 실패했습니다."]

