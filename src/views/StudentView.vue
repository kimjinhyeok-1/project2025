<template>
  <div class="container">
    <h2>Student Dashboard</h2>
    <p>어서오세요. 궁금한 점이 있다면 밑에 Chat bot을 통해 가상의 교수님께 질문해주세요.</p>

    <!-- 채팅 버튼 -->
    <button @click="showChat = !showChat" class="btn btn-primary mt-3">
      {{ showChat ? "Close Chat" : "Open Chat" }}
    </button>

    <!-- 채팅 UI -->
    <ChatComponent v-if="showChat" />
  </div>
</template>

<script>
import { ref } from "vue";
import ChatComponent from "@/components/ChatComponent.vue";

export default {
  name: "StudentView",
  components: {
    ChatComponent,
  },
  setup() {
    const showChat = ref(false); // 채팅 버튼 상태 관리

    return { showChat };
  },
};
</script>

<style scoped>
.container {
  text-align: center;
  margin-top: 20px;
}
</style>
