<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <main>
    <RouterView />
  </main>
</template>

<style scoped>
/* Scoped styles for main in App.vue */
/* Keep these if you need specific styling for the <main> tag itself */
/* Or remove this block if not needed */
main {
  width: 100%;
  /* Consider removing height: 100% unless specifically needed */
  /* height: 100%; */
  display: block; /* display: block is default for main, may be redundant */
  box-sizing: border-box;
}
</style>