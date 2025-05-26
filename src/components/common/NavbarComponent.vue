<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm px-4 w-100">
    <div class="container-fluid">
      <!-- 왼쪽 브랜드 -->
      <div class="d-flex align-items-center">
        <img src="/kut_logo.gif" alt="KUT Logo" class="kut-logo me-2" />
        <span class="sidebar-brand-text">KOREATECH</span>
      </div>

      <!-- 오른쪽 메뉴 -->
      <div class="d-flex align-items-center ms-auto gap-3">
        <router-link to="/" class="btn btn-danger">로그아웃</router-link>
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

.kut-logo {
  height: 32px;
  width: auto;
  object-fit: contain;
}
</style>
