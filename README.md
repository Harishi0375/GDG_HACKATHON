# Project: DocuMind - Fine-Tuned Document Analysis & Localization for EdTech (GDG Hackathon 2025)

**Event:** GDG on Campus Constructor University Bremen - Build with AI Hackathon (May 2-5, 2025)
**Team Member:** Harishi
**Document Version:** 2.3
**Last Updated:** May 3, 2025

---

## Table of Contents

1.  [Introduction and Vision](#1-introduction-and-vision)
    * [1.1. Problem Statement](#11-problem-statement)
    * [1.2. Project Vision](#12-project-vision)
    * [1.3. Target Audience & Use Cases](#13-target-audience--use-cases)
    * [1.4. Hackathon Goal](#14-hackathon-goal)
2.  [Functional Goals and Scope (MVP)](#2-functional-goals-and-scope-mvp)
    * [2.1. Supported Input](#21-supported-input)
    * [2.2. Core Task: Extraction & Localization](#22-core-task-extraction--localization)
    * [2.3. Output Format](#23-output-format)
    * [2.4. Fine-tuning Objectives](#24-fine-tuning-objectives)
3.  [Architecture and Technology Stack](#3-architecture-and-technology-stack)
    * [3.1. Core Logic & Environment](#31-core-logic--environment)
    * [3.2. AI Platform & Services](#32-ai-platform--services)
    * [3.3. Base Model Selection Process](#33-base-model-selection-process)
    * [3.4. Fine-tuning Strategy (Planned & In Progress)](#34-fine-tuning-strategy-planned--in-progress)
    * [3.5. Key Libraries](#35-key-libraries)
4.  [Development Status & Roadmap](#4-development-status--roadmap)
    * [4.1. Current Status](#41-current-status)
    * [4.2. Next Steps / Roadmap](#42-next-steps--roadmap)
    * [4.3. Development Challenges & Troubleshooting Summary](#43-development-challenges--troubleshooting-summary)
5.  [How to Run Locally (Inference)](#5-how-to-run-locally-inference)
    * [5.1. Prerequisites](#51-prerequisites)
    * [5.2. Setup](#52-setup)
    * [5.3. Execution](#53-execution)
    * [5.4. Note on Fine-tuning](#54-note-on-fine-tuning)
6.  [Project Structure Overview](#6-project-structure-overview)
7.  [Contributing](#7-contributing)
8.  [Resources](#8-resources)
9.  [Troubleshooting Journey & Learnings (Detailed)](#9-troubleshooting-journey--learnings-detailed)
    * [9.1. Challenge: Regional Model Availability & Performance](#91-challenge-regional-model-availability--performance)
    * [9.2. Challenge: Launching Fine-tuning via Python SDK](#92-challenge-launching-fine-tuning-via-python-sdk)
    * [9.3. Challenge: Dataset Format for Fine-tuning](#93-challenge-dataset-format-for-fine-tuning)
    * [9.4. Challenge: Python Environment & SDK Issues](#94-challenge-python-environment--sdk-issues)

---

## 1. Introduction and Vision

### 1.1. Problem Statement

Extracting specific information from diverse documents (notes, papers, forms) is often time-consuming. Furthermore, understanding *where* that information resides within the original document (localization) adds another layer of complexity, particularly crucial in educational and research contexts.

### 1.2. Project Vision

To develop "DocuMind," an AI-powered tool leveraging Google's Gemini models via Vertex AI. The vision is to provide highly accurate information extraction coupled with clear, descriptive localization, specifically **fine-tuned** to meet the demands of educational technology (EdTech) applications.

### 1.3. Target Audience & Use Cases

This tool is designed for users who need to efficiently retrieve and verify information within documents, including:
* **Students:** Analyzing lecture notes, summarizing research papers, reviewing study materials.
* **Educators:** Checking specific answers or data points in assignments (digital or scanned), preparing teaching materials.
* **Researchers:** Extracting data points, references, or key findings from academic papers or reports.

### 1.4. Hackathon Goal

To fulfill the GDG Build with AI Hackathon task by creating a specialized VLLM solution. This involves using a base Gemini model and **launching its fine-tuning** to excel at the core challenge: **extracting information and providing its location** within various document types.

---

## 2. Functional Goals and Scope (MVP)

### 2.1. Supported Input

* **Core Implementation:** The current system processes `.txt`, `.pdf`, and image files (`.png`, `.jpeg`, `.jpg`) located within the `inputs/` directory and its subdirectories. It handles multi-page PDFs by rendering initial pages as images for analysis.
* **Planned Expansion:** The goal is to extend support to include `.docx` (Microsoft Word) and `.latex` files to cover a broader range of common academic and document formats. *Note: Parsing logic for these types is not yet implemented.*
* **Unsupported Types (Blocked):** The system actively ignores audio, video, and other non-document file types based on MIME type and extension checks.

### 2.2. Core Task: Extraction & Localization

* **Base Model Inference:** Utilize the selected `gemini-2.0-flash-lite-001` model via the Vertex AI API for initial analysis. (Note: This will be switched to the fine-tuned model endpoint once training succeeds).
* **Information Extraction:** Extract key information (summary, main points, data, definitions, etc.) based on a structured prompt.
* **Localization Method:** Provide **descriptive localization** (e.g., "Page 3, top left", "Table Row 2, Column 1", "First bar, left") as requested by the prompt and aligned with hackathon guidelines.

### 2.3. Output Format

* Generate structured analysis results in a JSON file (`outputs/results.json`) containing document type, summary, categorized key information, confidence scores, and localization details.

### 2.4. Fine-tuning Objectives

* **Improve Accuracy (Goal B):** Enhance the model's precision in extracting the correct information and providing accurate descriptive localization, especially for complex or handwritten documents common in EdTech.
* **Improve Efficiency (Goal C):** Optimize the model (via fine-tuning) for more efficient processing, potentially enabling faster analysis for individual files and facilitating future batch processing capabilities.

---

## 3. Architecture and Technology Stack

### 3.1. Core Logic & Environment

* **Language:** Python (v3.10+)
* **Environment:** Python Virtual Environment (`venv` or `conda`) with packages listed in `requirements.txt`.
* **Configuration:** `.env` file for `GCP_PROJECT_ID` and `GCP_REGION`; Google Cloud Application Default Credentials (ADC) for authentication.

### 3.2. AI Platform & Services

* **Platform:** Google Cloud Platform (GCP)
* **Core Service:** Vertex AI used for:
    * Model Inference (current base model, switching to tuned model post-training)
    * Model Selection Testing (`test_models.ipynb`)
    * **Fine-tuning Job Execution** (Launched via Console UI)

### 3.3. Base Model Selection Process

* **Challenge:** Needed a capable Gemini model available and performant in a European region (specifically `europe-west4` preferred). Initial checks and subsequent testing revealed limited availability for newer models (Gemini 1.5 series, 2.5 Pro/Flash previews) in these regions. Speed was also a critical factor for a responsive EdTech tool.
* **Methodology:** A systematic testing approach was employed using the `test_models.ipynb` notebook. This script iterated through candidate models (`gemini-2.0-flash-001`, `gemini-2.0-flash-lite-001`, `gemini-1.5-pro-001`, `gemini-2.5-pro-preview-03-25`, `gemini-2.5-flash-preview-04-17`) and target regions (`us-central1`, `europe-west1`, `europe-west4`), performing basic document/image analysis tasks and measuring API call success rates and average processing times.
* **Results:** The tests confirmed that `gemini-2.0-flash-001` and `gemini-2.0-flash-lite-001` were the only models consistently available in the target European regions. The newer Pro and Flash preview models (1.5 and 2.5 series) returned "Model Not Found" errors in `europe-west1` and `europe-west4`. Where available (`us-central1`), the preview models were significantly slower than the 2.0 Flash models. Among the available models, `gemini-2.0-flash-lite-001` demonstrated the lowest latency in `europe-west4`.

    * _Summary Table Screenshot (Illustrative - See notebook output for latest):_
        <p align="center">
          <img src="./graphs/table.png" alt="Model Test Summary Table" width="70%">
        </p>
        *(Note: Table shows results including 'Model Not Found'. Full details in the `outputs/` directory generated by `test_models.ipynb`.)*

    * _Performance Chart Screenshot (Illustrative - See notebook output for latest):_
        <p align="center">
          <img src="./graphs/output.png" alt="Model Test Performance Chart" width="70%">
        </p>
        *(Note: Chart visualizes average processing time only for available model/region combinations.)*

* **Decision:** Based on the crucial requirements of **regional availability** in Europe and **inference speed**, `gemini-2.0-flash-lite-001` deployed in `europe-west4` was confirmed as the optimal base model for fine-tuning. Accuracy improvements for the specific task will be achieved through the fine-tuning process itself.

### 3.4. Fine-tuning Strategy (Planned & In Progress)

* **Motivation:** While the base `gemini-2.0-flash-lite-001` model provides a strong starting point with prompt engineering, fine-tuning is essential to significantly enhance its performance on the specific hackathon task, particularly improving the accuracy and reliability of **descriptive localization** and overall **batch processing efficiency** for typical EdTech documents.
* **Methodology:** Employing **Parameter-Efficient Fine-Tuning (PEFT)** using **LoRA (Low-Rank Adaptation)** via the Vertex AI managed tuning service. This allows adapting the large model efficiently using a smaller dataset and fewer computational resources. A LoRA rank of `4` was chosen as a starting point.
* **Dataset:** A custom dataset was prepared in JSONL format, containing examples mapping input document GCS URIs (`gs://harishi-gdg-tuning-data/data/tuning_data.jsonl`) to the desired structured Markdown output, including manually verified or corrected descriptive localization strings. The correct format (`"contents": [{"role":"user",...}]`) was identified by referencing Google's example notebook `sft_gemini_summarization.ipynb` after initial attempts failed due to format detection errors.
* **Current Status:** The fine-tuning job (`gdg-documind-flash-lite-tuned-console`) has been successfully launched via the **Vertex AI Studio UI** using the prepared dataset (after correcting the JSONL format), targeting 100 training steps with LoRA rank 4. The job is currently running.

### 3.5. Key Libraries

* **Google Cloud:** `google-cloud-aiplatform` (including `vertexai`)
* **PDF Handling:** `PyMuPDF` (fitz)
* **Image Handling:** `Pillow`
* **Configuration:** `python-dotenv`
* **Utilities:** `json`, `logging`, `os`, `re`, `mimetypes`
* **Testing/Analysis:** `pandas`, `matplotlib` (in `test_models.ipynb`)
   

---

## 4. Development Status & Roadmap

### 4.1. Current Status

* **Completed:**
    * Base model selection (`gemini-2.0-flash-lite-001` @ `europe-west4`) via systematic testing.
    * Implementation of the core inference pipeline (`vllm_handler.py`, `utils.py`, `main.py`) using the base model.
    * Refined prompt engineering for structured output (Type, Summary, Key Info & Localization, Category).
    * Recursive handling of input file types (`.txt`, `.pdf`, images) from subdirectories.
    * Initial dataset creation (`tuning_data.jsonl`) with examples formatted correctly and uploaded to GCS.
    * Successful launch of the **LoRA fine-tuning job** via Vertex AI Console UI after troubleshooting dataset format issues.
* **In Progress:**
    * **Fine-tuning Job Execution:** Waiting for the Vertex AI fine-tuning job (`gdg-documind-flash-lite-tuned-console`) to complete.

### 4.2. Next Steps / Roadmap

1.  **Monitor Fine-tuning Job:** Track the job status in the Vertex AI Console until "Succeeded".
2.  **Integrate Tuned Model:** Once successful, obtain the tuned model endpoint/ID and update `src/vllm_handler.py` to use it for inference.
3.  **Evaluate Tuned Model:** Test the fine-tuned model's performance on sample documents. Compare its accuracy (especially localization) against the base model's output. Add more data and retrain if necessary and time permits.
4.  **Implement MVP Logic:** Implement the specific EdTech processing logic in `src/main.py :: process_edtech_analysis` using the output from the fine-tuned model.
5.  *(Optional/Stretch Goal):* Integrate parsing for `.docx` files.
6.  **Finalize Documentation & Video:** Update README with final results/status and prepare the 3-minute presentation video.

### 4.3. Development Challenges & Troubleshooting Summary

*(See Section 9 for detailed descriptions)*

* **Regional Model Availability (Priority: 2 - Resolved)**
* **Base Model Inference Errors (Priority: 2 - Mitigated)**
* **Fine-tuning SDK/API Complexity (Priority: 1 - Bypassed using UI)**
* **Dataset Formatting for Tuning (Priority: 1 - Resolved using examples)**
* **Pipeline Template Discovery & Parameters (Priority: 3 - Bypassed using UI)**

---

## 5. How to Run Locally (Inference)

This describes how to run the current project using the **currently configured model** (base model until fine-tuning completes and `vllm_handler.py` is updated).

### 5.1. Prerequisites

* Python 3.10+
* Git
* Google Cloud SDK (`gcloud`) installed and authenticated.
* A Google Cloud Project with the **Vertex AI API** enabled.

### 5.2. Setup

1.  **Clone:** `git clone https://github.com/Harishi0375/GDG_HACKATHON.git && cd GDG_HACKATHON`
2.  **Environment:** `python -m venv venv && source venv/bin/activate` (or equivalent for your OS)
3.  **Install:** `pip install -r requirements.txt`
4.  **Authenticate:** `gcloud auth application-default login`
5.  **Configure `.env`:**
    * Copy `.env.example` to `.env`.
    * Edit `.env` and set `GCP_PROJECT_ID` to your project ID.
    * Set `GCP_REGION` to the region where the model (base or tuned) is deployed (e.g., `europe-west4`).

### 5.3. Execution

1.  Place input documents (`.txt`, `.pdf`, `.png`, `.jpg`, `.jpeg`) into the `inputs/` directory or its subfolders (`pdf/`, `png/`, etc.). *Note: The `inputs/` folder is gitignored.*
2.  Run the main script: `python src/main.py`
3.  Check console output and the generated `outputs/results.json` file. *Note: The `outputs/` folder is gitignored.*

### 5.4. Note on Fine-tuning

The fine-tuning job itself was launched via the Google Cloud Console UI. Using the *tuned* model requires updating the model identifier in `src/vllm_handler.py` after the tuning job successfully completes.

---

## 6. Project Structure Overview

## File Structure
```
GDG_HACKATHON/
├── .git/
├── .gitignore                # Specifies intentionally untracked files
├── data/                     # Local fine-tuning data prep (Gitignored)
│   └── tuning_data.jsonl
├── graphs/                   # Images/Graphs for README
│   ├── table.png             # Example base model test table
│   └── output.png            # Example base model test graph
├── inputs/                   # Example input documents (Gitignored)
│   ├── pdf/
│   ├── png/
│   ├── jpeg/
│   └── jpg/
├── my_learning/              # Folder for exploratory notebooks (Gitignored)
│   └── ... (e.g., sft_gemini_summarization.ipynb)
├── outputs/                  # Generated output files (Gitignored)
│   ├── results.json          # Output from main.py
│   ├── comparison_results.json # Output from compare_models.ipynb
│   ├── comparison_graph.png    # Output from compare_models.ipynb
│   ├── comparison_table.csv    # Output from compare_models.ipynb
│   └── ..._model_test_outputs_all.json # Output from test_models.ipynb
├── src/                      # Source code directory
│   ├── init.py           # Makes 'src' a Python package
│   ├── config.py             # Loads configuration (.env)
│   ├── main.py               # Main execution script (runs inference)
│   ├── utils.py              # File I/O, PDF/Image handling, file search etc.
│   └── vllm_handler.py       # Handles Vertex AI API interaction (inference)
├── venv/                     # Python virtual environment (if using venv) (Gitignored)
├── .env                      # Local environment variables (Gitignored)
├── .env.example              # Example environment variables file
├── README.md                 # This project overview file
├── requirements.txt          # Python dependencies
├── run_finetuning.py         # Script to launch tuning job via SDK (kept for reference)
├── test_models.ipynb         # Notebook for testing BASE model speed/availability
└── compare_models.ipynb      # Notebook for comparing BASE vs TUNED model performance
```

---

## 7. Contributing

This project was developed solely by Harishi for the GDG Build with AI Hackathon 2025 at Constructor University Bremen. As such, contributions are not being sought at this time.

---

## 8. Resources

* [Vertex AI Generative AI Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/overview)
* [Vertex AI Model Fine-Tuning Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/models/tune-models)
* [Gemini API Documentation](https://ai.google.dev/docs)
* [Paper: Scaling Down to Scale Up: A Guide to Parameter-Efficient Fine-Tuning](https://arxiv.org/abs/2303.15647) (Referenced in `google fine tuning.pdf`)
* [GDG Hackathon Presentation Slides]
* [Example Notebook: Supervised Fine Tuning with Gemini 2.0 Flash for Article Summarization](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/tuning/sft_gemini_summarization.ipynb) (Used to determine correct dataset format)

---

## 9. Troubleshooting Journey & Learnings (Detailed)

This section documents some of the key challenges faced during the hackathon development process and how they were addressed.

### 9.1. Challenge: Regional Model Availability & Performance

* **Problem:** Needed a fast, capable Gemini model available in a European region (`europe-west4` preferred). Initial checks and expanded testing showed limited or no availability for newer/preview models (Gemini 1.5 series, 2.5 Pro Preview, 2.5 Flash Preview) in `europe-west1` and `europe-west4`. Speed differences between available models were also significant.
* **Action:** Developed and executed a systematic test using `test_models.ipynb`. This script iterated through candidate models (including 2.0 Flash/Flash-Lite, 1.5 Pro, 2.5 Pro/Flash Previews) and target regions (`us-central1`, `europe-west1`, `europe-west4`), sending standard document/image analysis prompts and recording success/failure status and average response time.
* **Resolution:** Testing confirmed `gemini-2.0-flash-lite-001` and `gemini-2.0-flash-001` were reliably available in the target EU regions. Newer/preview models were unavailable there. `gemini-2.0-flash-lite-001` was identified as the fastest available option in `europe-west4`. This solidified its choice as the base model, relying on fine-tuning for task-specific accuracy rather than pursuing unavailable or significantly slower preview models.
* **Resource Used:** `test_models.ipynb` script within this repository.


### 9.2. Challenge: Launching Fine-tuning via Python SDK

* **Problem:** Attempting to programmatically launch the supervised LoRA fine-tuning job using the Vertex AI Python SDK (`google-cloud-aiplatform==1.91.0`) encountered multiple `AttributeError`s. The SDK structure appears to have evolved, making documentation examples or previous patterns obsolete for this specific task (Gemini PEFT/LoRA tuning).
* **Attempts:**
    1.  `vertexai.preview.tuning.SupervisedTuningJob.run()`: Failed (`AttributeError: module 'vertexai.preview.tuning' has no attribute 'SupervisedTuningJob'`).
    2.  `vertexai.preview.tuning.supervised_tune()`: Failed (`AttributeError: module 'vertexai.preview.tuning' has no attribute 'supervised_tune'`).
    3.  `GenerativeModel(...).tune_model(...)`: Failed (`AttributeError: module 'vertexai.preview.tuning.sft' has no attribute 'AdapterTuningSpec'`) indicating issues finding the correct classes for defining PEFT parameters (`AdapterTuningSpec`, `LoraConfig`).
    4.  `aiplatform.PipelineJob(...)`: Attempted using a guessed pipeline template URI and direct parameters, but failure likely without the correct template definition and parameter names.
* **Resolution:** Due to time constraints and SDK complexity/documentation ambiguity for this specific workflow, the decision was made to **bypass the SDK for job submission** and use the graphical interface instead. The `run_finetuning.py` script is kept for reference of the attempted methods.
* **Resources Used:** Official Vertex AI SDK documentation (searched), Google Search, trial-and-error with `run_finetuning.py`.

### 9.3. Challenge: Dataset Format for Fine-tuning

* **Problem:** The initial attempt to launch the fine-tuning job via the **Vertex AI Studio UI** failed with a "Failed to detect the dataset format" error. This indicated that the initial JSONL structure (`{"input_content_uri": "...", "output_text": "..."}`) was incorrect.
* **Action:** Needed to identify the exact JSONL schema expected by the Vertex AI tuning service for multimodal Gemini models.
* **Resolution:** Examined the structure used in Google's official example notebooks for Gemini supervised fine-tuning. The notebook `sft_gemini_summarization.ipynb` showed the correct format uses a `"contents"` array with `"role": "user"` and `"role": "model"` objects, where the input file is specified under `user -> parts -> fileData` (with `mime_type` and `file_uri`) and the target output under `model -> parts -> text`. The local `tuning_data.jsonl` file was reformatted accordingly.
* **Resource Used:** [Example Notebook: Supervised Fine Tuning with Gemini 2.0 Flash for Article Summarization](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/tuning/sft_gemini_summarization.ipynb) (referenced via file upload).


### 9.4. Challenge: Python Environment & SDK Issues

* **Problem:** Encountered several Python errors during development and testing within the Jupyter notebooks (`test_models.ipynb`, `compare_models.ipynb`), including `ModuleNotFoundError` for project modules (`config`, `utils`) and `AttributeError` or `TypeError` when calling Vertex AI SDK functions (`from_pretrained`, unexpected keyword arguments) even after confirming the SDK version was up-to-date.
* **Action:** Debugged path calculations, verified SDK versions (`pip show google-cloud-aiplatform`), checked function signatures (`inspect.signature`), and ensured correct argument names and dictionary keys were used (e.g., `image_paths` vs `pdf_paths`, `avg_time_ms` vs `Avg Time (ms)`). Restarting the Jupyter kernel frequently was necessary after code changes.
* **Resolution:** Path issues were resolved by ensuring the notebook execution context was correct relative to the `src` directory or by explicitly setting the project root path. SDK errors like the persistent `AttributeError: ... has no attribute 'from_pretrained'` were ultimately resolved by **cleanly recreating the Conda environment** (`pytorch_env`) and reinstalling the necessary libraries (`google-cloud-aiplatform`, `pandas`, `matplotlib`, etc.), suggesting a potential corruption or conflict in the previous environment setup. Consistent use of lowercase dictionary keys resolved the `KeyError` issues in DataFrame manipulation.
* **Resources Used:** Python `os`, `sys`, `inspect` modules, `pip`, `conda` environment management, debugging print statements, kernel restarts.
