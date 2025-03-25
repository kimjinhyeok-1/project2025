<template>
  <nav class="navbar navbar-expand-lg bg-primary">
    <div class="container-fluid">
      <!-- 로고: 클릭 시 이동하지 않도록 router-link 제거 -->
      <span class="navbar-brand text-white fw-bold">Koreatech</span>

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

      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <!-- 필요 시 다른 메뉴 유지 -->
          <li class="nav-item">
            <router-link class="nav-link text-white" to="/student">Student</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link text-white" to="/professor">Professor</router-link>
          </li>
        </ul>

        <!-- 로그아웃 버튼 (로그인 상태일 때만 표시) -->
        <div v-if="isLoggedIn" class="d-flex">
          <button class="btn btn-outline-light" @click="logout">Logout</button>
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
.navbar {
  box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
}
</style>
