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
            Stop wasting time searching - let CLU pinpoint the information you need.
          </p>
        </div>
      </section>

      <footer class="landing-footer">
        <RouterLink to="/prompt" custom v-slot="{ navigate }">
          <button @click="navigate" role="link" class="fancy-button">
            <span>LETS BEGIN</span>
          </button>
        </RouterLink>

        <nav class="footer-nav">
          <RouterLink to="/about">About</RouterLink> |
          <RouterLink to="/license">License</RouterLink>
        </nav>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* --- Dark Theme Variables --- */
:root {
  --bg-dark: #1a1a1a;
  --content-bg-dark: #242424;
  --text-bright: #e4e4e4;
  --text-muted: #a0a0a0;
  --primary-accent: #42d392;
  --primary-accent-hover: #34a853;
  --border-dark: #444;
  --shadow-dark: rgba(0, 0, 0, 0.4);
}

/* --- Centering Layout for the View --- */
.landing-page {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  color: var(--text-bright);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
}

/* --- Content Wrapper --- */
.content-container {
  max-width: 800px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 30px;
  background-color: var(--content-bg-dark);
  padding: 40px 50px;
  border-radius: 12px;
  box-shadow: 0 4px 15px var(--shadow-dark);
  border: 1px solid var(--border-dark);
  text-align: center;
}

/* --- Header --- */
.landing-header {
  text-align: center;
}
.landing-header h1 {
  color: var(--text-bright);
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 2.8em;
  font-weight: 700;
  letter-spacing: -0.5px;
}
.landing-header .tagline {
  font-size: 1.3em;
  color: var(--text-muted);
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
  background-color: var(--content-bg-dark);
}
.description-card h2 {
  color: var(--primary-accent);
  margin-top: 0;
  margin-bottom: 15px;
  border-bottom: 1px solid var(--border-dark);
  padding-bottom: 10px;
  font-size: 1.6em;
  font-weight: 600;
  text-align: center;
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
  color: var(--text-bright);
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

/* --- Footer --- */
.landing-footer {
  margin-top: 20px;
  width: 100%;
  text-align: center;
}

/* --- Footer Navigation --- */
.footer-nav {
  margin-top: 25px;
  font-size: 0.9em;
}
.footer-nav a {
  color: var(--text-muted);
  text-decoration: none;
  margin: 0 10px;
  transition: color 0.3s ease;
}
.footer-nav a:hover {
  color: var(--primary-accent);
  text-decoration: underline;
}

/* --- New Fancy Button Style (simplified) --- */
.fancy-button {
  background-color: var(--primary-accent);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.fancy-button:hover {
  background-color: var(--primary-accent-hover);
}
</style>
