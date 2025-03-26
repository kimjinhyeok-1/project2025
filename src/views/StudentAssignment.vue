<template>
  <div class="container mt-5">
    <h3>📂 과제 제출</h3>
    <p class="text-muted">여러 개의 파일을 제출할 수 있어요!</p>

    <form @submit.prevent="handleUpload">
      <div class="mb-3">
        <label for="fileInput" class="form-label">파일 선택</label>
        <input
          class="form-control"
          type="file"
          id="fileInput"
          multiple
          @change="handleFileChange"
        />
      </div>

      <button type="submit" class="btn btn-primary">제출하기</button>
    </form>

    <p v-if="uploadStatus" class="mt-3">{{ uploadStatus }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const files = ref([])
const uploadStatus = ref('')

const handleFileChange = (event) => {
  files.value = Array.from(event.target.files)
}

const handleUpload = async () => {
  if (files.value.length === 0) {
    uploadStatus.value = '❗ 업로드할 파일을 선택하세요.'
    return
  }

  const formData = new FormData()
  files.value.forEach((file) => {
    formData.append('files', file)
  })

  try {
    await axios.post('http://192.168.50.24:8000/upload', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

    uploadStatus.value = '✅ 업로드 성공!'
  } catch (err) {
    console.error('업로드 실패:', err)
    uploadStatus.value = '❌ 업로드 실패. 나중에 다시 시도해주세요.'
  }
}
</script>
