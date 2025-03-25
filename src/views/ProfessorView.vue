<template>
  <div class="container text-center mt-5">
    <h2>📚 Professor Dashboard</h2>
    <p class="text-muted">원하시는 메뉴를 선택하세요</p>

    <div class="d-grid gap-3 col-6 mx-auto mt-4">
      <router-link to="/professor/qna" class="btn btn-outline-primary btn-lg">
        ❓ 질문 & 답변 확인하기
      </router-link>
      <router-link to="/professor/lesson" class="btn btn-outline-success btn-lg">
        🎥 수업하기
      </router-link>
      <router-link to="/professor/assignments" class="btn btn-outline-warning btn-lg">
        📝 과제 확인하기
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProfessorView",
};
</script>
