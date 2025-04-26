import os
import aiohttp
from dotenv import load_dotenv

# ✅ 환경 변수 로딩
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError("❌ OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")

# ✅ OpenAI Whisper API 호출 함수
async def transcribe_with_whisper(file_path: str) -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    data = {
        "model": "whisper-1",   # OpenAI Whisper 모델
        "language": "ko"        # 한국어 지정
    }

    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as f:
                form_data = aiohttp.FormData()
                form_data.add_field('file', f, filename=os.path.basename(file_path))
                form_data.add_field('model', 'whisper-1')
                form_data.add_field('language', 'ko')

                async with session.post(url, headers=headers, data=form_data) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        print(f"❌ OpenAI Whisper API 오류: {text}")
                        return "음성을 변환하지 못했습니다."

                    response_json = await resp.json()
                    text_result = response_json.get("text", "").strip()

                    if not text_result:
                        print("⚠️ 변환 결과가 비어 있습니다.")
                        return "음성을 변환하지 못했습니다."

                    print("📝 OpenAI Whisper 변환 결과:", text_result)
                    return text_result

    except Exception as e:
        print("❌ OpenAI Whisper API 호출 실패:", e)
        return "음성을 변환하지 못했습니다."
