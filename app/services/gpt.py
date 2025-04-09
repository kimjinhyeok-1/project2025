import os
import openai
from dotenv import load_dotenv

# .env 파일에서 OPENAI_API_KEY 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_expected_questions(summary_text: str, num_questions: int = 3) -> list:
    prompt = (
        "당신은 수업을 듣고 있는 학생들을 돕는 AI입니다.\n"
        "다음 강의 요약을 읽고, 학생들이 궁금해할 만한 질문을 만들어주세요.\n\n"
        f"[강의 요약]\n{summary_text}\n\n"
        f"{num_questions}개의 질문을 자연스럽고 구체적으로 리스트 형식으로 작성해주세요.\n"
        "예: - 질문 1\n- 질문 2\n..."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 여기서 gpt-3.5-turbo 사용
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    content = response['choices'][0]['message']['content']

    # 응답에서 질문만 리스트로 정리
    questions = [
        q.strip("-•0123456789. ").strip()
        for q in content.strip().split("\n")
        if q.strip()
    ]

    return questions
