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
          <span class="user-id">{{ userId }}님</span>
          <span class="user-number">({{ studentNumber }})</span>
          <i class="fas fa-user user-icon"></i> <!-- 아이콘 -->
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
  gap: 4px;
  margin-right: 16px; /* 버튼과의 간격 약간 넓힘 */
}

.user-id {
  font-weight: 600;
  color: #000;
}

.user-number {
  color: #6c757d;
}

.user-icon {
  font-size: 18px;
  color: #6c757d;
}
</style>
