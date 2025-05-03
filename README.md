# Project: DocuMind - Fine-Tuned Document Analysis & Localization for EdTech (GDG Hackathon 2025)

**Event:** GDG on Campus Constructor University Bremen - Build with AI Hackathon (May 2-5, 2025)
**Team Member:** Harishi
**Document Version:** 2.1
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
    * [3.4. Fine-tuning Strategy (Planned)](#34-fine-tuning-strategy-planned)
    * [3.5. Key Libraries](#35-key-libraries)
4.  [Development Status & Roadmap](#4-development-status--roadmap)
    * [4.1. Current Status](#41-current-status)
    * [4.2. Next Steps / Roadmap](#42-next-steps--roadmap)
    * [4.3. Development Challenges & Troubleshooting](#43-development-challenges--troubleshooting)
5.  [How to Run Locally (Inference)](#5-how-to-run-locally-inference)
    * [5.1. Prerequisites](#51-prerequisites)
    * [5.2. Setup](#52-setup)
    * [5.3. Execution](#53-execution)
    * [5.4. Note on Fine-tuning](#54-note-on-fine-tuning)
6.  [Project Structure Overview](#6-project-structure-overview)
7.  [Contributing](#7-contributing)
8.  [Resources](#8-resources)

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

* **Challenge:** Initial exploration revealed that desired regions (e.g., `europe-west1` to `europe-west4`) had limited availability for many newer Gemini models (1.5 series, 2.5 previews). Additionally, speed was a critical factor for a responsive EdTech tool.
* **Methodology:** A systematic testing approach was employed using the `test_models.ipynb` notebook. This notebook iterated through a list of candidate models and target regions, performing basic image analysis tasks and measuring API call success rates and average processing times.
* **Results:** The tests highlighted significant availability gaps in European regions for preview models. Among the available and stable models, `gemini-2.0-flash-lite-001` emerged as the leading candidate, demonstrating both availability and the lowest latency in the `europe-west4` region.

    * _Summary Table Screenshot:_
      <p align="center">
        <img src="./graphs/table.png" alt="Model Test Summary Table" width="70%">
      </p>
      *(Note: Table shows results including 'Model Not Found' and 'Processing Errors' for unavailable/problematic combinations. Full details in `outputs/model_test_outputs.json`.)*

    * _Performance Chart Screenshot:_
      <p align="center">
        <img src="./graphs/output.png" alt="Model Test Performance Chart" width="70%">
      </p>
      *(Note: Chart visualizes average processing time only for model/region combinations that were available and returned results during testing.)*

* **Decision:** Based on these empirical results, `gemini-2.0-flash-lite-001` deployed in `europe-west4` was selected as the optimal base model for this project, balancing availability, speed, and capability.

### 3.4. Fine-tuning Strategy (Planned & In Progress)

* **Motivation:** While the base `gemini-2.0-flash-lite-001` model provides a strong starting point with prompt engineering, fine-tuning is essential to significantly enhance its performance on the specific hackathon task, particularly improving the accuracy and reliability of **descriptive localization** and overall **batch processing efficiency** for typical EdTech documents.
* **Methodology:** Employing **Parameter-Efficient Fine-Tuning (PEFT)** using **LoRA (Low-Rank Adaptation)** via the Vertex AI managed tuning service. This allows adapting the large model efficiently using a smaller dataset and fewer computational resources. A LoRA rank of `4` was chosen as a starting point.
* **Dataset:** A custom dataset was prepared in JSONL format, containing examples mapping input document GCS URIs (`gs://harishi-gdg-tuning-data/...`) to the desired structured Markdown output, including manually verified or corrected descriptive localization strings. This dataset (`tuning_data.jsonl`) currently contains initial examples and resides in GCS.
* **Current Status:** The fine-tuning job has been successfully launched via the **Vertex AI Studio UI** using the prepared dataset, targeting 100 training steps with LoRA rank 4. The job is currently running.

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
    * Initial dataset creation (`tuning_data.jsonl`) with examples uploaded to GCS.
    * Successful launch of the **LoRA fine-tuning job** via Vertex AI Console UI.
* **In Progress:**
    * **Fine-tuning Job Execution:** Waiting for the Vertex AI fine-tuning job to complete.

### 4.2. Next Steps / Roadmap

1.  **Monitor Fine-tuning Job:** Track the job status in the Vertex AI Console until "Succeeded".
2.  **Integrate Tuned Model:** Once successful, obtain the tuned model endpoint/ID and update `src/vllm_handler.py` to use it for inference.
3.  **Evaluate Tuned Model:** Test the fine-tuned model's performance on sample documents. Compare its accuracy (especially localization) against the base model's output. Add more data and retrain if necessary and time permits.
4.  **Implement MVP Logic:** Implement the specific EdTech processing logic in `src/main.py :: process_edtech_analysis` using the output from the fine-tuned model.
5.  *(Optional/Stretch Goal):* Integrate parsing for `.docx` files.
6.  **Finalize Documentation & Video:** Update README with final results/status and prepare the 3-minute presentation video.

### 4.3. Development Challenges & Troubleshooting

*(This section details challenges encountered during development. See previous response for the detailed text or paste the version you created here.)*

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
2.  **Environment:** `python -m venv venv && source venv/bin/activate` (or equivalent)
3.  **Install:** `pip install -r requirements.txt`
4.  **Authenticate:** `gcloud auth application-default login`
5.  **Configure `.env`:**
    * Copy `.env.example` to `.env`.
    * Edit `.env` and set `GCP_PROJECT_ID` to your project ID.
    * Set `GCP_REGION` to the region where the model (base or tuned) is deployed (e.g., `europe-west4`).

### 5.3. Execution

1.  Place input documents (`.txt`, `.pdf`, `.png`, `.jpg`, `.jpeg`) into the `inputs/` directory or its subfolders (`pdf/`, `png/`, etc.).
2.  Run the main script: `python src/main.py`
3.  Check console output and the generated `outputs/results.json` file.

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
│   ├── table.png
│   └── output.png
├── inputs/                   # Example input documents (Gitignored)
│   ├── pdf/
│   ├── png/
│   ├── jpeg/
│   └── jpg/
├── outputs/                  # Generated output files (Gitignored)
│   ├── results.json
│   └── model_test_outputs.json
├── src/                      # Source code directory
│   ├── __init__.py           # Makes 'src' a Python package
│   ├── config.py             # Loads configuration (.env)
│   ├── main.py               # Main execution script (runs inference)
│   ├── utils.py              # File I/O, PDF parsing, recursive file search etc.
│   └── vllm_handler.py       # Handles Vertex AI API interaction (inference)
├── venv/                     # Python virtual environment (Gitignored)
├── .env                      # Local environment variables (Gitignored)
├── .env.example              # Example environment variables file
├── README.md                 # This project overview file
├── requirements.txt          # Python dependencies
├── run_finetuning.py         # Script to launch tuning job via SDK (kept for reference)
└── test_models.ipynb         # Notebook for testing model speed/availability
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
