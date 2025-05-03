<template>
  <div class="prompt-view-dark">
    <div
      class="results-area"
      @dragover.prevent="dragOver"
      @dragleave.prevent="dragLeave"
      @drop.prevent="handleDrop"
    >
      <div v-if="isDragging" class="drop-overlay">
          Drop files here...
      </div>

      <div v-if="isLoading && !analysisResult && !error" class="loading-indicator">
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
          <img src="@/assets/clu_logo_placeholder.png" alt="CLU Logo" class="placeholder-logo"/>
          <p>Upload documents (PDF, PNG, JPG, DOCX) and add a prompt below.</p>
      </div>
    </div>

    <div class="input-area">
       <div v-if="selectedFiles.length > 0" class="file-list">
         <div v-for="(file, index) in selectedFiles" :key="file.name + index" class="file-item">
            <span class="file-icon">{{ getFileIcon(file.type || file.name) }}</span> <span class="file-name" :title="file.name">{{ file.name }}</span>
            <span class="file-size">({{ formatFileSize(file.size) }})</span>
            <button @click="removeFile(index)" class="remove-button" title="Remove file">×</button>
         </div>
       </div>

       <div class="input-controls">
            <label for="file-upload" class="file-upload-button" title="Add Files">
                📎
            </label>
            <input
              id="file-upload"
              type="file"
              multiple
              @change="handleFileChange"
              accept=".pdf,.png,.jpg,.jpeg,.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              style="display: none;"
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
              ➤
            </button>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';

// --- Reactive State ---
const selectedFiles = ref([]); // Array to hold selected File objects
const textPrompt = ref(''); // User's text prompt
const isLoading = ref(false); // Flag for loading state
const analysisResult = ref(''); // Stores the analysis result string
const error = ref(''); // Stores any error message
const isDragging = ref(false); // Flag for drag-over state

// --- API Endpoint ---
// *** IMPORTANT: Replace with your actual backend API URL ***
const apiUrl = 'http://127.0.0.1:5000/api/analyze'; // Example local Flask URL

// --- File Handling ---

// Triggered when files are selected via the input element
const handleFileChange = (event) => {
  addFiles(event.target.files);
  event.target.value = null; // Reset input to allow selecting the same file again
};

// Triggered when files are dropped onto the results area
const handleDrop = (event) => {
    isDragging.value = false; // Turn off drag overlay
    addFiles(event.dataTransfer.files); // Process dropped files
};

// Adds files to the selectedFiles array, checking type and preventing duplicates
const addFiles = (files) => {
    error.value = ''; // Clear previous errors
    const newFiles = Array.from(files); // Convert FileList to array

    newFiles.forEach(newFile => {
        // Define allowed MIME types
        const allowedTypes = [
            'application/pdf',
            'image/png',
            'image/jpeg',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document' // DOCX
        ];
        // Check if the file type is allowed (or if it's a DOCX by extension if type is missing)
        let isAllowed = allowedTypes.some(type => newFile.type && newFile.type.startsWith(type));
        if (!isAllowed && newFile.name.toLowerCase().endsWith('.docx')) {
            isAllowed = true; // Allow .docx by extension
        }

        if (!isAllowed) {
             error.value = `File type not supported: ${newFile.name} (${newFile.type || 'Unknown'})`;
             return; // Skip this file
        }

        // Prevent adding duplicate files (same name and size)
        if (!selectedFiles.value.some(existingFile => existingFile.name === newFile.name && existingFile.size === newFile.size)) {
            selectedFiles.value.push(newFile);
        }
    });
}

// Removes a file from the selectedFiles array by index
const removeFile = (index) => {
    selectedFiles.value.splice(index, 1);
};

// Returns an emoji icon based on file type or name extension
const getFileIcon = (mimeTypeOrName) => {
    const name = typeof mimeTypeOrName === 'string' ? mimeTypeOrName.toLowerCase() : '';
    const type = typeof mimeTypeOrName === 'string' && mimeTypeOrName.includes('/') ? mimeTypeOrName : ''; // Check if it looks like a MIME type

    if (type.startsWith('image/')) return '🖼️'; // Image icon
    if (type === 'application/pdf' || name.endsWith('.pdf')) return '📄'; // PDF icon
    if (type.includes('wordprocessingml') || name.endsWith('.docx')) return '📝'; // DOCX icon
    if (type.startsWith('text/') || name.endsWith('.txt')) return '📜'; // Text icon
    return '❓'; // Default unknown icon
};

