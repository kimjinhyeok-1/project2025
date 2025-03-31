<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white shadow py-3 mb-4">
    <div class="container-fluid">
      <!-- 로고 텍스트 -->
      <span class="navbar-brand text-primary fw-bold text-uppercase">KOREATECH</span>

      <!-- 햄버거 버튼 (모바일용) -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- 메뉴 항목 -->
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link text-gray-800 fw-semibold" to="/student">
              <i class="fas fa-user-graduate me-1"></i> 학생 페이지
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link text-gray-800 fw-semibold" to="/professor">
              <i class="fas fa-chalkboard-teacher me-1"></i> 교수자 페이지
            </router-link>
          </li>
        </ul>

        <!-- 로그아웃 버튼 -->
        <div v-if="isLoggedIn" class="d-flex">
          <button class="btn btn-danger btn-sm" @click="logout">
            <i class="fas fa-sign-out-alt me-1"></i> 로그아웃
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'NavbarComponent',
  setup() {
    const isLoggedIn = ref(false)
    const router = useRouter()

    const checkLogin = () => {
      isLoggedIn.value = !!localStorage.getItem('user')
    }

    const logout = () => {
      localStorage.removeItem('user')
      isLoggedIn.value = false
      router.push('/')
    }

    onMounted(() => {
      checkLogin()
    })

    return {
      isLoggedIn,
      logout,
    }
  },
}
</script>

<style scoped>
.navbar-brand {
  font-size: 1.2rem;
  letter-spacing: 1px;
}

.nav-link {
  font-size: 0.95rem;
}

.btn-sm {
  font-size: 0.85rem;
  padding: 0.375rem 0.75rem;
}
</style>
