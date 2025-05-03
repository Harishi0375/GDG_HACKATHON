<script setup>
// Import RouterLink to enable navigation via the custom button
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="landing-page">
    <div class="content-container">
      <header class="landing-header">
        <h1>Codified Likeness Utility</h1>
        <p class="tagline">
          AI-powered document analysis and information localization, fine-tuned with Google Gemini.
        </p>
      </header>

      <section class="description-section">
        <div class="description-card">
          <h2>What it Does</h2>
          <p>
            CLU leverages a fine-tuned Vision-Language Large Model (VLLM) to accurately extract key information (summaries, main points, data, definitions) from various documents like lecture notes, research papers, and forms. Crucially, it also tells you <em>where</em> in the document that information was found.
          </p>
          <hr class="divider">
          <h2>How it Helps</h2>
          <ul>
            <li><strong>Students:</strong> Quickly analyze notes, summarize papers, and review study materials efficiently.</li>
            <li><strong>Educators:</strong> Check specific details in assignments and prepare materials faster.</li>
            <li><strong>Researchers:</strong> Extract findings and references from papers with precise localization.</li>
          </ul>
          <p>
            Stop wasting time searching – let CLU pinpoint the information you need.
          </p>
        </div>
      </section>

      <footer class="landing-footer">
        <RouterLink to="/prompt" custom v-slot="{ navigate }">
          <button @click="navigate" role="link" class="fancy-button">
            <span>LETS BEGIN</span>
          </button>
        </RouterLink>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* --- Dark Theme Variables --- */
/* Define colors suitable for a dark background */
:root {
  --bg-dark: #1a1a1a; /* Very dark background */
  --content-bg-dark: #242424; /* Slightly lighter content area */
  --text-bright: #e4e4e4; /* Bright primary text */
  --text-muted: #a0a0a0; /* Muted secondary text */
  --primary-accent: #42d392; /* Vue green */
  --primary-accent-hover: #34a853;
  --border-dark: #444;
  --shadow-dark: rgba(0, 0, 0, 0.4);
  --button-initial-bg-dark: #3f3f3f;
  --button-text-initial-dark: #e4e4e4;
  --button-text-hover-dark: #1a1a1a; /* Dark text on hover */
  --button-bg-hover-dark: var(--primary-accent);
  --button-shadow-hover-dark: rgba(66, 211, 146, 0.4);
}

/* --- Base Layout --- */
.landing-page {
  /* Centering is handled by App.vue's <main> tag */
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  color: var(--text-bright); /* Use bright text */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
  /* Background is likely set globally or by App.vue based on theme */
}

/* --- Content Wrapper --- */
.content-container {
  max-width: 800px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 30px;
  background-color: var(--content-bg-dark); /* Dark content background */
  padding: 40px 50px;
  border-radius: 12px;
  box-shadow: 0 4px 15px var(--shadow-dark);
  border: 1px solid var(--border-dark);
  margin: 0 auto; /* Center the container block horizontally */
  text-align: center; /* Default text alignment */
}

/* --- Header --- */
.landing-header {
  text-align: center;
}
.landing-header h1 {
  color: var(--text-bright); /* Bright heading */
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 2.8em;
  font-weight: 700;
  letter-spacing: -0.5px;
}
.landing-header .tagline {
  font-size: 1.3em;
  color: var(--text-muted); /* Muted text */
  margin-bottom: 0;
  font-weight: 400;
}

/* --- Description Section --- */
.description-section {
  width: 100%;
}

.description-card {
  padding: 0;
  text-align: left;
  background-color: var(--content-bg-dark); /* Match container background */
}
.description-card h2 {
  color: var(--primary-accent); /* Accent color for headings */
  margin-top: 0;
  margin-bottom: 15px;
  border-bottom: 1px solid var(--border-dark);
  padding-bottom: 10px;
  font-size: 1.6em;
  font-weight: 600;
}
.divider {
  border: none;
  height: 1px;
  background-color: var(--border-dark);
  margin: 30px 0;
}
.description-card ul {
  list-style-position: outside;
  padding-left: 25px;
  color: var(--text-muted);
  margin-top: 15px;
}
.description-card ul li strong {
  color: var(--text-bright); /* Bright text for strong */
}
.description-card li {
  margin-bottom: 12px;
  line-height: 1.6;
}
.description-card p {
  text-align: left;
  line-height: 1.6;
  color: var(--text-muted);
  margin-top: 15px;
  margin-bottom: 0;
}
.description-card p:first-of-type {
  margin-top: 0;
}
.description-card p em {
  color: var(--primary-accent);
  font-style: normal;
  font-weight: 600;
}

