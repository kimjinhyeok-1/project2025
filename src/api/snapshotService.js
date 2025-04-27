// src/api/snapshotService.js
import axios from 'axios'

const BASE_URL = 'https://project2025-backend.onrender.com'

export async function uploadSnapshot({ timestamp, transcript, screenshot_base64 }) {
  try {
    const [date, time] = timestamp.split(' ')  // timestamp를 "2025-04-28 15:30:00" → ["2025-04-28", "15:30:00"]로 나눔

    const response = await axios.post(`${BASE_URL}/snapshots/snapshots`, {
      date,                  // YYYY-MM-DD
      time,                  // HH:MM:SS
      text: transcript,      // 필드명 변경
      screenshot_base64,     // 그대로
    }, {
      withCredentials: true
    })

    console.log("✅ 스냅샷 업로드 성공:", response.data)
    return response.data
  } catch (error) {
    console.error("❌ 스냅샷 업로드 실패:", error.response?.data || error.message || error)
    throw error
  }
}
