import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assignment_qna_assistant_id = os.getenv("ASSIGNMENT_QNA_ASSISTANT_ID")

# ✅ Q&A용 Thread 가져오기 또는 생성
async def create_or_get_qna_thread(db_session, assignment_id: int, student_id: int):
    from app.models import AssignmentThread

    # DB에서 기존 Thread 검색
    result = await db_session.execute(
        select(AssignmentThread).where(
            AssignmentThread.assignment_id == assignment_id,
            AssignmentThread.student_id == student_id
        )
    )
    thread = result.scalar_one_or_none()

    if thread:
        return thread.thread_id

    # 없다면 새 Thread 생성
    new_thread = await client.beta.threads.create()

    # DB에 저장
    new_assignment_thread = AssignmentThread(
        assignment_id=assignment_id,
        student_id=student_id,
        thread_id=new_thread.id
    )
    db_session.add(new_assignment_thread)
    await db_session.commit()

    return new_thread.id


# ✅ 학생 질문에 대해 Assistant 답변 받기
async def ask_question_to_gpt(thread_id: str, question: str) -> str:
    assistant_id = assignment_qna_assistant_id  

    # 학생 질문 추가
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )

    # 답변 생성 (gpt-4o 스타일 프롬프트 자동 반영)
    run = await client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="문단을 자연스럽게 구분하고, 필요한 경우 코드 블록을 사용하여 깔끔한 스타일로 답변하세요. 답변 마지막에는 추가 질문을 유도하는 문장을 자연스럽게 작성하세요. 과제 정답을 직접 제공하지 말고 방향성을 중심으로 설명하세요."
    )

    # 답변 대기 (simple polling)
    while True:
        run_status = await client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break
        elif run_status.status in ("failed", "expired"):
            raise Exception("GPT 답변 생성 실패")

    # 답변 가져오기
    messages = await client.beta.threads.messages.list(thread_id=thread_id)
    # 가장 최근 assistant 답변 찾기
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            return msg.content[0].text.value.strip()

    raise Exception("Assistant 답변을 찾을 수 없습니다.")
