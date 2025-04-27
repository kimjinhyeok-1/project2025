import os
import asyncio
import openai
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

# 📌 서버 메모리 기반 누적 텍스트 저장소
lecture_texts = {}  # {lecture_id: [chunk1, chunk2, ...]}

# 📌 OpenAI Client 설정
openai_client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# 📌 Assistant ID (.env에 저장된 요약 전용 Assistant)
ASSISTANT_ID = os.getenv("LECTURE_SUMMARY_ASSISTANT_ID")

# ✂️ 텍스트를 블록으로 나누는 함수
def split_text(text: str, max_chars: int = 4000) -> list:
    blocks = []
    while len(text) > max_chars:
        idx = text[:max_chars].rfind('\n')  # 최대한 문단 단위로 자르기
        if idx == -1:
            idx = max_chars
        blocks.append(text[:idx].strip())
        text = text[idx:].strip()
    if text:
        blocks.append(text)
    return blocks

@router.post("/upload_text_chunk")
async def upload_text_chunk(request: Request):
    """텍스트 chunk를 받아서 lecture_id별로 누적 저장"""
    body = await request.json()
    lecture_id = body.get("lecture_id")
    text_chunk = body.get("text", "").strip()

    if not lecture_id or not text_chunk:
        raise HTTPException(status_code=400, detail="lecture_id와 text는 필수입니다.")

    if lecture_id not in lecture_texts:
        lecture_texts[lecture_id] = []
    lecture_texts[lecture_id].append(text_chunk)

    return {"message": "Chunk 저장 완료"}

@router.get("/lecture_text/{lecture_id}")
async def get_lecture_text(lecture_id: str):
    """현재까지 저장된 수업 텍스트 확인"""
    if lecture_id not in lecture_texts:
        raise HTTPException(status_code=404, detail="해당 수업이 존재하지 않습니다.")

    return {
        "lecture_id": lecture_id,
        "texts": lecture_texts[lecture_id],
        "full_text": "\n".join(lecture_texts[lecture_id])
    }

@router.post("/reset_lecture/{lecture_id}")
async def reset_lecture(lecture_id: str):
    """특정 수업 텍스트 초기화"""
    if lecture_id in lecture_texts:
        del lecture_texts[lecture_id]
    return {"message": f"{lecture_id} 수업 데이터 초기화 완료"}

@router.post("/summarize_lecture")
async def summarize_lecture(request: Request):
    """수업 종료 시 전체 텍스트 요약"""
    body = await request.json()
    lecture_id = body.get("lecture_id")

    if not lecture_id:
        raise HTTPException(status_code=400, detail="lecture_id가 필요합니다.")

    chunks = lecture_texts.get(lecture_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="해당 수업 텍스트가 없습니다.")

    # 1. 전체 텍스트 합치기
    full_text = "\n".join(chunks)

    # 2. AI를 이용해 텍스트 클린업
    print("🧹 AI 클린업 시작...")
    cleaned_text = await ai_clean_text(full_text)

    # 3. 텍스트 분할
    text_blocks = split_text(cleaned_text, max_chars=4000)
    print(f"✅ 클린업 후 텍스트 블록 수: {len(text_blocks)}개")

    # 4. 각 블록 요약
    partial_summaries = []
    for idx, block in enumerate(text_blocks):
        print(f"🧩 블록 {idx+1} 요약 중...")
        summary = await summarize_with_assistant(block)
        partial_summaries.append(summary)

    # 5. 부분 요약 합치기
    combined_summary_text = "\n\n".join(partial_summaries)

    # 6. 최종 요약
    print("🧠 최종 요약 시작...")
    final_summary = await summarize_with_assistant(combined_summary_text)

    # ✅ 완료 후 메모리에서 삭제
    del lecture_texts[lecture_id]

    return {
        "lecture_id": lecture_id,
        "summary": final_summary
    }

# 🔥 Assistant로 텍스트 클린업하는 함수
async def ai_clean_text(text: str) -> str:
    thread = await openai_client.beta.threads.create()

    await openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"""
아래 수업 녹취록에서 다음에 해당하는 문장을 모두 제거해 주세요:
- 의미 없는 잡담 (예: 음, 어, 끊기는 말, unrelated small talk)
- 강의 주제와 무관한 대화
- 어색하거나 연결이 안 되는 중간 멘트

오로지 강의 핵심 내용, 수업 설명만 남기고 정리해 주세요.

수업 텍스트:
{text}
        """
    )

    run = await openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    while True:
        run_status = await openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status in ["completed", "failed", "cancelled", "expired"]:
            break
        await asyncio.sleep(1)

    if run_status.status != "completed":
        raise Exception(f"AI 클린업 실패: {run_status.status}")

    messages = await openai_client.beta.threads.messages.list(thread_id=thread.id)
    cleaned_text = messages.data[0].content[0].text.value.strip()

    return cleaned_text

# 🔥 Assistant로 텍스트 요약하는 함수
async def summarize_with_assistant(text: str) -> str:
    thread = await openai_client.beta.threads.create()

    await openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"""
다음은 수업 녹취록 일부입니다. 이 내용을 부드럽고 깔끔하게 요약해 주세요.

수업 텍스트:
{text}
        """
    )

    run = await openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    while True:
        run_status = await openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status in ["completed", "failed", "cancelled", "expired"]:
            break
        await asyncio.sleep(1)

    if run_status.status != "completed":
        raise Exception(f"Run 실패: {run_status.status}")

    messages = await openai_client.beta.threads.messages.list(thread_id=thread.id)
    summary_text = messages.data[0].content[0].text.value.strip()

    return summary_text
