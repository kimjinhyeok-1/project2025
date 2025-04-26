// src/api/snapshotService.js
import axios from 'axios'

const BASE_URL = 'https://project2025-backend.onrender.com' // ✅ 반드시 HTTPS 주소!

// 🖼️ 스냅샷 업로드
export async function uploadSnapshot({ timestamp, transcript, screenshot_base64 }) {
  try {
    const response = await axios.post(`${BASE_URL}/snapshots`, {
      timestamp,
      transcript,
      screenshot_base64,
    },{
      withCredentials: true  // ✅ 여기에
    })
    console.log("✅ 스냅샷 업로드 성공:", response.data)
    return response.data
  } catch (error) {
    console.error("❌ 스냅샷 업로드 실패:", error.response?.data || error.message || error)
    throw error
  }
}
