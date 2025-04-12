# app/routes/vad.py

from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import time

router = APIRouter()

UPLOAD_DIR = "temp/audio_chunks"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_audio_chunk")
async def upload_audio_chunk(file: UploadFile = File(...)):
    try:
        filename = f"chunk_{int(time.time())}.webm"
        save_path = os.path.join(UPLOAD_DIR, filename)
        contents = await file.read()

        with open(save_path, "wb") as f:
            f.write(contents)

        print(f"✅ 음성 chunk 저장 완료: {save_path}")
        return {"message": "Chunk received", "filename": filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
