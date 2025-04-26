<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm px-4 w-100">
    <div class="container-fluid">
      <!-- 왼쪽 브랜드 -->
      <span class="sidebar-brand-text mx-4">KOREATECH</span>

      <!-- 오른쪽 메뉴 -->
      <div class="d-flex align-items-center ms-auto gap-3">
        <router-link to="/student" class="btn btn-link text-primary">🎓 학생 페이지</router-link>
        <router-link to="/professor" class="btn btn-link text-primary">👨‍🏫 교수자 페이지</router-link>
        <router-link to="/" class="btn btn-danger">로그아웃</router-link>
        <router-link to="/record" class="btn btn-link text-success">🤖 실시간 질문 시연</router-link>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavbarComponent',
}
</script>

<style scoped>
.navbar {
  height: 56px;
}
</style>
