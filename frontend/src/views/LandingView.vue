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
/* --- Theme Variables (Light Theme) --- */
:root {
  --bg-color: #f8f9fa; /* Light grey background */
  --content-bg-color: #ffffff; /* White content area */
  --description-bg-color: #ffffff; /* White card background (can be same as content) */
  --text-color: #212529; /* Dark primary text */
  --text-secondary-color: #6c757d; /* Medium grey secondary text */
  --primary-color: #007bff; /* Standard blue accent */
  --border-color: #dee2e6; /* Light grey border */
  --shadow-color: rgba(0, 0, 0, 0.1); /* Lighter shadow */
  --button-initial-bg: #343a40; /* Dark initial button background */
  --button-text-initial: #ffffff; /* Light initial button text */
  --button-text-hover: #ffffff; /* Light hover button text */
  --button-bg-hover: var(--primary-color); /* Blue hover background */
  --button-shadow-hover: rgba(0, 123, 255, 0.3); /* Blue glow */
}

/* --- Base Layout --- */
.landing-page {
  display: flex;
  flex-direction: column;
  justify-content: center; /* Vertical centering */
  align-items: center; /* Horizontal centering */
  min-height: 100vh; /* Ensure it takes full viewport height */
  width: 100%;
  padding: 40px 20px; /* Adjusted padding */
  box-sizing: border-box;
  background-color: var(--bg-color);
  color: var(--text-color); /* Base text color for the page */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
}

/* --- Content Wrapper --- */
.content-container {
  max-width: 800px;
  width: 100%;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 30px;
  background-color: var(--content-bg-color);
  padding: 40px 50px;
  border-radius: 12px; /* Slightly adjusted radius */
  box-shadow: 0 4px 15px var(--shadow-color);
  border: 1px solid var(--border-color);
}

/* --- Header --- */
.landing-header h1 {
  color: var(--text-color); /* Use main dark text color */
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 2.8em; /* Slightly adjusted size */
  font-weight: 700;
  letter-spacing: -0.5px;
}

.landing-header .tagline {
  font-size: 1.3em; /* Slightly adjusted size */
  color: var(--text-secondary-color); /* Use secondary grey */
  margin-bottom: 0;
  font-weight: 400; /* Adjusted weight */
}

/* --- Description Section --- */
.description-section {
  width: 100%;
}

.description-card {
  padding: 0; /* Keep padding within content-container */
  text-align: left; /* Keep text left-aligned here */
  background-color: var(--description-bg-color); /* Explicitly set */
}

.description-card h2 {
  color: var(--primary-color); /* Use accent color for headings */
  margin-top: 0;
  margin-bottom: 15px; /* Adjusted margin */
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
  font-size: 1.6em; /* Adjusted size */
  font-weight: 600;
}

.divider {
    border: none;
    height: 1px;
    background-color: var(--border-color);
    margin: 30px 0;
}

.description-card ul {
    list-style-position: outside;
    padding-left: 25px;
    color: var(--text-secondary-color); /* Use secondary grey */
    margin-top: 15px; /* Adjusted margin */
}
.description-card ul li strong {
    color: var(--text-color); /* Use main dark text */
}

.description-card li {
    margin-bottom: 12px; /* Adjusted margin */
    line-height: 1.6;
}

.description-card p {
    text-align: left;
    line-height: 1.6;
    color: var(--text-secondary-color); /* Use secondary grey */
    margin-top: 15px; /* Adjusted margin */
    margin-bottom: 0;
}
.description-card p:first-of-type {
    margin-top: 0; /* Remove top margin for first paragraph after h2 */
}

.description-card p em {
    color: var(--primary-color); /* Keep accent for emphasis */
    font-style: normal;
    font-weight: 600;
}

/* --- Footer / Button Area --- */
.landing-footer {
    margin-top: 20px; /* Adjusted margin */
    width: 100%;
    text-align: center; /* Ensure button is centered if needed */
}

