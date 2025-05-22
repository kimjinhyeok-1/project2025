import axios from 'axios';

const BASE_URL = 'https://project2025-backend.onrender.com';

function getFormattedTimestamp() {
  const now = new Date();
  return `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, "0")}-${now.getDate().toString().padStart(2, "0")} ${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
}

async function createLecture() {
  try {
    const response = await axios.post(`${BASE_URL}/snapshots/lectures`, {}, { withCredentials: true });
    const lecture_id = response.data.lecture_id;
    localStorage.setItem("lecture_id", lecture_id.toString());
    console.log("✅ 강의 세션 시작:", lecture_id);
    return lecture_id;
  } catch (error) {
    console.error("❌ 강의 세션 생성 실패:", error.response?.data || error.message || error);
    throw error;
  }
}

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

async function uploadSnapshot({ transcript = "", screenshot_base64 = "" }) {
  const lecture_id = localStorage.getItem("lecture_id");
  if (!lecture_id) {
    console.error("❌ lecture_id 없음. 세션을 먼저 시작하세요.");
    return;
  }

  const cleanedTranscript = transcript.trim();
  const timestamp = getFormattedTimestamp();

  try {
    const response = await axios.post(
      `${BASE_URL}/snapshots/snapshots?lecture_id=${lecture_id}`,
      { timestamp, transcript: cleanedTranscript, screenshot_base64 },
      { withCredentials: true }
    );
    console.log("✅ 스냅샷 업로드 성공:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 스냅샷 업로드 실패:", error.response?.data || error.message || error);
    throw error;
  }
}

async function getSummaries() {
  const lecture_id = localStorage.getItem("lecture_id");
  if (!lecture_id) {
    console.error("❌ lecture_id 없음. 세션을 먼저 시작하세요.");
    return;
  }
  try {
    const response = await axios.get(`${BASE_URL}/snapshots/lecture_summary?lecture_id=${lecture_id}`);
    console.log("📥 요약 목록 수신 완료:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 요약 목록 요청 실패:", error);
    throw error;
  }
}

async function generateLectureSummary() {
  const lecture_id = localStorage.getItem("lecture_id");
  if (!lecture_id) throw new Error("lecture_id 없음");

  try {
    const response = await axios.post(`${BASE_URL}/snapshots/lecture_summary?lecture_id=${lecture_id}`);
    console.log("✅ 요약 생성 및 저장 완료:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 요약 저장 실패:", error);
    throw error;
  }
}

export {
  createLecture,
  captureScreenshot,
  uploadSnapshot,
  getSummaries,
  generateLectureSummary
};
