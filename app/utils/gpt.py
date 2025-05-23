import os
from openai import AsyncOpenAI
from app.models import Snapshot

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_SUMMARY_ASSISTANT_ID")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def summarize_text_with_gpt(text: str) -> str:
    thread = await client.beta.threads.create()
    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    messages = await client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value.strip()


async def summarize_snapshot_transcript(context: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "다음 문장을 참고하여 교수님이 설명하는 강의내용을 분석하여 사진을 소개하는 말을 작성해주세요."
                )
            },
            {"role": "user", "content": context}
        ],
        max_tokens=60,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

async def pick_top2_snapshots_by_topic(topic: str, snapshots: list[Snapshot]) -> list[int]:
    """
    topic과 관련해 가장 적절한 2개의 snapshot index를 GPT에게 물어봐서 받는다.
    """
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = (
        f"다음은 강의 주제입니다:\n\n'{topic}'\n\n"
        f"그리고 아래는 교수님의 설명 요약입니다:\n\n" +
        "\n".join([f"{i+1}. {snap.summary_text}" for i, snap in enumerate(snapshots)]) +
        "\n\n위 주제와 가장 관련 있는 설명을 2개 선택하세요. "
        "중요하거나 중심이 되는 장면을 고려해 판단하고, 번호만 콤마로 구분해서 출력하세요 (예: 1,4)"
    )

    res = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=20,
    )
    text = res.choices[0].message.content.strip()
    try:
        indices = [int(x.strip()) - 1 for x in text.split(",")]
        return [i for i in indices if 0 <= i < len(snapshots)]
    except Exception:
        return []
