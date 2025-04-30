import os
import httpx
import asyncio
import time

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def ask_assistant(question: str, thread_id: str, assistant_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2",
        "Content-Type": "application/json"
    }

    # 🔹 Run 생성
    payload = {
        "assistant_id": assistant_id,
        "instructions": "학생 질문에 친절하게 답해주세요."
    }

    print(f"\n🟢 [Run 생성 요청]")
    print(f"thread_id: {thread_id}")
    print(f"payload: {payload}")

    async with httpx.AsyncClient() as client:
        run_res = await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=headers,
            json=payload
        )

    print(f"📡 응답 상태코드: {run_res.status_code}")
    try:
        json_data = run_res.json()
        print(f"📄 응답 본문: {json_data}")
    except Exception as e:
        print(f"❌ JSON 파싱 실패: {e}")
        raise RuntimeError(f"OpenAI 응답 파싱 오류: {run_res.text}")

    if run_res.status_code != 200:
        raise RuntimeError(f"❌ Run 생성 실패: {json_data}")
    if "id" not in json_data:
        raise RuntimeError(f"❌ 응답에 'id' 없음: {json_data}")

    run_id = json_data["id"]
    print(f"✅ Run 생성 완료: {run_id}")

    # 🔁 Run 상태 polling (최대 20초)
    run_status = "queued"
    timeout = 20
    elapsed = 0

    async with httpx.AsyncClient() as client:
        while run_status not in ("completed", "failed", "cancelled"):
            await asyncio.sleep(1)
            elapsed += 1

            poll_res = await client.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers=headers
            )

            poll_data = poll_res.json()
            run_status = poll_data.get("status", "unknown")
            print(f"⏳ [{elapsed}s] Run 상태: {run_status}")

            if elapsed >= timeout:
                raise RuntimeError(f"⛔ Run 응답 대기 시간 초과: {poll_data}")

        if run_status != "completed":
            raise RuntimeError(f"❌ Run 실패 또는 중단됨: {poll_data}")

    # 📥 최종 메시지 가져오기
    async with httpx.AsyncClient() as client:
        msg_res = await client.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=headers
        )

    msg_data = msg_res.json()
    print(f"📩 메시지 응답: {msg_data}")

    # 🔍 마지막 Assistant 메시지 추출
    try:
        messages = msg_data["data"]
        assistant_msg = next(
            (m for m in messages if m["role"] == "assistant"), None
        )
        if not assistant_msg:
            raise RuntimeError("🛑 Assistant 메시지를 찾을 수 없습니다.")

        answer = assistant_msg["content"][0]["text"]["value"]
        print(f"✅ 최종 답변: {answer}")
        return answer

    except Exception as e:
        raise RuntimeError(f"❌ 메시지 파싱 오류: {e} / 데이터: {msg_data}")
