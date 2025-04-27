// src/api/snapshotService.js
import axios from 'axios'

const BASE_URL = 'https://project2025-backend.onrender.com'

// 🖼️ 스냅샷 업로드 (date, time, text, screenshot_base64 포맷)
export async function uploadSnapshot({ timestamp, transcript, screenshot_base64 }) {
  try {
    const [date, time] = timestamp.split(' ')  // "2025-04-28 15:30:00" → "2025-04-28", "15:30:00"

    const response = await axios.post(`${BASE_URL}/snapshots/snapshots`, {
      date,                  // 날짜 (YYYY-MM-DD)
      time,                  // 시간 (HH:MM:SS)
      text: transcript,      // 텍스트 (변환된 음성 인식 결과)
      screenshot_base64,     // 스크린샷 (Base64)
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