/* --- Fancy Button Styles (Adapted for Light Theme) --- */
.fancy-button {
  display: inline-block;
  border: none;
  position: relative;
  width: 220px;
  height: 73px;
  padding: 0;
  z-index: 2;
  /* Mask shape - DO NOT REMOVE THE DATA URI */
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='868' width='2500' viewBox='0 0 726 252.17'%3E%3Cpath d='M483.92 0S481.38 24.71 466 40.11c-11.74 11.74-24.09 12.66-40.26 15.07-9.42 1.41-29.7 3.77-34.81-.79-2.37-2.11-3-21-3.22-27.62-.21-6.92-1.36-16.52-2.82-18-.75 3.06-2.49 11.53-3.09 13.61S378.49 34.3 378 36a85.13 85.13 0 0 0-30.09 0c-.46-1.67-3.17-11.48-3.77-13.56s-2.34-10.55-3.09-13.61c-1.45 1.45-2.61 11.05-2.82 18-.21 6.67-.84 25.51-3.22 27.62-5.11 4.56-25.38 2.2-34.8.79-16.16-2.47-28.51-3.39-40.21-15.13C244.57 24.71 242 0 242 0H0s69.52 22.74 97.52 68.59c16.56 27.11 14.14 58.49 9.92 74.73C170 140 221.46 140 273 158.57c69.23 24.93 83.2 76.19 90 93.6 6.77-17.41 20.75-68.67 90-93.6 51.54-18.56 103-18.59 165.56-15.25-4.21-16.24-6.63-47.62 9.93-74.73C656.43 22.74 726 0 726 0z'/%3E%3C/svg%3E") no-repeat center center;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='868' width='2500' viewBox='0 0 726 252.17'%3E%3Cpath d='M483.92 0S481.38 24.71 466 40.11c-11.74 11.74-24.09 12.66-40.26 15.07-9.42 1.41-29.7 3.77-34.81-.79-2.37-2.11-3-21-3.22-27.62-.21-6.92-1.36-16.52-2.82-18-.75 3.06-2.49 11.53-3.09 13.61S378.49 34.3 378 36a85.13 85.13 0 0 0-30.09 0c-.46-1.67-3.17-11.48-3.77-13.56s-2.34-10.55-3.09-13.61c-1.45 1.45-2.61 11.05-2.82 18-.21 6.67-.84 25.51-3.22 27.62-5.11 4.56-25.38 2.2-34.8.79-16.16-2.47-28.51-3.39-40.21-15.13C244.57 24.71 242 0 242 0H0s69.52 22.74 97.52 68.59c16.56 27.11 14.14 58.49 9.92 74.73C170 140 221.46 140 273 158.57c69.23 24.93 83.2 76.19 90 93.6 6.77-17.41 20.75-68.67 90-93.6 51.54-18.56 103-18.59 165.56-15.25-4.21-16.24-6.63-47.62 9.93-74.73C656.43 22.74 726 0 726 0z'/%3E%3C/svg%3E") no-repeat center center;
  -webkit-mask-size: contain;
  mask-size: contain;
  cursor: pointer;
  background-color: var(--button-initial-bg); /* Initial background (dark) */
  transform: translateY(0px);
  transition: transform 0.2s ease, background-color 0.6s ease; /* Slightly faster bg transition */
}
.fancy-button:hover {
    transform: translateY(-3px);
    background-color: var(--button-bg-hover); /* Background on hover (blue) */
}
.fancy-button:active {
    transform: translateY(0px);
}

/* Glow effect using ::after */
.fancy-button::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  box-shadow: 0px 0px 0px 0px var(--button-shadow-hover);
  opacity: 0;
  transition: box-shadow 0.6s ease-out, opacity 0.6s ease-out; /* Match bg transition */
  z-index: 1;
  pointer-events: none;
   -webkit-mask: inherit; /* Inherit mask for glow */
   mask: inherit;
}

.fancy-button:hover::after {
  opacity: 1;
  box-shadow: 0px 0px 35px 10px var(--button-shadow-hover); /* Adjusted glow size */
}

/* Text Styling */
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
  color: var(--button-text-initial); /* Initial text color (light) */
  transition: color 0.6s ease-out; /* Match bg transition */
  z-index: 3; /* Text on top */
}

.fancy-button:hover span {
  color: var(--button-text-hover); /* Hover text color (light) */
}
/* End Fancy Button Styles */

</style>