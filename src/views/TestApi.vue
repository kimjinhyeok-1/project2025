import api from "@/api";

export default {
  name: "TestApi",
  mounted() {
    api.get("/health")
      .then(res => {
        console.log("✅ 연결 성공:", res.data);
      })
      .catch(err => {
        console.error("❌ 연결 실패:", err);
      });
  },
  template: `<div>API 연결 확인 중... 개발자도구(F12) 콘솔을 확인하세요.</div>`
}
