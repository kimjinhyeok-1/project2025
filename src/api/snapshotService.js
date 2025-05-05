import axios from 'axios';

const BASE_URL = 'https://project2025-backend.onrender.com';

// 🕒 현재 시간 포맷: yyyy-MM-dd HH:mm:ss
function getFormattedTimestamp() {
  const now = new Date();
  return `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, "0")}-${now.getDate().toString().padStart(2, "0")} ${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
}

// 🖼️ 스크린샷 캡처 (video에 연결한 후 안정적 타이밍 확보)
async function captureScreenshot() {
  try {
    const displayStream = await navigator.mediaDevices.getDisplayMedia({
      video: true
    });

    const video = document.createElement("video");
    video.srcObject = displayStream;
    video.muted = true;
    video.playsInline = true;

    // DOM 없이도 플레이 가능
    await video.play();

    await new Promise(resolve => {
      video.onloadeddata = () => resolve();
    });

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    // 스트림 정리
    video.pause();
    video.srcObject = null;
    displayStream.getTracks().forEach(track => track.stop());

    return canvas.toDataURL("image/png");

  } catch (err) {
    console.error("❌ 화면 캡처 실패:", err);
    return "";
  }
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

export { captureScreenshot, uploadSnapshot };
