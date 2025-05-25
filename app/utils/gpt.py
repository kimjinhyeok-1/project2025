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
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "다음 문장을 참고하여 교수님의 설명 내용을 한 문장으로 요약하세요. "
                    "단순히 '~를 설명한 장면입니다'처럼 일반적인 말투로 끝내지 말고, "
                    "교수님의 설명 방식이나 강조한 점을 구체적으로 포함하세요. "
                    "예: '교수님은 문자열과 기본 타입의 차이를 설명하며, 문자열이 실제로는 레퍼런스 타입임을 강조하셨습니다.'"
                )
            },
            {"role": "user", "content": context}
        ],
        max_tokens=70,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

async def pick_top2_snapshots_by_topic(topic: str, snapshots: list[Snapshot], max_count: int = 2) -> list[int]:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = (
        f"다음은 강의 주제입니다:\n\n'{topic}'\n\n"
        f"아래는 교수님의 설명 요약입니다:\n\n" +
        "\n".join([f"{i+1}. {snap.summary_text}" for i, snap in enumerate(snapshots)]) +
        f"\n\n위 주제와 가장 관련 있는 설명을 1개 ~ 2개 선택하세요. "
        f"중복되는 경우는 1개만 선택하고, 번호만 콤마 없이 한 줄에 출력하세요 (예: 1 또는 1,2)"
    )

    res = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=20,
    )
    text = res.choices[0].message.content.strip()
    try:
        indices = [int(x.strip()) - 1 for x in text.split(",") if x.strip().isdigit()]
        unique_indices = list(dict.fromkeys([i for i in indices if 0 <= i < len(snapshots)]))
        return unique_indices[:max_count]  # 최대 max_count개
    except Exception:
        return []