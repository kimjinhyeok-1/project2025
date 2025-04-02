<template>
  <div>
    <!-- 현재 경로가 '/'가 아닐 때만 네비게이션 바 표시 -->
    <NavbarComponent v-if="!isHome" />

    <!-- ✅ 여기에 TestApi 추가 (테스트 후 나중에 지워도 됨) -->
    <TestApi />

    <!-- 라우터 뷰는 항상 표시 -->
    <div>
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import NavbarComponent from './components/NavbarComponent.vue'
import TestApi from './views/TestApi.vue' // ✅ TestApi 임포트 추가

export default {
  components: {
    NavbarComponent,
    TestApi, // ✅ 등록
  },
  setup() {
    const route = useRoute()
    const isHome = computed(() => route?.path === '/')
    return {
      isHome,
    }
  },
}
</script>
