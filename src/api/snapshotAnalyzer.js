import axios from "axios";

const BASE_URL = "https://project2025-backend.onrender.com/api/evaluate_snapshot";

export async function evaluateSnapshotImportance(transcript) {
  try {
    const response = await axios.get(BASE_URL, {
      params: { q: transcript },
      withCredentials: true
    });

    const reply = response.data.trim();
    return reply.includes("중요");
  } catch (error) {
    console.error("🛑 GPT 판단 API 실패:", error);
    return false;
  }
}
