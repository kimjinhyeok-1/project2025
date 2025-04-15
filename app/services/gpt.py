import os
from openai import OpenAI
from dotenv import load_dotenv

# ✅ 환경 변수 로딩
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 예상 질문 생성 함수
def generate_expected_questions(summary_text: str, num_questions: int = 3) -> list:
    if not summary_text.strip() or "음성이 감지되지 않았습니다" in summary_text:
        return ["음성이 인식되지 않았거나 내용이 비었습니다."]

    prompt = (
        "당신은 학생들을 돕는 AI입니다.\n"
        "다음 강의 내용을 읽고, 학생들이 궁금해할 만한 질문을 만들어주세요.\n\n"
        f"[강의 요약]\n{summary_text}\n\n"
        f"{num_questions}개의 질문을 자연스럽고 구체적으로 리스트 형식으로 작성해주세요.\n"
        "예: - 질문 1\n- 질문 2\n..."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        content = response.choices[0].message.content
        questions = [
            q.strip("-•0123456789. ").strip()
            for q in content.strip().split("\n") if q.strip()
        ]
        return questions

    except Exception as e:
        print("❌ GPT 질문 생성 실패:", e)
        return ["질문 생성을 실패했습니다."]
