<template>
    <div class="prompt-view-dark">
      <div class="results-area" @dragover.prevent="dragOver" @dragleave.prevent="dragLeave" @drop.prevent="handleDrop">
        <div v-if="isDragging" class="drop-overlay">
            Drop files here...
        </div>
  
        <div v-if="isLoading && !analysisResult" class="loading-indicator">
          <p>Processing...</p>
          <div class="spinner"></div>
        </div>
        <div v-if="error" class="error-message">
            <p>⚠️ Error: {{ error }}</p>
        </div>
        <div v-if="analysisResult" class="analysis-output">
          <pre>{{ analysisResult }}</pre>
        </div>
        <div v-if="!analysisResult && !isLoading && !error" class="placeholder">
            <img src="@/assets/clu_logo_placeholder.png" alt="CLU Logo" class="placeholder-logo"/> <p>Upload documents (PDF, PNG, JPG, DOCX) and add a prompt below.</p>
        </div>
      </div>
  
      <div class="input-area">
         <div v-if="selectedFiles.length > 0" class="file-list">
           <div v-for="(file, index) in selectedFiles" :key="file.name + index" class="file-item">
              <span class="file-icon">{{ getFileIcon(file.type) }}</span>
              <span class="file-name" :title="file.name">{{ file.name }}</span>
              <span class="file-size">({{ formatFileSize(file.size) }})</span>
              <button @click="removeFile(index)" class="remove-button" title="Remove file">×</button>
           </div>
         </div>
         <div class="input-controls">
              <label for="file-upload" class="file-upload-button" title="Add Files">
                  📎 </label>
              <input
                id="file-upload"
                type="file"
                multiple
                @change="handleFileChange"
                accept=".pdf,.png,.jpg,.jpeg,.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              />
              <textarea
                  v-model="textPrompt"
                  placeholder="Ask something about the document(s)..."
                  class="prompt-textarea"
                  rows="1"
                  @input="autoGrowTextarea"
                  @keydown.enter.prevent="handleEnterKey"
              ></textarea>
              <button @click="analyzeDocuments" :disabled="selectedFiles.length === 0 || isLoading" class="analyze-button-main" title="Analyze">
                ➤ </button>
         </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, nextTick } from 'vue';
  
  // --- Reactive State ---
  const selectedFiles = ref([]); // Array to hold multiple File objects
  const textPrompt = ref(''); // For the text input
  const isLoading = ref(false);
  const analysisResult = ref(''); // Display latest result simply for now
  const error = ref('');
  const isDragging = ref(false); // For drag-and-drop visual feedback
  
  // --- File Handling ---
  const handleFileChange = (event) => {
    addFiles(event.target.files);
    event.target.value = null; // Reset input to allow selecting the same file again
  };
  
  const handleDrop = (event) => {
      isDragging.value = false;
      addFiles(event.dataTransfer.files);
  };
  
  const addFiles = (files) => {
      error.value = '';
      // analysisResult.value = ''; // Optionally clear results when new files are added
      const newFiles = Array.from(files);
      newFiles.forEach(newFile => {
          // Check if file type is allowed
          const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
          if (!allowedTypes.includes(newFile.type)) {
              error.value = `File type not supported: ${newFile.name} (${newFile.type})`;
              return; // Skip this file
          }
          // Prevent duplicates
          if (!selectedFiles.value.some(existingFile => existingFile.name === newFile.name && existingFile.size === newFile.size)) {
              selectedFiles.value.push(newFile);
          }
      });
  }
  
  const removeFile = (index) => {
      selectedFiles.value.splice(index, 1);
  };
  
  // Provide simple icons based on MIME type
  const getFileIcon = (mimeType) => {
      if (mimeType.startsWith('image/')) return '🖼️';
      if (mimeType === 'application/pdf') return '📄';
      if (mimeType.includes('wordprocessingml')) return '📝';
      return '❓';
  };
  
  // Format file size
  const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB']; // Simplified sizes
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };
  
  // --- Drag and Drop Visuals ---
  const dragOver = () => { isDragging.value = true; };
  const dragLeave = () => { isDragging.value = false; };
  
  // --- Textarea Auto-Grow ---
  const autoGrowTextarea = (event) => {
      const textarea = event.target;
      textarea.style.height = 'auto'; // Reset height
      textarea.style.height = (textarea.scrollHeight) + 'px'; // Set to scroll height
  };
  
  // --- Analysis Trigger ---
  const handleEnterKey = (event) => {
      if (!event.shiftKey) { // Trigger analysis if Enter is pressed without Shift
          analyzeDocuments();
      }
      // Allow Shift+Enter for new lines (default textarea behavior)
  };
  
  const analyzeDocuments = async () => {
    if (selectedFiles.value.length === 0) {
      error.value = 'Please select one or more files.';
      return;
    }
  
    isLoading.value = true;
    analysisResult.value = ''; // Clear previous result before new analysis
    error.value = '';
  
    console.log(`Analyzing ${selectedFiles.value.length} files with prompt: "${textPrompt.value}"`);
    const formData = new FormData();
    selectedFiles.value.forEach((file) => {
      formData.append('files', file); // Backend needs to handle multiple files with this key
    });
    // Include the text prompt if it's not empty
    if (textPrompt.value.trim()) {
        formData.append('prompt', textPrompt.value.trim());
    }
  
    try {
      // ** IMPORTANT: Replace with your actual backend endpoint **
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
        // Add headers if needed (e.g., authentication)
      });
  
      if (!response.ok) {
         let errorText = `HTTP error! Status: ${response.status}`;
          try {
              const errorData = await response.json();
              errorText = errorData.detail || errorData.error || errorData.message || errorText; // Check common error keys
          } catch (e) {
              errorText = await response.text() || errorText;
          }
          throw new Error(errorText);
      }
  
      const data = await response.json();
      // Display the analysis result (adjust based on your backend response structure)
      if (data.analysis) {
          analysisResult.value = typeof data.analysis === 'string' ? data.analysis : JSON.stringify(data.analysis, null, 2);
      } else {
           analysisResult.value = JSON.stringify(data, null, 2); // Fallback
      }
      // Clear prompt and files after successful analysis? Optional.
      // textPrompt.value = '';
      // selectedFiles.value = [];
  
    } catch (err) {
      console.error('Error analyzing documents:', err);
      error.value = `Analysis failed: ${err.message}`;
      analysisResult.value = ''; // Clear results on error
    } finally {
      isLoading.value = false;
    }
  };
  
  </script>
  
  <style scoped>
  /* Dark Mode Theme */
  :root {
    --bg-dark: #1e1e1e;
    --bg-light: #2a2a2a;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --accent-color: #42d392; /* Vue green */
    --accent-hover: #34a853;
    --border-color: #444;
    --error-bg: #4d2f2f;
    --error-text: #ffcdd2;
    --error-border: #8f4b4b;
    --button-disabled: #4caf50; /* Darker green */
  }
  
  .prompt-view-dark {
    display: flex;
    flex-direction: column;
    height: 100vh; /* Full viewport height */
    width: 100%;
    margin: 0;
    padding: 0; /* Remove padding */
    box-sizing: border-box;
    background-color: var(--bg-dark);
    color: var(--text-primary);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  
  .results-area {
    flex-grow: 1;
    overflow-y: auto;
    padding: 25px;
    background-color: var(--bg-dark); /* Match parent */
    border-bottom: 1px solid var(--border-color); /* Separator */
    position: relative;
    display: flex; /* Use flex to center placeholder */
    justify-content: center; /* Center horizontally */
    align-items: center; /* Center vertically */
    text-align: center;
  }
  .drop-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(66, 211, 146, 0.2); /* Semi-transparent accent */
      border: 3px dashed var(--accent-color);
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 1.5em;
      color: var(--accent-color);
      z-index: 10;
      pointer-events: none; /* Allow drop event to reach underlying element */
  }
  
  
  .placeholder {
      color: var(--text-secondary);
  }
  .placeholder-logo {
      max-width: 100px; /* Adjust size */
      opacity: 0.5;
      margin-bottom: 15px;
  }
  
  
  .loading-indicator {
    /* Styles from before, centered by parent flex */
    color: var(--text-secondary);
  }
  .spinner {
      border: 4px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top: 4px solid var(--accent-color);
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 20px auto;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  
  .error-message {
      color: var(--error-text);
      background-color: var(--error-bg);
      padding: 15px 25px;
      border-radius: 5px;
      border: 1px solid var(--error-border);
      width: fit-content;
      max-width: 90%;
       /* Centered by parent flex */
  }
  
  .analysis-output {
      width: 100%; /* Take full width */
      height: 100%; /* Take full height */
      overflow-y: auto; /* Scroll if content overflows */
      text-align: left; /* Align text left */
  }
  
  .analysis-output h2 {
      text-align: left; /* Align heading left */
      margin-bottom: 15px;
      color: var(--text-primary);
      padding-bottom: 10px;
      border-bottom: 1px solid var(--border-color);
  }
  
  .analysis-output pre {
      background-color: var(--bg-light); /* Slightly lighter dark */
      border: 1px solid var(--border-color);
      border-radius: 4px;
      padding: 15px;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.95em;
      color: var(--text-primary);
      max-height: none; /* Remove max-height if results-area scrolls */
      overflow-y: visible; /* No scrollbar needed here if parent scrolls */
  }
  
  .input-area {
    padding: 15px 20px;
    background-color: var(--bg-light);
    border-top: 1px solid var(--border-color);
    box-shadow: 0 -2px 5px rgba(0,0,0,0.2);
  }
  
  .file-list {
      max-height: 80px; /* Adjust as needed */
      overflow-y: auto;
      margin-bottom: 10px;
      padding: 8px;
      background-color: var(--bg-dark); /* Darker list background */
      border-radius: 4px;
      border: 1px solid var(--border-color);
  }
  .file-item {
      display: flex;
      align-items: center;
      padding: 4px 6px;
      background-color: var(--bg-light);
      border-radius: 3px;
      margin-bottom: 4px;
      color: var(--text-secondary);
      font-size: 0.85em;
  }
  .file-icon {
      margin-right: 8px;
      font-size: 1.1em;
  }
  .file-name {
      flex-grow: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-right: 5px;
  }
  .file-size {
      margin-right: 5px;
      white-space: nowrap;
      color: #888;
  }
  .remove-button {
      background: none;
      border: none;
      color: #888;
      font-size: 1.3em;
      cursor: pointer;
      padding: 0 5px;
      line-height: 1;
  }
  .remove-button:hover {
      color: #ff6b6b; /* Reddish for remove */
  }
  
  .input-controls {
      display: flex;
      align-items: flex-end; /* Align items to bottom for textarea grow */
      gap: 10px;
  }
  
  .file-upload-button {
    padding: 8px 12px;
    background-color: #3a3a3a; /* Darker button */
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    font-size: 1.2em; /* Larger icon */
  }
  
  .file-upload-button:hover {
    background-color: #4a4a4a;
    color: var(--text-primary);
  }
  
  .prompt-textarea {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid var(--border-color);
    border-radius: 5px;
    background-color: var(--bg-dark); /* Match area background */
    color: var(--text-primary);
    resize: none; /* Disable manual resize */
    min-height: 24px; /* Start small */
    line-height: 1.4;
    max-height: 150px; /* Limit max height */
    overflow-y: auto; /* Add scroll if needed */
    font-family: inherit;
    font-size: 1em;
  }
  .prompt-textarea::placeholder {
      color: #666;
  }
  
  .analyze-button-main {
    padding: 8px 15px;
    background-color: var(--accent-color);
    color: #111; /* Dark text on accent button */
    border: none;
    border-radius: 50%; /* Make it round */
    font-size: 1.3em; /* Larger icon */
    cursor: pointer;
    transition: background-color 0.3s ease;
    line-height: 1; /* Ensure icon is centered */
    height: 40px; /* Match textarea approx height */
    width: 40px;
  }
  
  .analyze-button-main:disabled {
    background-color: #338a5f;
    cursor: not-allowed;
    opacity: 0.6;
  }
  
  .analyze-button-main:not(:disabled):hover {
    background-color: var(--accent-hover);
  }
  
  input[type="file"] {
    display: none;
  }
  </style>