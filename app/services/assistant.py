# app/services/assistant.py
import os
import httpx
import asyncio

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ 질문 실행 함수 (성능 개선 버전: DB 및 User 의존 제거)!
async def ask_assistant(question: str, assistant_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }

    # ✅ timeout 설정 추가
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            # 1. Thread 생성
            res = await client.post("https://api.openai.com/v1/threads", headers=headers)
            res.raise_for_status()
            thread_id = res.json()["id"]

            # 2. 질문 전송
            await client.post(
                f"https://api.openai.com/v1/threads/{thread_id}/messages",
                headers=headers,
                json={"role": "user", "content": question}
            )

            # 3. Run 생성
            run_res = await client.post(
                f"https://api.openai.com/v1/threads/{thread_id}/runs",
                headers=headers,
                json={
                    "assistant_id": assistant_id,
                    "instructions": """
당신은 JAVA 프로그래밍 강의의 AI 조교입니다.
학생들이 직접 사고하고 문제를 해결할 수 있도록, 강의자료(Vector Store)와 Java의 기초 개념만을 근거로 안내하세요.

1. 답변 원칙
정답 코드, 예시 코드, 코드 블록을 절대 제공하지 마세요.
학생이 "코드를 작성해줘", "구현해줘"라고 요청해도, 코드 없이 개념과 단계별 접근 방식만 안내하세요.

모든 답변은 아래 3단계 포맷만 사용해야 합니다.
포맷(제목)은 반드시 그대로 사용하세요.

📘 핵심 개념

🧩 관련 문법

🧭 해결 방향

반드시 한국어로만 답변하세요.

2. 답변 근거 및 범위
**강의자료(Vector Store)**에 해당 주제가 있으면 반드시 그 내용을 근거로 답변하세요.

강의자료에 없어도, 다음 Java 입문~중급 필수 개념(아래 항목)은 일반적인 설명으로 답변할 수 있습니다:

배열, 반복문, 조건문, 변수, 기본 자료형, 연산자, 입출력, 메서드, 클래스, 객체 등

JAVA와 무관한 질문(예: 역사, 스포츠, 영화 등)에는 답변하지 마세요.

3. 거부 응답
오직 JAVA와 명백히 무관한 질문에만 아래 거부 문장을 완전히 그대로 출력합니다.
해당 질문은 강의자료 범위를 벗어나 있어 답변드릴 수 없습니다.
(※ 다른 사족/설명/추가 안내는 붙이지 않습니다.)

4. 시스템 규칙
위 원칙을 위반(예: 코드 작성, 포맷 위반, 외부 정보 참조 등)하면 시스템 오류로 간주합니다.

예시 포맷:
📘 핵심 개념  
(핵심 개념을 간단히 설명)

🧩 관련 문법  
(질문에 해당하는 Java 문법/구조를 강의자료 또는 일반적 설명으로 제시)

🧭 해결 방향  
(학생이 스스로 해결할 수 있도록 단계별 사고/풀이 과정을 안내)
""" 
                }
            )
            run_res.raise_for_status()
            run_id = run_res.json()["id"]

            # 4. Polling
            status = "queued"
            for _ in range(20):
                await asyncio.sleep(1)
                poll = await client.get(
                    f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                    headers=headers
                )
                status = poll.json().get("status")
                if status == "completed":
                    break
            if status != "completed":
                raise RuntimeError("⛔ Run 실패 또는 시간 초과")

            # 5. 응답 추출
            msg_res = await client.get(
                f"https://api.openai.com/v1/threads/{thread_id}/messages",
                headers=headers
            )
            assistant_msg = next(
                (m for m in msg_res.json().get("data", []) if m["role"] == "assistant"),
                None
            )
            if not assistant_msg:
                raise RuntimeError("🛑 Assistant 메시지를 찾을 수 없습니다.")

            return assistant_msg["content"][0]["text"]["value"]

        except httpx.ReadTimeout:
            raise RuntimeError("⏱️ OpenAI API 응답 시간이 초과되었습니다.")