from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Snapshot
import os
import base64
import uuid
from datetime import datetime

from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# OpenAI 클라이언트 초기화
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

IMAGE_DIR = "tmp/snapshots"
FULL_IMAGE_DIR = os.path.join("static", IMAGE_DIR)
os.makedirs(FULL_IMAGE_DIR, exist_ok=True)

TEXT_LOG_DIR = "data"
os.makedirs(TEXT_LOG_DIR, exist_ok=True)


class SnapshotRequest(BaseModel):
    timestamp: str
    transcript: str
    screenshot_base64: str


@router.post("/snapshots")
async def upload_snapshot(data: SnapshotRequest, db: AsyncSession = Depends(get_db)):
    # 1) 요청 데이터 파싱
@router.post("/snapshots")
async def upload_snapshot(data: SnapshotRequest, db: AsyncSession = Depends(get_db)):
    timestamp = data.timestamp
    text = data.transcript
    image_data = data.screenshot_base64
    lecture_id = 1

    try:
        dt = datetime.strptime(data.timestamp, "%Y-%m-%d %H:%M:%S")
        date_group = dt.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="timestamp 형식 오류")

    # 2) 이미지 디코딩 및 저장
    try:
        _, encoded = data.screenshot_base64.split(",", 1) if "," in data.screenshot_base64 else ("", data.screenshot_base64)
        image_bytes = base64.b64decode(encoded)
        filename = f"{uuid.uuid4().hex}.png"
        save_path = os.path.join(FULL_IMAGE_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(image_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="이미지 디코딩 또는 저장 실패")

    relative_url = f"/static/{IMAGE_DIR}/{filename}"
    absolute_url = f"https://project2025-backend.onrender.com{relative_url}"

    # 3) 텍스트 로그 누적 저장
    lecture_id = 1  # 동적 처리 필요 시 수정
    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    try:
        with open(text_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{dt:%Y-%m-%d %H:%M:%S} - {data.transcript}\n")
    except Exception:
        # 로깅 실패 시에도 API 차단하지 않음
        pass

        _, encoded = image_data.split(",", 1) if "," in image_data else ("", image_data)
        image_bytes = base64.b64decode(encoded)
    except Exception:
        raise HTTPException(status_code=400, detail="이미지 디코딩 실패")

    filename = f"{uuid.uuid4().hex}.png"
    save_path = os.path.join(FULL_IMAGE_DIR, filename)
    relative_url = f"/static/{IMAGE_DIR}/{filename}"
    absolute_url = f"https://project2025-backend.onrender.com{relative_url}"

    with open(save_path, "wb") as f:
        f.write(image_bytes)

    text_log_path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    with open(text_log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{dt.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")

    # 4) DB 저장
    snapshot = Snapshot(
        lecture_id=lecture_id,
        date=date_group,
        time=dt.strftime("%H:%M:%S"),
        text=data.transcript,
        image_path=relative_url
    )
    db.add(snapshot)
    await db.commit()

    return {
        "message": "스냅샷 저장 완료",
        "lecture_id": lecture_id,
        "date": date_group,
        "time": snapshot.time,
        "text": data.transcript,
        "image_url": absolute_url
    }


# GPT 기반 Markdown 요약 함수
async def summarize_text_with_gpt(text: str) -> str:
    system_msg = {
        "role": "system",
        "content": (
            "당신은 ‘교수의 강의 마무리 리마인더’를 작성하는 역할입니다.\n"
            "• 이번 강의에서 등장한 핵심 키워드 5개를 추출하고,\n"
            "• 각 키워드를 ### 헤딩으로, 간단한 설명을 bullet으로 작성하세요. (마크다운 형식)"
        )
    }
    user_msg = {
        "role": "user",
        "content": f"강의 로그 (최대 3000자):\n```text\n{text[:3000]}\n```"
    }
    res = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_msg, user_msg],
    )
# GPT 요약 함수
async def summarize_text_with_gpt(text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 ‘교수의 강의 마무리 리마인더’를 작성하는 역할입니다.\n"
                "• 이번 강의에서 등장한 핵심 키워드 5개를 추출하고,\n"
                "• 각 키워드를 ### 헤딩으로, 간단한 설명을 bullet으로 작성하세요. (마크다운 형식)"
            )
        },
        {
            "role": "user",
            "content": f"강의 로그:\n```text\n{text[:3000]}\n```\n"
        }
    ]
    res = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=800,
    )
    return res.choices[0].message.content.strip()


class SummaryResponse(BaseModel):
    lecture_id: int
    summary: str


@router.get("/generate_markdown_summary", response_model=SummaryResponse)
async def generate_markdown_summary(lecture_id: int = 1):
    # 텍스트 로그 불러오기
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 없음")
    text = open(path, "r", encoding="utf-8").read()

    # Markdown 요약 생성
    markdown = await summarize_text_with_gpt(text)
    return SummaryResponse(lecture_id=lecture_id, summary=markdown)



