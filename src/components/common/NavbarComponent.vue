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
          <div class="avatar-circle">
            <i class="fas fa-user"></i>
          </div>
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
  gap: 6px;
  margin-right: 16px;
}

.user-id {
  font-weight: 600;
  color: #000;
}

.user-number {
  color: #6c757d;
}

/* ✅ 동그란 아이콘 스타일 */
.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-circle i {
  color: #6c757d;
  font-size: 16px;
}
</style>
