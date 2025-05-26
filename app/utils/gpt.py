import os
from openai import AsyncOpenAI
from app.models import Snapshot

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_SUMMARY_ASSISTANT_ID")
BASE_URL = os.getenv("BASE_URL", "")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# 📌 GPT 기반 마크다운 요약 (Assistant API 버전)
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

# ✅ 개선된 스냅샷 STT 요약 함수 (한 문장 요약)
async def summarize_snapshot_transcript(transcript: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 Java 수업 중 교수님의 설명을 요약하는 전문 비서입니다.\n\n"
                    "📌 다음 원칙을 반드시 따르세요:\n"
                    "1. **한 문장으로 요약**하며, **중요 개념이나 비교 설명을 반드시 반영**하세요.\n"
                    "2. '~에 대해 설명했습니다'와 같은 일반적 문장은 피하고, **교수님의 강조점이나 설명 방식을 드러내세요.**\n"
                    "3. 설명 내용이 단순하더라도 임의로 보완하지 말고, **주어진 내용 안에서 가장 핵심만 압축**하세요.\n\n"
                    "✍️ 예시:\n"
                    "- '클래스와 객체의 개념을 구분하며, 객체는 클래스에서 생성되는 실체임을 강조하셨습니다.'\n"
                    "- '값 전달과 참조 전달의 차이를 설명하며, 메모리 관점에서의 동작을 시각적으로 보여주셨습니다.'"
                )
            },
            {"role": "user", "content": transcript}
        ],
        max_tokens=150,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# ✅ 주제별 관련성 높은 스냅샷 1~2개 선택 (is_image=True 필터링은 상위에서 수행)
async def pick_top2_snapshots_by_topic(topic: str, snapshots: list[Snapshot], max_count: int = 2, used_paths: set[str] = set()) -> list[int]:
    valid_snapshots = []
    snapshot_map = []
    for i, snap in enumerate(snapshots):
        if not snap.image_path or snap.image_path in used_paths:
            continue
        valid_snapshots.append(snap)
        snapshot_map.append(i)

    if not valid_snapshots:
        return []

    prompt = (
        f"다음은 강의 주제입니다:\n\n'{topic}'\n\n"
        f"아래는 교수님의 설명 요약입니다:\n\n" +
        "\n".join([f"{i+1}. {snap.text}" for i, snap in enumerate(valid_snapshots)]) +
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
        unique_indices = list(dict.fromkeys([i for i in indices if 0 <= i < len(valid_snapshots)]))
        result = [snapshot_map[i] for i in unique_indices[:max_count]]
        for i in result:
            used_paths.add(snapshots[i].image_path)
        return result
    except Exception:
        return []