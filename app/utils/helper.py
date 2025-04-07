import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ✅ 새로운 방식

# ✅ 정답 요구 감지
def contains_answer_request(text: str) -> bool:
    keywords = ["정답", "답좀", "코드 다", "해줘", "답 알려"]
    return any(k in (text or "") for k in keywords)

# ✅ GPT 응답 생성 함수 (통합 content 기반)
async def generate_gpt_response(assignment_description, sample_answer, full_content):
    # 정답 요구 차단
    if contains_answer_request(full_content or ""):
        return "한 번 차근차근 해볼까요? 궁금한 부분이나 막힌 부분이 있다면 도와드릴게요!"

    system_prompt = (
        "너는 학생의 과제에 대해 도와주는 AI야.\n"
        "- 절대 정답을 알려주지 마.\n"
        "- 대신, 개념 설명, 코드 오류 디버깅, 힌트만 제공해.\n"
        "- 정답 유도하는 질문은 모두 격려 메시지로 응답해."
    )

    user_prompt = (
        f"[과제 설명]\n{assignment_description}\n\n"
        f"[예시 코드]\n{sample_answer or '없음'}\n\n"
        f"[학생 질문 및 코드]\n{full_content}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT ERROR] {str(e)}")
        return "GPT 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."
