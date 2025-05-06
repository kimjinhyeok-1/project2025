import axios from 'axios';

const BASE_URL = 'https://project2025-backend.onrender.com';

// 🕒 현재 시간 포맷: yyyy-MM-dd HH:mm:ss
function getFormattedTimestamp() {
  const now = new Date();
  return `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, "0")}-${now.getDate().toString().padStart(2, "0")} ${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
}

// 🖼️ 스크린샷 Base64 캡처 (displayStream 이용)
async function captureScreenshot(displayStream) {
  if (!displayStream) return "";

  try {
    const track = displayStream.getVideoTracks()[0];
    const imageCapture = new ImageCapture(track);
    const bitmap = await imageCapture.grabFrame();

    const canvas = document.createElement("canvas");
    canvas.width = bitmap.width;
    canvas.height = bitmap.height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(bitmap, 0, 0);

    return canvas.toDataURL("image/png");
  } catch (err) {
    console.error("❌ 이미지 캡처 실패:", err);
    return "";
  }
}

// 📤 스냅샷 업로드
async function uploadSnapshot({ transcript = "", screenshot_base64 = "" }) {
  const cleanedTranscript = transcript.trim();

  const timestamp = getFormattedTimestamp();

  try {
    const response = await axios.post(`${BASE_URL}/snapshots/snapshots`, {
      timestamp,
      transcript: cleanedTranscript,
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

// 📥 전체 요약 목록 조회
async function getSummaries() {
  try {
    const response = await axios.get(`${BASE_URL}/summaries`);
    console.log("📥 요약 목록 수신 완료:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 요약 목록 요청 실패:", error);
    throw error;
  }
}

// 📄 특정 요약 상세 조회
async function getSummaryById(id) {
  try {
    const response = await axios.get(`${BASE_URL}/summaries/${id}`);
    console.log("📄 요약 상세 수신 완료:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 요약 상세 요청 실패:", error);
    throw error;
  }
}

export {
  uploadSnapshot,
  captureScreenshot,
  getSummaries,
  getSummaryById,
};
