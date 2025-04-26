<template>
  <div>
    <!-- 현재 경로가 '/'가 아닐 때만 네비게이션 바 표시 -->
    <NavbarComponent v-if="!isHome" />

    <!-- 라우터 뷰는 항상 표시 -->
    <div>
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import NavbarComponent from '@/components/common/NavbarComponent.vue'

export default {
  components: {
    NavbarComponent,
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

