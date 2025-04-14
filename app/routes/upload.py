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
from openai import OpenAI
import tiktoken
import json
import hashlib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
POPPLER_PATH = r"C:\\poppler-24.08.0\\Library\\bin"

encoding = tiktoken.encoding_for_model("text-embedding-3-small")

# ====== 전처리 및 보조 함수들 ======
def clean_text(text: str) -> str:
    unwanted_symbols = r"[■▶▷\xb7▒▓□※☆★●○•◆◇△▽▲]"
    text = re.sub(unwanted_symbols, "", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ ]{2,}", " ", text).strip()
    return text

def extract_text_from_image(image_path: Path) -> str:
    return pytesseract.image_to_string(Image.open(image_path), lang="eng+kor")

def extract_images_from_pdf(pdf_path: Path, output_folder: Path) -> list:
    output_folder.mkdir(parents=True, exist_ok=True)
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    image_paths = []
    for i, image in enumerate(images):
        image_path = output_folder / f"page_{i+1}.jpg"
        image.save(image_path, "JPEG")
        image_paths.append(image_path)
    return image_paths

def split_text_into_chunks(text: str, chunk_size=500, overlap=50):
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(encoding.decode(chunk))
    return chunks

def hash_chunk(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def generate_embedding(text: str) -> list:
    if len(text) > 10000:
        text = text[:10000]
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    embedding = response.data[0].embedding
    if not embedding:
        raise ValueError("임베딩 벡터가 비어 있음")
    return embedding

def cosine_deduplicate(chunks: list[str], threshold=0.95):
    embeddings = [generate_embedding(c) for c in chunks]
    keep = []
    used = set()

    for i in range(len(embeddings)):
        if i in used:
            continue
        keep.append((chunks[i], embeddings[i]))
        for j in range(i + 1, len(embeddings)):
            if j in used:
                continue
            sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
            if sim >= threshold:
                used.add(j)
    return keep

# ========== 메인 업로드 API ==========
@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    file_location = UPLOAD_DIR / file.filename
    with file_location.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 텍스트 추출 (PDF + 이미지)
    extracted_text = ""
    extracted_image_texts = []

    if file.filename.endswith(".pdf"):
        extracted_text = clean_text(extract_text_from_pdf(file_location))
        image_folder = UPLOAD_DIR / "images" / file.filename
        image_paths = extract_images_from_pdf(file_location, image_folder)
        for image_path in image_paths:
            img_text = extract_text_from_image(image_path)
            cleaned = clean_text(img_text)
            if len(cleaned.strip()) > 30:
                extracted_image_texts.append(cleaned)

    full_text = extracted_text + "\n" + "\n".join(extracted_image_texts)
    raw_chunks = split_text_into_chunks(full_text)

    # ===== 1차: 완전 중복 제거 (해시 기반) =====
    seen_hashes = set()
    unique_chunks = []
    for c in raw_chunks:
        if len(c.strip()) < 30:
            continue
        h = hash_chunk(c)
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique_chunks.append(c)

    # ===== 2차: 유사 중복 제거 (cosine) =====
    final_chunks_with_vecs = cosine_deduplicate(unique_chunks, threshold=0.95)

    # DB 저장 (기존 파일이면 재저장)
    result = await db.execute(select(LectureMaterial).filter_by(filename=file.filename))
    existing_material = result.scalars().first()

    if existing_material:
        old_embeddings = await db.execute(select(Embedding).where(Embedding.material_id == existing_material.id))
        for e in old_embeddings.scalars():
            await db.delete(e)

        for i, (chunk, vec) in enumerate(final_chunks_with_vecs):
            db.add(Embedding(
                material_id=existing_material.id,
                chunk_index=i,
                content=chunk,
                embedding=json.dumps(vec)
            ))
        await db.commit()
        return {"message": "기존 파일 갱신 및 중복 제거 후 임베딩 저장 완료"}

    else:
        new_material = LectureMaterial(
            filename=file.filename,
            file_path=str(file_location),
            content=full_text
        )
        db.add(new_material)
        await db.commit()

        for i, (chunk, vec) in enumerate(final_chunks_with_vecs):
            db.add(Embedding(
                material_id=new_material.id,
                chunk_index=i,
                content=chunk,
                embedding=json.dumps(vec)
            ))
        await db.commit()

        return {"message": "신규 파일 업로드 및 중복 제거 후 임베딩 저장 완료"}
