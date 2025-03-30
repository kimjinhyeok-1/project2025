from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import LectureMaterial, Quiz
import openai
import os
import json

router = APIRouter()

# 최신 OpenAI 클라이언트
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post("/generate_quiz/{material_id}")
async def generate_quiz(material_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LectureMaterial).filter(LectureMaterial.id == material_id))
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="Lecture material not found.")

    truncated_content = material.content[:5000]

    prompt = f"""
    다음 강의자료를 기반으로 학생을 위한 객관식 퀴즈 3개를 만들어줘. 
    각 퀴즈는 보기 4개와 정답을 포함해줘. JSON 형식으로 반환해줘.

    예시 형식:
    [
      {{
        "question": "질문 내용",
        "options": ["보기1", "보기2", "보기3", "보기4"],
        "answer": "정답 보기"
      }}
    ]

    강의자료:
    {truncated_content}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )

        quiz_text = response.choices[0].message.content.strip()

        try:
            quiz_data = json.loads(quiz_text)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"GPT 응답을 JSON으로 파싱할 수 없습니다. 원본 응답:\n{quiz_text}"
            )

        for quiz in quiz_data:
            db.add(Quiz(
                question=quiz.get("question"),
                options=json.dumps(quiz.get("options")),
                answer=quiz.get("answer"),
                material_id=material_id
            ))
        await db.commit()

        return {"message": "퀴즈가 성공적으로 생성되었습니다.", "quiz_count": len(quiz_data)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ 새로 추가된 부분: filename 기반 퀴즈 생성
@router.post("/generate_quiz_by_filename")
async def generate_quiz_by_filename(filename: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LectureMaterial).filter(LectureMaterial.filename == filename))
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="해당 파일명을 가진 강의자료를 찾을 수 없습니다.")

    return await generate_quiz(material.id, db)


# ✅ 선택사항: 사용자에게 보여줄 filename 리스트 반환
@router.get("/list_filenames")
async def list_filenames(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LectureMaterial.filename))
    filenames = [row[0] for row in result.fetchall()]
    return filenames
