# app/utils/gpt.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_text_with_gpt(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"다음 텍스트를 간결하고 명확하게 요약해줘:\n\n{text}"}
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()
