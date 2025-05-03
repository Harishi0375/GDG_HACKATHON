<script setup>
// Only import RouterView from vue-router
import { RouterView } from 'vue-router'
</script>

<template>
  <main>
    <RouterView />
  </main>
</template>

<style scoped>
/* Apply centering styles directly to the main element */
main {
  display: flex;            /* Enable Flexbox */
  justify-content: center;  /* Center content horizontally */
  align-items: center;      /* Center content vertically */
  min-height: 100vh;        /* Ensure main takes at least full viewport height for vertical centering */
  width: 100%;              /* Ensure main takes full width */
  box-sizing: border-box;   /* Include padding/border in height/width calculation */
  padding: 1rem;            /* Keep your desired padding around the centered content */
}

/* Styles for header and .logo below are not needed */
/* unless you add a <header> or element with class="logo" back into the template */
/*
header {
  line-height: 1.5;
}

.logo {
 display: none;
}
*/

/* Add any other global layout styles for App.vue here if needed */
</style>

<style>
/* Optional: Global styles (not scoped) if needed for body reset etc. */
/* It's good practice to have minimal body margin */
body {
  margin: 0;
  font-family: sans-serif; /* Example base font */
}
</style>