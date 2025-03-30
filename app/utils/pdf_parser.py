import fitz  # PyMuPDF
from pathlib import Path

def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    try:
        with fitz.open(str(pdf_path)) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        return f"PDF 파싱 중 오류 발생: {str(e)}"
    
    return text.strip()