// Formats file size from bytes to KB, MB, GB
const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    // Ensure at least one decimal place for KB/MB/GB, none for Bytes
    const formattedSize = parseFloat((bytes / Math.pow(k, i)).toFixed(i === 0 ? 0 : 1));
    return `${formattedSize} ${sizes[i]}`;
};

// --- Drag and Drop Visuals ---

// Sets drag effect and shows overlay when dragging over the target area
const dragOver = (event) => {
    event.dataTransfer.dropEffect = 'copy'; // Indicate a copy operation
    isDragging.value = true;
};

// Hides overlay when dragging leaves the target area
const dragLeave = () => {
    isDragging.value = false;
};

// --- Textarea Auto-Grow ---

// Automatically adjusts textarea height based on content
const autoGrowTextarea = (event) => {
    const textarea = event.target;
    textarea.style.height = 'auto'; // Reset height to calculate scrollHeight correctly
    // Use nextTick to wait for DOM update before setting new height
    nextTick(() => {
      textarea.style.height = (textarea.scrollHeight) + 'px';
    });
};

// --- Analysis Trigger ---

// Handles Enter key press in textarea (triggers analysis if Shift is not held)
const handleEnterKey = (event) => {
    if (!event.shiftKey) { // Only trigger if Shift key is not pressed
        analyzeDocuments();
    }
    // Allows Shift+Enter for new lines (default textarea behavior)
};

// Sends files and prompt to the backend API for analysis
const analyzeDocuments = async () => {
  // Basic validation
  if (selectedFiles.value.length === 0) {
    error.value = 'Please select one or more files.';
    return;
  }
  if (!textPrompt.value.trim()) {
      error.value = 'Please enter a prompt.';
      return;
  }

  // Set loading state and clear previous results/errors
  isLoading.value = true;
  analysisResult.value = '';
  error.value = '';

  console.log(`Analyzing ${selectedFiles.value.length} files with prompt: "${textPrompt.value}"`);

  // Create FormData to send files and prompt
  const formData = new FormData();
  selectedFiles.value.forEach((file) => {
    // The backend expects files under the key 'files'
    formData.append('files', file);
  });
  // The backend expects the prompt under the key 'prompt'
  formData.append('prompt', textPrompt.value.trim());

  try {
    // Make the POST request to the API
    const response = await fetch(apiUrl, {
      method: 'POST',
      body: formData,
      // Headers like 'Content-Type': 'multipart/form-data' are usually set automatically by fetch with FormData
    });

    // Handle non-successful HTTP responses
    if (!response.ok) {
       let errorText = `HTTP error! Status: ${response.status}`;
        try {
            // Try to parse JSON error response from backend
            const errorData = await response.json();
            errorText = errorData.detail || errorData.error || errorData.message || errorText;
        } catch (e) {
             // If response is not JSON or parsing fails, use text response
            const textError = await response.text();
            errorText = textError || errorText; // Use text error if available
        }
        throw new Error(errorText); // Throw error to be caught below
    }

    // Parse the successful JSON response
    const data = await response.json();

    // --- Improved Result Handling ---
    // Check if the expected 'analysis' key exists in the response
    if (data.analysis) {
        // Handle potential array of results (e.g., one per file) or single string result
        if (Array.isArray(data.analysis)) {
            analysisResult.value = data.analysis.map(item =>
                // Format multiple results clearly
                `--- Analysis for ${item.filename || 'file'} ---\n${item.analysis}`
            ).join('\n\n');
        } else {
            // Assign single string result directly
             analysisResult.value = data.analysis;
        }
    } else if (data.error) {
        // Handle structured errors explicitly sent from the backend
        error.value = `Analysis failed: ${data.error}. Details: ${JSON.stringify(data.details || {})}`;
    } else {
         // Fallback for unexpected successful response structure
         error.value = "Received response, but couldn't find 'analysis' key.";
         console.warn("Unexpected response format:", data);
         analysisResult.value = JSON.stringify(data, null, 2); // Show raw response for debugging
    }
    // -----------------------------

  } catch (err) {
    // Handle fetch errors (network issues) or errors thrown from response handling
    console.error('Error analyzing documents:', err);
    error.value = `Analysis failed: ${err.message || 'Network error or server unavailable'}`;
    analysisResult.value = ''; // Ensure result area is cleared on error
  } finally {
    // Always turn off loading state
    isLoading.value = false;
  }
};

