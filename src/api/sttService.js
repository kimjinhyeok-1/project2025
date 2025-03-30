// src/api/sttService.js
import axios from "axios";

// ✅ 백엔드2에서 실행 중인 FastAPI 주소 (너의 IP로 바꿔!)
const STT_API_BASE = "http://172.22.170.43:8000";

// 📤 스냅샷 업로드 (타임스탬프 + 캡처 이미지 + 문장)
export async function uploadSnapshot({ timestamp, transcript, screenshot_base64 }) {
  try {
    const response = await axios.post(`${STT_API_BASE}/snapshots`, {
      timestamp,
      transcript,
      screenshot_base64,
    });
    console.log("✅ 스냅샷 업로드 성공:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 스냅샷 업로드 실패:", error);
    throw error;
  }
}

// 📥 전체 스냅샷 목록 조회
export async function getSnapshots() {
  try {
    const response = await axios.get(`${STT_API_BASE}/snapshots`);
    console.log("📥 복습 데이터 수신 완료:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 복습 데이터 요청 실패:", error);
    throw error;
  }
}

// 📘 요약 목록 가져오기 (날짜 기준)
export async function getSummaries() {
  try {
    const response = await axios.get(`${STT_API_BASE}/summaries`);
    console.log("📘 요약 목록 수신 완료:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 요약 목록 요청 실패:", error);
    throw error;
  }
}

// 📄 특정 요약 리포트 상세 보기
export async function getSummaryById(id) {
  try {
    const response = await axios.get(`${STT_API_BASE}/summaries/${id}`);
    console.log("📄 요약 상세 수신 완료:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ 요약 상세 요청 실패:", error);
    throw error;
  }
}
