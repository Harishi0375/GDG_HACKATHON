<template>
    <div class="license-page">
       <div class="content-wrapper">
        <h1>License Information</h1>
  
        <section class="license-section">
          <h2>Google AI Services (Gemini & Vertex AI)</h2>
          <p>
            This project utilizes Google AI technologies, including Gemini models accessed via the Vertex AI platform.
            The use of these services is subject to Google's terms and conditions. It is important to review these terms, particularly regarding usage rights, limitations, and responsible AI practices.
          </p>
          <p>
            Please refer to the official Google Cloud Platform Terms of Service and the specific terms for Generative AI services for detailed information:
          </p>
          <ul>
            <li>
              <a href="https://cloud.google.com/terms" target="_blank" rel="noopener noreferrer">Google Cloud Platform Terms of Service</a>
            </li>
            <li>
               <a href="https://cloud.google.com/terms/generative-ai" target="_blank" rel="noopener noreferrer">Additional Terms for Generative AI</a>
            </li>
             <li>
               <a href="https://cloud.google.com/vertex-ai/docs/generative-ai/responsible-ai/safety-filters" target="_blank" rel="noopener noreferrer">Vertex AI Safety Filters and Responsible AI</a>
            </li>
             <li>
               <a href="https://ai.google.dev/terms" target="_blank" rel="noopener noreferrer">Google AI Developer Terms</a> (If applicable to any APIs used directly)
            </li>
          </ul>
           <p>
              Usage of the models may also be subject to specific model licenses or acceptable use policies provided by Google.
           </p>
        </section>
  
        <section class="license-section">
          <h2>Project Code (CLU)</h2>
          <p>
            The source code for this specific project (CLU), developed by Harishi Velavan for the GDG Hackathon 2025, is available on GitHub.
          </p>
           <p>
             Please check the repository for the specific license applied to the project code itself (e.g., MIT, Apache 2.0). If no license file (e.g., `LICENSE` or `LICENSE.md`) is present in the root of the repository, standard copyright laws apply, and the code is not open source unless explicitly stated otherwise by the owner.
           </p>
           <p>
             <a :href="githubRepoUrl" target="_blank" rel="noopener noreferrer">CLU GitHub Repository</a>
           </p>
        </section>
  
         <nav class="footer-nav">
            <RouterLink to="/">Home</RouterLink> |
            <RouterLink to="/about">About</RouterLink>
          </nav>
  
      </div>
    </div>
  </template>
  
  <script setup>
  // Import RouterLink for navigation
  import { RouterLink } from 'vue-router';
  
  // Define the repo URL here for easy update
  const githubRepoUrl = "https://github.com/Harishi0375/GDG_HACKATHON";
  </script>
  
  <style scoped>
  /* Using similar dark theme styles */
  :root {
    --bg-dark: #1a1a1a;
    --content-bg-dark: #242424;
    --text-bright: #e4e4e4;
    --text-muted: #a0a0a0;
    --primary-accent: #42d392;
    --border-dark: #444;
    --shadow-dark: rgba(0, 0, 0, 0.4);
  }
  
  /* Centering layout for the entire view */
  .license-page {
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
    /* background-color: var(--bg-dark); */ /* Assuming global background */
  }
  
  /* Container for the main content block */
  .content-wrapper {
    max-width: 800px;
    width: 100%;
    background-color: var(--content-bg-dark);
    padding: 40px 50px;
    border-radius: 12px;
    box-shadow: 0 4px 15px var(--shadow-dark);
    border: 1px solid var(--border-dark);
    text-align: center; /* Center main heading */
  }
  
  h1 {
    color: var(--primary-accent);
    margin-bottom: 2rem;
  }
  
  /* Styling for individual sections */
  .license-section {
    margin-bottom: 2rem;
    text-align: left; /* Left-align paragraph text */
  }
  
  .license-section h2 {
    color: var(--primary-accent);
    border-bottom: 1px solid var(--border-dark);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    text-align: center; /* Center section headings */
  }
  
  .license-section p {
    line-height: 1.6;
    color: var(--text-muted);
    margin-bottom: 1rem;
  }
  
  .license-section ul {
    list-style: disc; /* Use bullets for links */
    padding-left: 25px; /* Indent list */
    color: var(--text-muted);
    margin-bottom: 1rem;
  }
  
  .license-section li {
    margin-bottom: 0.5rem;
  }
  
  .license-section a {
    color: var(--primary-accent);
    text-decoration: none;
  }
  .license-section a:hover {
    text-decoration: underline;
    color: var(--text-bright);
  }
  
  /* Footer navigation styling */
  .footer-nav {
    margin-top: 25px;
    padding-top: 15px;
    border-top: 1px solid var(--border-dark);
    font-size: 0.9em;
    text-align: center;
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
  </style>
  