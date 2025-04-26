from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.gpt import generate_expected_questions

router = APIRouter()

# 👉 OPTIONS 및 GET 허용 (CORS 프리플라이트 요청 대응)
@router.options("/upload_text_chunk")
@router.get("/upload_text_chunk")
async def dummy_text_route():
    return JSONResponse(content={"message": "This endpoint only accepts POST requests."})

# 👉 텍스트 업로드 처리
@router.post("/upload_text_chunk")
async def upload_text_chunk(request: Request):
    try:
        body = await request.json()
        text = body.get("text", "").strip()

        # 🔥 텍스트 비었는지 체크
        if not text:
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")

        print(f"✅ 받은 텍스트: {text}")

        # GPT 예상 질문 생성
        questions = generate_expected_questions(text)
        print(f"❓ 예상 질문 리스트: {questions}")

        return {
            "transcript": text,
            "questions": questions
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print("❌ 처리 중 예상치 못한 오류:", str(e))
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
