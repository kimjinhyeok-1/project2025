// src/api/chatService.js
import axios from "axios";

const BASE_URL = "https://project2025-backend.onrender.com/api/ask_assistant"; // 친구 FastAPI 서버 주소

export async function sendMessageToChatGPT(message) {
  try {
    console.log("FastAPI 백엔드로 요청 시작...");

    const response = await axios.get(`${BASE_URL}`, {
      params: { q: message },
      withCredentials: true
    });

    console.log("백엔드 응답:", response.data);
    return response.data; // FastAPI가 바로 텍스트를 주는 구조라고 가정
  } catch (error) {
    console.error("FastAPI API Error:", error);

    if (error.response) {
      return `⚠️ 백엔드 오류 (${error.response.status}): ${JSON.stringify(error.response.data)}`
    } else {
      return "⚠️ 네트워크 오류 발생. 서버 연결을 확인하세요.";
    }
  }
}
