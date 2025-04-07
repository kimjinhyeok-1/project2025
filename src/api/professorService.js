// src/api/professorService.js
import axios from "axios";

const BASE_URL = "http://192.168.50.24:8000";

// 질문 요약 가져오기
export async function getChatSummary() {
  const response = await axios.get(`${BASE_URL}/api/professor/qna-summary`);
  return response.data;
}

// 전체 대화 로그 가져오기
export async function getChatLogs() {
  const response = await axios.get(`${BASE_URL}/api/chat/logs`);
  return response.data;
}
