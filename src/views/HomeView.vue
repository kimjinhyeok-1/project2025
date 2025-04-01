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
          <button type="submit" class="btn btn-primary btn-user w-100">
            로그인
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
        router.push(foundUser.role === 'teacher' ? '/professor' : '/student')
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