</script>

<style scoped>
  /* Dark Mode Theme Variables */
  :root {
    --bg-dark: #1e1e1e; /* Dark background */
    --bg-light: #2a2a2a; /* Slightly lighter background */
    --text-primary: #e0e0e0; /* Primary text (light gray) */
    --text-secondary: #a0a0a0; /* Secondary text (medium gray) */
    --accent-color: #42d392; /* Accent color (Vue green) */
    --accent-hover: #34a853; /* Darker green for hover */
    --border-color: #444; /* Border color */
    --error-bg: #4d2f2f; /* Background for error messages */
    --error-text: #ffcdd2; /* Text color for error messages */
    --error-border: #8f4b4b; /* Border color for error messages */
    --button-disabled: #3b805a; /* Background for disabled button */
    --placeholder-text: #666; /* Color for placeholder text */
  }

  /* Main container for the prompt view */
  .prompt-view-dark {
    display: flex;
    flex-direction: column;
    height: 100vh; /* Full viewport height */
    width: 100%;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    background-color: var(--bg-dark);
    color: var(--text-primary);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  /* Area where results, loading, errors, or placeholder are shown */
  .results-area {
    flex-grow: 1; /* Takes up available vertical space */
    overflow-y: auto; /* Allows scrolling for long results */
    padding: 25px;
    background-color: var(--bg-dark);
    border-bottom: 1px solid var(--border-color);
    position: relative; /* Needed for absolute positioning of drop-overlay */
    display: flex;
    justify-content: center; /* Center placeholder/loading/error horizontally */
    align-items: center; /* Center placeholder/loading/error vertically */
    text-align: center;
  }

  /* Overlay shown when dragging files over the results area */
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
      z-index: 10; /* Ensure it's above other content */
      pointer-events: none; /* Allows drop event to reach underlying element */
  }

  /* Placeholder content (logo and text) */
  .placeholder {
      color: var(--placeholder-text);
       display: flex;
       flex-direction: column;
       align-items: center;
       justify-content: center;
       opacity: 0.7;
  }
  .placeholder-logo {
      max-width: 80px;
      opacity: 0.5;
      margin-bottom: 15px;
  }

  /* Loading indicator text */
  .loading-indicator {
    color: var(--text-secondary);
  }
  /* Spinning animation for loading */
  .spinner {
      border: 4px solid rgba(255, 255, 255, 0.3); /* Light gray border */
      border-radius: 50%;
      border-top: 4px solid var(--accent-color); /* Accent color for spinning part */
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite; /* Animation definition */
      margin: 20px auto; /* Center spinner */
  }

  /* Keyframes for the spinning animation */
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Styling for error messages */
  .error-message {
      color: var(--error-text);
      background-color: var(--error-bg);
      padding: 15px 25px;
      border-radius: 5px;
      border: 1px solid var(--error-border);
      width: fit-content; /* Adjust width to content */
      max-width: 90%; /* Prevent it from becoming too wide */
      margin: auto; /* Helps centering if needed */
  }

  /* Container for the analysis result */
  .analysis-output {
      width: 100%;
      height: 100%;
      overflow-y: auto; /* Allow scrolling within this div if needed, though parent scrolls */
      text-align: left; /* Align analysis text to the left */
      /* Override parent's centering when results are shown */
       justify-content: flex-start;
       align-items: flex-start;
  }

  /* Styling for the <pre> tag containing the analysis result */
  .analysis-output pre {
      background-color: var(--bg-light);
      border: 1px solid var(--border-color);
      border-radius: 4px;
      padding: 15px;
      white-space: pre-wrap; /* Wrap long lines */
      word-wrap: break-word; /* Break long words */
      font-family: 'Courier New', Courier, monospace; /* Monospace font for code-like output */
      font-size: 0.9em;
      color: var(--text-primary);
      width: 100%; /* Take full width */
      box-sizing: border-box; /* Include padding in width */
  }

  /* Area at the bottom containing file list and input controls */
  .input-area {
    padding: 15px 20px;
    background-color: var(--bg-light);
    border-top: 1px solid var(--border-color);
    box-shadow: 0 -2px 5px rgba(0,0,0,0.2); /* Subtle shadow */
  }

  /* Container for the list of selected files */
  .file-list {
      max-height: 80px; /* Limit height and allow scrolling */
      overflow-y: auto;
      margin-bottom: 10px;
      padding: 8px;
      background-color: var(--bg-dark);
      border-radius: 4px;
      border: 1px solid var(--border-color);
  }
  /* Individual file item in the list */
  .file-item {
      display: flex;
      align-items: center;
      padding: 4px 6px;
      background-color: var(--bg-light);
      border-radius: 3px;
      margin-bottom: 4px; /* Space between items */
      color: var(--text-secondary); /* Default text color for item */
      font-size: 0.85em; /* Smaller font size for file list */
  }
  /* File type icon */
  .file-icon {
      margin-right: 8px;
      font-size: 1.1em;
  }
  /* File name */
  .file-name {
      flex-grow: 1; /* Allow name to take available space */
      white-space: nowrap; /* Prevent wrapping */
      overflow: hidden; /* Hide overflow */
      text-overflow: ellipsis; /* Show ellipsis (...) for long names */
      margin-right: 5px;
      color: var(--text-primary); /* Make filename primary color */
  }
  /* File size */
  .file-size {
      margin-right: 5px;
      white-space: nowrap;
      /* --- CHANGE: Use variable for consistency --- */
      color: var(--text-secondary);
  }
  /* Remove file button (X) */
  .remove-button {
      background: none;
      border: none;
      /* --- CHANGE: Use variable for consistency --- */
      color: var(--text-secondary);
      font-size: 1.3em;
      cursor: pointer;
      padding: 0 5px;
      line-height: 1; /* Adjust line height for better vertical alignment */
  }
  .remove-button:hover {
      color: #ff6b6b; /* Red color on hover */
  }

  /* Container for the input controls (upload, textarea, send) */
  .input-controls {
      display: flex;
      align-items: flex-end; /* Align items to the bottom (useful for growing textarea) */
      gap: 10px; /* Space between controls */
  }

  /* Style for the file upload button (label) */
  .file-upload-button {
    padding: 8px 12px;
    background-color: #3a3a3a;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    font-size: 1.2em;
    height: 40px; /* Match button/textarea height */
     display: flex;
     align-items: center;
     justify-content: center;
  }

  .file-upload-button:hover {
    background-color: #4a4a4a; /* Slightly lighter on hover */
    color: var(--text-primary);
  }

  /* Style for the prompt textarea */
  .prompt-textarea {
    flex-grow: 1; /* Allow textarea to take available horizontal space */
    padding: 10px;
    border: 1px solid var(--border-color);
    border-radius: 5px;
    background-color: var(--bg-dark);
    color: var(--text-primary);
    resize: none; /* Disable manual resizing */
    min-height: 40px; /* Minimum height matching buttons */
    line-height: 1.4;
    max-height: 150px; /* Limit maximum height before scrolling */
    overflow-y: auto; /* Allow vertical scrolling */
    font-family: inherit; /* Use the main font */
    font-size: 1em;
    box-sizing: border-box;
  }
  /* Style for the textarea placeholder text */
  .prompt-textarea::placeholder {
      color: var(--placeholder-text);
  }

  /* Style for the main analyze/send button */
  .analyze-button-main {
    padding: 0;
    background-color: var(--accent-color);
    /* --- CHANGE: Use white icon for better contrast --- */
    color: white;
    border: none;
    border-radius: 50%; /* Make it round */
    font-size: 1.3em;
    cursor: pointer;
    transition: background-color 0.3s ease;
    line-height: 1;
    height: 40px; /* Fixed height */
    width: 40px; /* Fixed width */
    flex-shrink: 0; /* Prevent button from shrinking */
     display: flex;
     align-items: center;
     justify-content: center;
  }

  /* Style for the analyze button when disabled */
  .analyze-button-main:disabled {
    background-color: var(--button-disabled);
    cursor: not-allowed;
    opacity: 0.6;
  }

  /* Style for the analyze button on hover (when not disabled) */
  .analyze-button-main:not(:disabled):hover {
    background-color: var(--accent-hover);
  }

</style>
