<template>
  <div class="bg-gradient-primary min-vh-100 d-flex justify-content-center align-items-center">
    <div class="card o-hidden border-0 shadow-lg my-5" style="width: 400px;">
      <div class="card-body p-5">
        <!-- 로고 + 제목 -->
        <div class="text-center mb-4">
          <img src="/kut_logo.gif" alt="Logo" class="img-fluid mb-3" style="width: 60px;" />
          <h1 class="h4 text-gray-900 mb-1">KOREATECH</h1>
          <p class="text-gray-600 mb-4">온라인 교육 로그인</p>
        </div>

        <!-- 로그인 폼 -->
        <form @submit.prevent="handleLogin" class="user">
          <div class="form-group mb-3">
            <input
              v-model="userId"
              type="text"
              class="form-control form-control-user"
              placeholder="아이디"
              required
            />
          </div>
          <div class="form-group mb-3">
            <input
              v-model="password"
              type="password"
              class="form-control form-control-user"
              placeholder="비밀번호"
              required
            />
          </div>
          <button type="submit" class="btn btn-primary btn-user w-100" :disabled="loading">
            {{ loading ? "로그인 중..." : "로그인" }}
          </button>
        </form>

        <!-- 에러 메시지 -->
        <p v-if="errorMessage" class="text-danger text-center mt-3 small">
          {{ errorMessage }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'HomeView',
  setup() {
    const userId = ref('')
    const password = ref('')
    const errorMessage = ref('')
    const loading = ref(false)
    const router = useRouter()

    const BASE_URL = 'https://project2025-backend.onrender.com'

    const handleLogin = async () => {
      errorMessage.value = ''
      loading.value = true

      try {
        const formData = new URLSearchParams()
        formData.append('username', userId.value)
        formData.append('password', password.value)

        const response = await axios.post(`${BASE_URL}/login`, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          withCredentials: true   // ✅ 여기로 와야 함!
        })

        const token = response.data.access_token
        localStorage.setItem('access_token', token)

        const payload = JSON.parse(atob(token.split('.')[1]))
        const role = payload.role

        if (role === 'professor') {
          router.push('/professor')
        } else if (role === 'student') {
          router.push('/student')
        } else {
          errorMessage.value = '권한 정보가 올바르지 않습니다.'
        }
      } catch (error) {
        console.error(error)
        errorMessage.value = '❌ 로그인 실패: 아이디 또는 비밀번호를 확인하세요.'
      } finally {
        loading.value = false
      }
    }

    return {
      userId,
      password,
      errorMessage,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(180deg, #4e73df 10%, #224abe 100%);
  background-size: cover;
}
.card {
  border-radius: 1rem;
}
.form-control-user {
  border-radius: 10rem;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
}
.btn-user {
  border-radius: 10rem;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
}
</style>
