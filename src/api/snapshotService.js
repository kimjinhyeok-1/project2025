// src/api/snapshotService.js
import axios from 'axios'

const BASE_URL = 'https://project2025-backend.onrender.com'

// 🖼️ 스냅샷 업로드 (timestamp, transcript, screenshot_base64)
export async function uploadSnapshot({ timestamp, transcript, screenshot_base64 }) {
  try {
    const response = await axios.post(`${BASE_URL}/snapshots`, {
      timestamp,            // (예: "2025-04-27 16:02:11")
      transcript,           // (학생이 말한 텍스트)
      screenshot_base64,    // (Base64 인코딩된 이미지 데이터)
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