@router.get("/generate_markdown_summary")
async def generate_markdown_summary(lecture_id: int = 1):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 없음")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    markdown = await summarize_text_with_gpt(text)
    return {"lecture_id": lecture_id, "markdown": markdown}


@router.get("/generate_question_summary")
async def generate_question_summary(lecture_id: int = 1):
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 없음")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    summary = await summarize_text_with_gpt(text)
    return {"lecture_id": lecture_id, "summary": summary}


# ✅ 최종 API: /lecture_summary
@router.get("/lecture_summary")
async def get_lecture_summary(lecture_id: int = 1, db: AsyncSession = Depends(get_db)):
    # 1. 전체 텍스트 요약 받아오기
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="텍스트 파일 없음")

    with open(path, "r", encoding="utf-8") as f:
        full_text = f.read()

@router.get("/generate_question_summary", response_model=SummaryResponse)
async def generate_question_summary(lecture_id: int = 1):
    # 기존 텍스트 요약과 동일하게 처리
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="요약할 텍스트 없음")
    text = open(path, "r", encoding="utf-8").read()
    summary = await summarize_text_with_gpt(text)
    return SummaryResponse(lecture_id=lecture_id, summary=summary)


# ✅ 최종 API: 강의별 요약 + 관련 스냅샷 하이라이트
class LectureTopicHighlight(BaseModel):
    topic: str
    summary: str
    highlights: list


@router.get("/lecture_summary", response_model=list[LectureTopicHighlight])
async def get_lecture_summary(lecture_id: int = 1, db: AsyncSession = Depends(get_db)):
    # 1) 강의 로그 불러오기
    path = os.path.join(TEXT_LOG_DIR, f"lecture_{lecture_id}.txt")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="텍스트 파일 없음")
    full_text = open(path, "r", encoding="utf-8").read()

    # 2) Markdown 요약 생성
    markdown = await summarize_text_with_gpt(full_text)

    # 3) Markdown에서 주제별 키워드와 요약 추출
    topics = []
    current_topic = None
    for line in markdown.splitlines():
        if line.startswith("### "):
            current_topic = line.removeprefix("### ").strip()
        elif line.startswith("-") and current_topic:
            summary_line = line.lstrip("- ").strip()
            topics.append({"topic": current_topic, "summary": summary_line})
            current_topic = None

    if not topics:
        raise HTTPException(status_code=204, detail="추출된 토픽 없음")

    # 4) DB에서 스냅샷 불러오기
    result = await db.execute(select(Snapshot).where(Snapshot.lecture_id == lecture_id))
    snapshots = result.scalars().all()
    if not snapshots:
        raise HTTPException(status_code=404, detail="스냅샷 없음")
    texts = [s.text for s in snapshots]
    data_urls = [f"https://project2025-backend.onrender.com{s.image_path}" for s in snapshots]

    # 5) 임베딩 및 유사도 계산
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    topic_embs = model.encode([t["topic"] for t in topics])
    snap_embs = model.encode(texts)

    response = []
    for idx, t in enumerate(topics):
        sims = cosine_similarity([topic_embs[idx]], snap_embs)[0]
        top_idxs = sims.argsort()[-3:][::-1]
        highlights = [
            {"text": texts[i], "image_url": data_urls[i]}
            for i in top_idxs
        ]
        response.append({
            "topic": t["topic"],
            "summary": t["summary"],
            "highlights": highlights
        })

    return response
# 2. Markdown에서 주제 추출
    topics = []
    current_topic = ""
    for line in markdown.splitlines():
        if line.startswith("### "):
            current_topic = line.replace("### ", "").strip()
        elif line.startswith("-") and current_topic:
            topics.append({"topic": current_topic, "summary": line.replace("-", "").strip()})
            current_topic = ""

    # 3. DB에서 스냅샷 문장 불러오기
    result = await db.execute(select(Snapshot).where(Snapshot.lecture_id == lecture_id))
    snapshot_rows = result.scalars().all()
    if not snapshot_rows:
        raise HTTPException(status_code=404, detail="스냅샷 없음")

    snapshot_texts = [s.text for s in snapshot_rows]
    snapshot_data = [{"text": s.text, "image_url": f"https://project2025-backend.onrender.com{s.image_path}"} for s in snapshot_rows]

    # 4. 임베딩 유사도 계산
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    topic_embeddings = model.encode([t["topic"] for t in topics])
    snapshot_embeddings = model.encode(snapshot_texts)

    result = []
    for idx, topic in enumerate(topics):
        sims = cosine_similarity([topic_embeddings[idx]], snapshot_embeddings)[0]
        top_indices = sims.argsort()[-3:][::-1]
        highlights = [snapshot_data[i] for i in top_indices]
        result.append({
            "topic": topic["topic"],
            "summary": topic["summary"],
            "highlights": highlights
        })

    return result
