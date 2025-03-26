<template>
  <div class="chat-container">
    <h2>Chat with AI</h2>

    <div class="chat-box">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['chat-bubble', message.role]"
      >
        {{ message.content }}
      </div>
    </div>

    <div class="input-area">
      <input
        v-model="userInput"
        placeholder="Type a message..."
        @keyup.enter="sendMessage"
      />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import { ref } from "vue"
import { sendMessageToChatGPT } from "@/api/chatService"

export default {
  name: "ChatComponent",
  setup() {
    const messages = ref([])
    const userInput = ref("")

    const sendMessage = async () => {
      if (userInput.value.trim() === "") return

      messages.value.push({ role: "user", content: userInput.value })

      const response = await sendMessageToChatGPT(userInput.value)

      // 백엔드에서 { answer: "...내용..." } 구조니까, answer만 꺼내서 저장
      const answer = typeof response === "object" ? response.answer : response

      messages.value.push({ role: "assistant", content: answer })
      userInput.value = ""
    }

    return { messages, userInput, sendMessage }
  },
}
</script>

<style scoped>
.chat-container {
  max-width: 1000px;
  width: 90%;
  margin: 40px auto;
  background: #f9f9f9;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

h2 {
  margin-bottom: 25px;
  text-align: center;
  font-weight: 700;
  font-size: 1.8rem;
}

.chat-box {
  height: 400px;
  overflow-y: auto;
  padding: 15px;
  background: #ffffff;
  border: 1px solid #ddd;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-bubble {
  max-width: 80%;
  padding: 12px 18px;
  border-radius: 16px;
  word-break: break-word;
  line-height: 1.5;
  font-size: 1rem;
}

/* 사용자 메시지 (오른쪽) */
.user {
  align-self: flex-end;
  background-color: #d0e7ff;
  color: #004085;
  border-top-right-radius: 0;
}

/* AI 응답 (왼쪽) */
.assistant {
  align-self: flex-start;
  background-color: #e2e3e5;
  color: #383d41;
  border-top-left-radius: 0;
}

.input-area {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

input {
  flex: 1;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
}

button {
  padding: 12px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

button:hover {
  background-color: #0056b3;
}

</style>
