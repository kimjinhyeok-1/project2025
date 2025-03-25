<!-- src/views/LoginPage.vue -->
<template>
  <div class="container mt-5" style="max-width: 400px;">
    <h2 class="text-center mb-4">로그인</h2>
    <form @submit.prevent="handleLogin">
      <div class="mb-3">
        <label for="id" class="form-label">아이디</label>
        <input v-model="userId" type="text" id="id" class="form-control" required />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">비밀번호</label>
        <input v-model="password" type="password" id="password" class="form-control" required />
      </div>
      <button type="submit" class="btn btn-primary w-100">로그인</button>
    </form>
    <p v-if="errorMessage" class="text-danger text-center mt-3">{{ errorMessage }}</p>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginPage',
  setup() {
    const userId = ref('')
    const password = ref('')
    const errorMessage = ref('')
    const router = useRouter()

    // 샘플 사용자 데이터 (실제론 서버에서 받아야 함)
    const users = [
      { id: 'prof001', password: '1234', role: 'teacher' },
      { id: 'stu001', password: '5678', role: 'student' },
    ]

    const handleLogin = () => {
      const foundUser = users.find(
        (user) => user.id === userId.value && user.password === password.value
      )

      if (foundUser) {
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
