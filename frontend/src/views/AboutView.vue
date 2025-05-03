<template>
    <div class="about-page">
      <div class="content-wrapper">
        <h1>About CLU (Codified Likeness Utility)</h1>
  
        <section class="about-section">
          <h2>The Project</h2>
          <p>
            CLU (Codified Likeness Utility) is an AI-powered tool developed for the <strong>GDG Build with AI Hackathon 2025</strong> at Constructor University Bremen (May 2-5). The project vision is to provide highly accurate information extraction coupled with clear, descriptive localization, specifically fine-tuned for educational technology (EdTech) applications.
          </p>
          <p>
            It leverages Google's Gemini models, fine-tuned on Vertex AI, to create a specialized Vision-Language Large Model (VLLM). This VLLM excels at extracting key information (summaries, main points, data, definitions) from various documents (PDF, PNG, JPEG) like lecture notes, research papers, and forms, and importantly, <strong>localizing where</strong> that information was found.
          </p>
          <p>
            The backend is built with Python (Flask, Vertex AI SDK) and the frontend with Vue.js. The currently deployed fine-tuned model is based on `gemini-2.0-flash-lite-001`.
          </p>
        </section>
  
        <section class="about-section target-audience-section">
           <h2>Target Audience & Use Cases</h2>
            <ul>
              <li><strong>Students:</strong> Analyzing lecture notes, summarizing research papers, reviewing study materials.</li>
              <li><strong>Educators:</strong> Checking specific answers or data points in assignments, preparing teaching materials.</li>
              <li><strong>Researchers:</strong> Extracting data points, references, or key findings from academic papers.</li>
            </ul>
        </section>
  
        <section class="about-section owner-section">
          <h2>The Owner & Developer</h2>
          <div class="owner-details">
            <div class="photo-placeholder">
               <img src="@/assets/photo.jpg" alt="Harishi Velavan">
            </div>
            <div class="owner-info">
              <p><strong>Harishi Velavan</strong></p>
              <p>This project was solely developed by Harishi during the GDG Hackathon 2025.</p>
              <div class="links">
                <a :href="githubRepoUrl" target="_blank" rel="noopener noreferrer">GitHub Repository</a> |
                <a :href="linkedinUrl" target="_blank" rel="noopener noreferrer">LinkedIn</a>
              </div>
            </div>
          </div>
        </section>
  
         <nav class="footer-nav">
            <RouterLink to="/">Home</RouterLink> |
            <RouterLink to="/license">License</RouterLink>
          </nav>
  
      </div>
    </div>
  </template>
  
  <script setup>
  // Import RouterLink for navigation
  import { RouterLink } from 'vue-router';
  
  // Define constants for links
  const githubRepoUrl = "https://github.com/Harishi0375/GDG_HACKATHON";
  const linkedinUrl = "https://www.linkedin.com/in/harishi-velavan-585164294/";
  
  // No other script logic needed for this static page
  </script>
  
  <style scoped>
  /* Re-using similar dark theme styles */
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
  .about-page {
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
  .about-section {
    margin-bottom: 2rem;
    text-align: left; /* Left-align paragraph text */
  }
  
  .about-section h2 {
    color: var(--primary-accent);
    border-bottom: 1px solid var(--border-dark);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    text-align: center; /* Center section headings */
  }
  
  .about-section p, .about-section ul {
    line-height: 1.6;
    color: var(--text-muted);
    margin-bottom: 1rem;
  }
  
  .about-section ul {
    list-style: disc; /* Use bullets for audience list */
    padding-left: 25px; /* Indent list */
  }
  
  .about-section li {
    margin-bottom: 0.5rem;
  }
  
  .about-section li strong {
    color: var(--text-bright);
  }
  
  /* Specific styling for the owner section */
  .owner-section .owner-details {
    display: flex;
    flex-direction: column; /* Stack photo and info vertically on small screens */
    align-items: center; /* Center items */
    gap: 20px;
    margin-top: 1.5rem;
    text-align: center; /* Center text in this section */
  }
  
  /* Media query for larger screens */
  @media (min-width: 600px) {
    .owner-section .owner-details {
      flex-direction: row; /* Side-by-side layout on larger screens */
      text-align: left; /* Align text left on larger screens */
    }
  }
  
  
  .photo-placeholder {
    width: 120px; /* Slightly larger photo */
    height: 120px;
    background-color: var(--border-dark); /* Fallback background */
    border-radius: 50%; /* Circular */
    display: flex;
    justify-content: center;
    align-items: center;
    color: var(--text-muted);
    font-size: 0.9em;
    flex-shrink: 0;
    overflow: hidden; /* Important for containing the img */
    border: 2px solid var(--border-dark); /* Optional border */
  }
  
  /* Style the actual image */
  .photo-placeholder img {
    width: 100%;
    height: 100%;
    object-fit: cover; /* Ensure image covers the circle without distortion */
    display: block; /* Remove potential extra space below image */
  }
  
  
  .owner-info {
    /* No specific styles needed now, alignment handled by flex parent */
  }
  
  .owner-info p {
    margin-bottom: 0.5rem;
    color: var(--text-muted); /* Muted text for description */
  }
  
  .owner-info strong {
     color: var(--text-bright); /* Bright text for the name */
     font-size: 1.1em; /* Slightly larger name */
  }
  
  /* Styling for the links */
  .links {
    margin-top: 1rem;
  }
  
  .links a {
    color: var(--primary-accent);
    text-decoration: none;
    margin: 0 10px; /* Space out links */
    transition: color 0.3s ease;
  }
  .links a:hover {
    text-decoration: underline;
    color: var(--text-bright); /* Brighten on hover */
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