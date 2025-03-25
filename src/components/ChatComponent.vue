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
  width: 500px;
  margin: auto;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

h2 {
  margin-bottom: 20px;
}

.chat-box {
  height: 300px;
  overflow-y: auto;
  padding: 10px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-bubble {
  max-width: 75%;
  padding: 10px 15px;
  border-radius: 15px;
  word-break: break-word;
  line-height: 1.4;
}

/* 학생 (오른쪽) */
.user {
  align-self: flex-end;
  background-color: #d0e7ff;
  color: #004085;
  border-top-right-radius: 0;
}

/* GPT (왼쪽) */
.assistant {
  align-self: flex-start;
  background-color: #e2e3e5;
  color: #383d41;
  border-top-left-radius: 0;
}

.input-area {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
}

button {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>
