import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_text_with_gpt(transcript: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "다음 텍스트를 간단히 요약해줘."},
            {"role": "user", "content": transcript}
        ],
        temperature=0.5
    )
    return response['choices'][0]['message']['content'].strip()
