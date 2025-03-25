<!-- src/views/HomeView.vue -->
<template>
  <div class="bg-gradient-primary min-vh-100 d-flex justify-content-center align-items-center">
    <div class="card shadow p-5" style="width: 400px; border-radius: 1rem;">
      <!-- 상단 로고 + 제목 -->
      <div class="text-center mb-4">
        <img src="/kut_logo.gif" alt="Logo" class="logo-gif mb-2" />
        <h1 class="mb-1">KOREATECH</h1>
        <p class="text-muted">온라인 교육</p>
      </div>

      <!-- 로그인 폼 -->
      <form @submit.prevent="handleLogin">
        <div class="form-group mb-3">
          <input
            v-model="userId"
            type="text"
            class="form-control rounded-pill"
            placeholder="아이디"
            required
          />
        </div>
        <div class="form-group mb-3">
          <input
            v-model="password"
            type="password"
            class="form-control rounded-pill"
            placeholder="비밀번호"
            required
          />
        </div>
        <button type="submit" class="btn btn-primary w-100 rounded-pill">로그인</button>
      </form>

      <p v-if="errorMessage" class="text-danger text-center mt-3">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'HomeView',
  setup() {
    const userId = ref('')
    const password = ref('')
    const errorMessage = ref('')
    const router = useRouter()

    const users = [
      { id: 'prof001', password: '1234', role: 'teacher', name: '설순옥' },
      { id: 'stu001', password: '5678', role: 'student', name: '김민주' },
    ]

    const handleLogin = () => {
      const foundUser = users.find(
        (user) => user.id === userId.value && user.password === password.value
      )

      if (foundUser) {
        localStorage.setItem('user', JSON.stringify(foundUser))

        // ✅ 역할에 따라 라우팅
        if (foundUser.role === 'teacher') {
          router.push('/professor')
        } else if (foundUser.role === 'student') {
          router.push('/student')
        }
      } else {
        errorMessage.value = '아이디 또는 비밀번호가 올바르지 않습니다.'
      }
    }

    return {
      userId,
      password,
      handleLogin,
      errorMessage
    }
  }
}
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(to bottom right, #4e73df, #224abe);
}

.logo-gif {
  width: 60px;
  height: auto;
  border-radius: 8px;
}

.mb-1 {
  font-family: 'Do Hyeon', sans-serif;
  font-size: 2.0rem;
  font-weight: 700;
  color: #1a1a1a;
}

.text-muted {
  font-family: 'Do Hyeon', sans-serif;
  font-size: 1.0rem;
  font-weight: 600;
  color: #555;
}
</style>
