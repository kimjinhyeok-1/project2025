<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm px-4 w-100">
    <div class="container-fluid">
      <!-- 왼쪽 브랜드 -->
      <div class="d-flex align-items-center">
        <img src="/kut_logo.gif" alt="KUT Logo" class="kut-logo" />
        <span class="sidebar-brand-text">KOREATECH</span>
      </div>

      <!-- 오른쪽 메뉴 -->
      <div class="d-flex align-items-center ms-auto gap-3">
        <div class="user-info">
          <span class="user-id">{{ userId }}</span>
          <span class="user-number">({{ studentNumber }})</span>
        </div>
        <router-link to="/" class="btn btn-danger">로그아웃</router-link>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavbarComponent',
  data() {
    return {
      userId: '',
      studentNumber: ''
    }
  },
  mounted() {
    this.userId = localStorage.getItem('user_id') || ''
    this.studentNumber = localStorage.getItem('student_number') || ''
  }
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
  margin-right: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 4px; /* 이름과 학번 사이 간격 */
  margin-right: 8px; /* 로그아웃 버튼과의 거리 */
}

.user-id {
  font-weight: 600;
  color: #000; /* 검정색 */
}

.user-number {
  color: #6c757d; /* 기존 회색 그대로 */
}
</style>
