# Project: DocuMind - Fine-Tuned Document Analysis & Localization for EdTech (GDG Hackathon 2025)

**Event:** GDG on Campus Constructor University Bremen - Build with AI Hackathon (May 2-5, 2025)
**Team Member:** Harishi
**Document Version:** 2.0
**Last Updated:** May 2, 2025

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
    * [3.3. Base Model Selection](#33-base-model-selection)
    * [3.4. Fine-tuning Strategy (Planned)](#34-fine-tuning-strategy-planned)
    * [3.5. Key Libraries](#35-key-libraries)
4.  [Development Status & Roadmap](#4-development-status--roadmap)
    * [4.1. Current Status](#41-current-status)
    * [4.2. Next Steps / Roadmap](#42-next-steps--roadmap)
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

To fulfill the GDG Build with AI Hackathon task by creating a specialized VLLM solution. This involves using a base Gemini model and **planning its fine-tuning** to excel at the core challenge: **extracting information and providing its location** within various document types.

---

## 2. Functional Goals and Scope (MVP)

### 2.1. Supported Input

* **Required Types (Implemented):** Process `.txt`, `.pdf`, `.png`, `.jpeg`, `.jpg` files located in the `inputs/` directory. Handles multi-page PDFs by sending initial pages as images.
* **Unsupported Types (Blocked):** The system currently does not process audio, video, or other non-specified file types. File types like `.docx` or `.latex` require adding specific parsing libraries and are considered potential future enhancements.

### 2.2. Core Task: Extraction & Localization

* **Base Model Inference:** Utilize the selected `gemini-2.0-flash-lite-001` model via the Vertex AI API for initial analysis.
* **Information Extraction:** Extract key information (summary, main points, data, definitions, etc.) based on a structured prompt.
* **Localization Method:** Provide **descriptive localization** (e.g., "Page 3, top left", "Table Row 2, Column 1") as requested by the prompt and aligned with hackathon guidelines.

### 2.3. Output Format

* Generate structured analysis results in a JSON file (`outputs/results.json`) containing document type, summary, categorized key information, confidence scores, and localization details.

### 2.4. Fine-tuning Objectives

* **Improve Accuracy (Goal B):** Enhance the model's precision in extracting the correct information and providing accurate descriptive localization, especially for complex or handwritten documents common in EdTech.
* **Improve Efficiency (Goal C):** Optimize the model (via fine-tuning) for more efficient processing, potentially enabling faster analysis for individual files and facilitating future batch processing capabilities.

---

## 3. Architecture and Technology Stack

### 3.1. Core Logic & Environment

* **Language:** Python (v3.10+)
* **Environment:** Python Virtual Environment (`venv`) with packages listed in `requirements.txt`.
* **Configuration:** `.env` file for GCP Project ID/Region; Google Cloud Application Default Credentials (ADC) for authentication.

### 3.2. AI Platform & Services

* **Platform:** Google Cloud Platform (GCP)
* **Core Service:** Vertex AI used for:
    * Model Inference (current)
    * Model Testing (`test_models.ipynb`)
    * **Planned Fine-tuning Jobs**

### 3.3. Base Model Selection

* **Selected Model:** `gemini-2.0-flash-lite-001`.
* **Rationale:** Chosen based on systematic testing (`test_models.ipynb`) across various Gemini models and regions. `gemini-2.0-flash-lite-001` demonstrated the best combination of **availability and speed** in the target European region (`europe-west4`) during tests.

### 3.4. Fine-tuning Strategy (Planned)

* **Motivation:** While the base `gemini-2.0-flash-lite-001` model provides a strong starting point with prompt engineering, fine-tuning is planned to significantly enhance its performance on the specific hackathon task, particularly improving the accuracy and reliability of **descriptive localization** and overall **batch processing efficiency** for typical EdTech documents.
* **Methodology:** Plan to employ **Parameter-Efficient Fine-Tuning (PEFT)** techniques available on Vertex AI. **LoRA (Low-Rank Adaptation)** is a primary candidate method, recognized for its efficiency in adapting large models.
* **Dataset Requirement:** Successful fine-tuning necessitates creating a specialized dataset. This dataset will consist of representative documents (PDFs, images, text relevant to EdTech) paired with meticulously crafted target outputs in the desired JSON-like format, including accurate **descriptive localization strings** ("Page 3, top-left", etc.) for each extracted piece of information.
* **Current Status:** Fine-tuning is in the **planning and dataset preparation phase**.

### 3.5. Key Libraries

* **Google Cloud:** `google-cloud-aiplatform`
* **PDF Handling:** `PyMuPDF` (fitz)
* **Image Handling:** `Pillow`
* **Configuration:** `python-dotenv`
* **Testing/Analysis:** `pandas`, `matplotlib` (in `test_models.ipynb`)
   

---

## 4. Development Status & Roadmap

### 4.1. Current Status

* **Completed:**
    * Systematic testing of various Gemini models and regions (`test_models.ipynb`).
    * Selection of `gemini-2.0-flash-lite-001` in `europe-west4` as the base model.
    * Implementation of the core inference pipeline (`vllm_handler.py`) using the selected base model.
    * Refined prompt engineering focused on extraction, descriptive localization, and categorization.
    * Handling of input types: `.txt`, `.pdf` (multi-page rendering), images (`.png`, `.jpg`, `.jpeg`).
    * Improved error handling during file processing and API interaction.
    * Structured JSON output generation.
* **In Progress / Planned Next:**
    * **Fine-tuning Planning:** Defining the specific PEFT/LoRA parameters and Vertex AI job configuration.
    * **Dataset Preparation:** Creating or sourcing a suitable dataset with documents and target outputs including descriptive localization for fine-tuning.

### 4.2. Next Steps / Roadmap

1.  **Dataset Finalization:** Complete the creation and formatting of the fine-tuning dataset.
2.  **Fine-tuning Execution:** Configure and launch the fine-tuning job on Vertex AI using the prepared dataset and chosen PEFT method (LoRA).
3.  **Evaluation:** Rigorously evaluate the fine-tuned model's performance compared to the base model, focusing on improvements in extraction accuracy, localization correctness, and potentially processing speed/cost.
4.  **MVP Logic Implementation:** Implement the specific EdTech processing logic in `src/main.py :: process_edtech_analysis` using the output from the (ideally fine-tuned) model.
5.  *(Optional/Stretch Goal):* Integrate parsing for `.docx` files if time permits.
6.  **Documentation & Video:** Finalize project documentation and prepare the 3-minute presentation video for submission.

---

## 5. How to Run Locally (Inference)

This describes how to run the current project using the **base pre-trained model** for inference. Fine-tuning requires separate steps on Google Cloud.

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
    * Set `GCP_REGION` to the region where the chosen model is available (e.g., `europe-west4` for `gemini-2.0-flash-lite-001`).

### 5.3. Execution

1.  Place input documents (`.txt`, `.pdf`, `.png`, `.jpg`, `.jpeg`) into the `inputs/` directory.
2.  Run the main script: `python src/main.py`
3.  Check console output and the generated `outputs/results.json` file.

### 5.4. Note on Fine-tuning

Running the **fine-tuning process** itself is not done via `python src/main.py`. It requires:
* Preparing a dataset in a format suitable for Vertex AI (e.g., JSONL uploaded to GCS).
* Using the Google Cloud Console or `gcloud` CLI / Vertex AI SDK to configure and launch a fine-tuning job, specifying the base model (`gemini-2.0-flash-lite-001`), the dataset location, and PEFT parameters (like LoRA settings).
* Refer to the official [Vertex AI documentation on fine-tuning](https://cloud.google.com/vertex-ai/generative-ai/docs/models/tune-models) for detailed steps.

---

## 6. Project Structure Overview

## File Structure
```
GDG_HACKATHON/
├── .git/
├── .gitignore
├── venv/
├── inputs/             # Input images and text files
│   ├── example_image.jpg
│   └── example_text.txt
├── outputs/            # Extracted information (e.g., JSON)
│   │── results.json
│   └── model_test_outputs.json # Raw outputs from test_models.ipynb
├── src/                # Source code
│   ├── __init__.py
│   ├── main.py         # Main execution script
│   ├── utils.py        # Helper functions
│   ├── vllm_handler.py # Gemini API interaction logic
│   └── config.py       # Configuration and API key loading
├── requirements.txt    # Python dependencies
├── README.md           # Project overview
├── .env.example        # Example environment variables file
└── test_models.ipynb   # Notebook for testing model speed/availability
```

---

## 7. Contributing

This project was developed solely by Harishi for the GDG Build with AI Hackathon 2025 at Constructor University Bremen. As such, contributions are not being sought at this time.

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

---