// src/api/snapshotService.js
import axios from 'axios'

const BASE_URL = 'https://project2025-backend.onrender.com'

function getFormattedTimestamp() {
  const now = new Date();
  return `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, "0")}-${now.getDate().toString().padStart(2, "0")} ${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
}

// 🖼️ 스크린샷 Base64 캡처
async function captureScreenshot(displayStream) {
  if (!displayStream) return "";

  const track = displayStream.getVideoTracks()[0];
  const imageCapture = new ImageCapture(track);
  const bitmap = await imageCapture.grabFrame();

  const canvas = document.createElement("canvas");
  canvas.width = bitmap.width;
  canvas.height = bitmap.height;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(bitmap, 0, 0);
  return canvas.toDataURL("image/png");
}

// 📤 스냅샷 업로드
async function uploadSnapshot({ transcript, screenshot_base64 = "" }) {
  if (!transcript || transcript.trim() === "") {
    console.error("❌ transcript가 비어있어서 업로드 중단");
    return;
  }

  const timestamp = getFormattedTimestamp();

  try {
    const response = await axios.post(`${BASE_URL}/snapshots/snapshots`, {
      timestamp,
      transcript,
      screenshot_base64,
    }, {
      withCredentials: true
    });

    console.log("✅ 스냅샷 업로드 성공:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 스냅샷 업로드 실패:", error.response?.data || error.message || error);
    throw error;
  }
}

export { uploadSnapshot, captureScreenshot }
