from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import LectureMaterial, Embedding
from app.utils.pdf_parser import extract_text_from_pdf
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import re
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
import tiktoken
import json

# .env 파일에서 OPENAI_API_KEY 불러오기
load_dotenv()

# OpenAI 클라이언트 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

POPPLER_PATH = r"C:\\poppler-24.08.0\\Library\\bin"  # Windows용

def clean_text(text: str) -> str:
    unwanted_symbols = r"[■▶▷\xb7▒▓□※☆★●○•◆◇△▽▲▼]"
    text = re.sub(unwanted_symbols, "", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ ]{2,}", " ", text).strip()
    return text

def extract_text_from_image(image_path: Path) -> str:
    return pytesseract.image_to_string(Image.open(image_path), lang="eng+kor")

def extract_images_from_pdf(pdf_path: Path, output_folder: Path) -> list:
    output_folder.mkdir(parents=True, exist_ok=True)
    try:
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 이미지 변환 오류: {str(e)}")
    image_paths = []
    for i, image in enumerate(images):
        image_path = output_folder / f"page_{i+1}.jpg"
        image.save(image_path, "JPEG")
        image_paths.append(image_path)
    return image_paths

def split_text_into_chunks(text: str, chunk_size=8000, overlap=200):
    encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
    tokens = encoding.encode(text)
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(encoding.decode(chunk))

    return chunks

def generate_embedding(text: str) -> list:
    if len(text) > 10000:
        text = text[:10000]

    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    embedding = response.data[0].embedding

    if not embedding:
        raise ValueError("임베딩 벡터가 비어 있습니다.")
    return embedding

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    file_location = UPLOAD_DIR / file.filename
    with file_location.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""
    extracted_image_texts = []

    if file.filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_location)
        extracted_text = clean_text(extracted_text)
        image_folder = UPLOAD_DIR / "images" / file.filename
        image_paths = extract_images_from_pdf(file_location, image_folder)
        for image_path in image_paths:
            text_from_image = extract_text_from_image(image_path)
            cleaned_image_text = clean_text(text_from_image)
            extracted_image_texts.append(cleaned_image_text)

    full_text = extracted_text + "\n" + "\n".join(extracted_image_texts)

    chunks = split_text_into_chunks(full_text)
    embedding_vectors = [generate_embedding(chunk) for chunk in chunks]

    result = await db.execute(select(LectureMaterial).filter(LectureMaterial.filename == file.filename))
    existing_material = result.scalars().first()

    if existing_material:
        await db.execute(f"DELETE FROM embedding WHERE material_id = {existing_material.id}")
        for i, chunk in enumerate(chunks):
            db.add(Embedding(
                material_id=existing_material.id,
                chunk_index=i,
                content=chunk,
                embedding=json.dumps(embedding_vectors[i])
            ))
        await db.commit()
        return {"message": "기존 파일 갱신 및 임베딩 재저장 완료"}

    else:
        new_material = LectureMaterial(
            filename=file.filename,
            file_path=str(file_location),
            content=full_text
        )
        db.add(new_material)
        await db.commit()

        for i, chunk in enumerate(chunks):
            db.add(Embedding(
                material_id=new_material.id,
                chunk_index=i,
                content=chunk,
                embedding=json.dumps(embedding_vectors[i])
            ))
        await db.commit()

        return {"message": "신규 파일 업로드 및 임베딩 저장 완료"}