/* --- Footer / Button Area --- */
.landing-footer {
  margin-top: 20px;
  width: 100%;
  text-align: center;
}

/* --- Fancy Button Styles (Adapted for Dark Theme) --- */
.fancy-button {
  display: inline-block;
  border: none;
  position: relative;
  width: 220px;
  height: 73px;
  padding: 0;
  z-index: 2;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='868' width='2500' viewBox='0 0 726 252.17'%3E%3Cpath d='M483.92 0S481.38 24.71 466 40.11c-11.74 11.74-24.09 12.66-40.26 15.07-9.42 1.41-29.7 3.77-34.81-.79-2.37-2.11-3-21-3.22-27.62-.21-6.92-1.36-16.52-2.82-18-.75 3.06-2.49 11.53-3.09 13.61S378.49 34.3 378 36a85.13 85.13 0 0 0-30.09 0c-.46-1.67-3.17-11.48-3.77-13.56s-2.34-10.55-3.09-13.61c-1.45 1.45-2.61 11.05-2.82 18-.21 6.67-.84 25.51-3.22 27.62-5.11 4.56-25.38 2.2-34.8.79-16.16-2.47-28.51-3.39-40.21-15.13C244.57 24.71 242 0 242 0H0s69.52 22.74 97.52 68.59c16.56 27.11 14.14 58.49 9.92 74.73C170 140 221.46 140 273 158.57c69.23 24.93 83.2 76.19 90 93.6 6.77-17.41 20.75-68.67 90-93.6 51.54-18.56 103-18.59 165.56-15.25-4.21-16.24-6.63-47.62 9.93-74.73C656.43 22.74 726 0 726 0z'/%3E%3C/svg%3E") no-repeat center center;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='868' width='2500' viewBox='0 0 726 252.17'%3E%3Cpath d='M483.92 0S481.38 24.71 466 40.11c-11.74 11.74-24.09 12.66-40.26 15.07-9.42 1.41-29.7 3.77-34.81-.79-2.37-2.11-3-21-3.22-27.62-.21-6.92-1.36-16.52-2.82-18-.75 3.06-2.49 11.53-3.09 13.61S378.49 34.3 378 36a85.13 85.13 0 0 0-30.09 0c-.46-1.67-3.17-11.48-3.77-13.56s-2.34-10.55-3.09-13.61c-1.45 1.45-2.61 11.05-2.82 18-.21 6.67-.84 25.51-3.22 27.62-5.11 4.56-25.38 2.2-34.8.79-16.16-2.47-28.51-3.39-40.21-15.13C244.57 24.71 242 0 242 0H0s69.52 22.74 97.52 68.59c16.56 27.11 14.14 58.49 9.92 74.73C170 140 221.46 140 273 158.57c69.23 24.93 83.2 76.19 90 93.6 6.77-17.41 20.75-68.67 90-93.6 51.54-18.56 103-18.59 165.56-15.25-4.21-16.24-6.63-47.62 9.93-74.73C656.43 22.74 726 0 726 0z'/%3E%3C/svg%3E") no-repeat center center;
  -webkit-mask-size: contain;
  mask-size: contain;
  cursor: pointer;
  background-color: var(--button-initial-bg-dark); /* Use dark theme variable */
  transform: translateY(0px);
  transition: transform 0.2s ease, background-color 0.6s ease;
}
.fancy-button:hover {
    transform: translateY(-3px);
    background-color: var(--button-bg-hover-dark); /* Use dark theme variable */
}
.fancy-button:active {
    transform: translateY(0px);
}
.fancy-button::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  box-shadow: 0px 0px 0px 0px var(--button-shadow-hover-dark); /* Use dark theme variable */
  opacity: 0;
  transition: box-shadow 0.6s ease-out, opacity 0.6s ease-out;
  z-index: 1;
  pointer-events: none;
   -webkit-mask: inherit;
   mask: inherit;
}
.fancy-button:hover::after {
  opacity: 1;
  box-shadow: 0px 0px 35px 10px var(--button-shadow-hover-dark); /* Use dark theme variable */
}
.fancy-button span {
  position: absolute;
  width: 100%;
  font-size: 16px;
  font-weight: 500;
  left: 50%;
  top: 50%;
  letter-spacing: 3px;
  text-align: center;
  transform: translate(-50%, -50%);
  color: var(--button-text-initial-dark); /* Use dark theme variable */
  transition: color 0.6s ease-out;
  z-index: 3;
}
.fancy-button:hover span {
  color: var(--button-text-hover-dark); /* Use dark theme variable */
}
/* End Fancy Button Styles */
</style>