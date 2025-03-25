<template>
  <div>
    <NavbarComponent />
    <div class="container mt-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import NavbarComponent from './components/NavbarComponent.vue';

export default {
  components: {
    NavbarComponent,
  },
};
</script>
