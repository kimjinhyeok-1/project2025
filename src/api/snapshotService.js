// src/api/snapshotService.js
import axios from 'axios'

const BASE_URL = 'https://project2025-backend.onrender.com'

// 🖼️ 스냅샷 업로드 (date, time, text, screenshot_base64 포맷)
export async function uploadSnapshot({ timestamp, transcript, screenshot_base64 }) {
  try {
    const [date, time] = timestamp.split(' ');  // "2025-04-28 15:30:00" → "2025-04-28", "15:30:00"

    const response = await axios.post(`${BASE_URL}/snapshots/snapshots`, {
      date,
      time,
      text: transcript,
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

// 🧪 OPTIONS 요청 테스트 (에러 디버깅용)
export async function testOptionsRequest() {
  const url = `${BASE_URL}/snapshots/snapshots`;

  try {
    console.log(`🌐 [OPTIONS 테스트 시작] URL: ${url}`);

    const response = await fetch(url, {
      method: 'OPTIONS',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('✅ 서버가 OPTIONS 요청을 정상적으로 받았습니다.');
    console.log('🔎 응답 상태 코드:', response.status);
    console.log('🔎 응답 헤더:', [...response.headers.entries()]);

    if (response.status >= 200 && response.status < 300) {
      console.log('🎯 서버에서 OPTIONS 요청이 허용되었습니다. (정상)');
    } else {
      console.warn('⚠️ 서버에서 응답은 왔지만 상태 코드가 2xx가 아닙니다.');
    }
  } catch (err) {
    console.error('❌ 서버가 OPTIONS 요청을 처리하지 못했습니다.');
    console.error('🧹 에러 상세:', err);
  }
}
