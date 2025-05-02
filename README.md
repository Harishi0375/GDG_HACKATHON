# GDG Hackathon - Build with AI (Constructor University Bremen)

**Event:** GDG on Campus Constructor University Bremen - Build with AI Hackathon (May 2-5, 2025)
**Team Member:** Harishi

---

## Project Overview

This project is an entry for the GDG Build with AI Hackathon. The goal is to create an **EdTech** application leveraging Vision-Language Models (VLLMs) to analyze input documents (images and text files), extract relevant information, and provide clear provenance (indicating where in the document the information was found). The target is to achieve high accuracy in information extraction using Google Cloud AI technologies.

## Task

Develop a VLLM-powered application focused on an **EdTech** use case (e.g., analyzing student work, summarizing papers) that can:
1.  Accept image files (`.jpg`, `.png`, etc. - scanned/photo of documents) and text files (`.txt`) as input.
2.  Utilize a Google VLLM (specifically, **Gemini via Vertex AI**) to understand the content of these documents.
3.  Extract key information relevant to the EdTech task.
4.  **Localize** the extracted information (describe *where* in the document it was found).
5.  Output the extracted information and its location in a structured format (e.g., JSON).
6.  Strive for the highest possible accuracy in the extraction and localization process.

## Technology Stack

* **Programming Language:** Python 3.10+
* **Cloud Platform:** Google Cloud Platform (GCP)
* **Core AI Service:** Vertex AI (using Gemini Pro models)
* **Python SDKs:** `google-cloud-aiplatform`, `google-cloud-storage` (optional), `Pillow`
* **Environment Management:** Conda / venv
* **Secrets/Config Management:** python-dotenv, Google Cloud Application Default Credentials (ADC)

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
│   └── results.json
├── src/                # Source code
│   ├── __init__.py
│   ├── main.py         # Main execution script
│   ├── utils.py        # Helper functions
│   ├── vllm_handler.py # Gemini API interaction logic
│   └── config.py       # Configuration and API key loading
├── requirements.txt    # Python dependencies
├── README.md           # Project overview
└── .env.example        # Example environment variables file
```

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Harishi0375/GDG_HACKATHON.git](https://github.com/Harishi0375/GDG_HACKATHON.git)
    cd GDG_HACKATHON
    ```
2.  **Google Cloud Setup:**
    * Have a Google Cloud Project created.
    * Redeem any provided Hackathon credits to your billing account.
    * **Enable the Vertex AI API** in your GCP project.
    * Install the Google Cloud CLI (`gcloud`): [Install gcloud CLI](https://cloud.google.com/sdk/docs/install)
    * Authenticate for Application Default Credentials (ADC):
        ```bash
        gcloud auth application-default login
        ```
3.  **Create and activate a Python virtual environment:**
    ```bash
    # Using venv
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate    # On Windows

    # Or using Conda (if you prefer)
    # conda create -n gdg_hack_env python=3.10 google-cloud-sdk
    # conda activate gdg_hack_env
    # gcloud auth application-default login # Run again if using conda env
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Set up Environment Variables:**
    * Copy the `.env.example` file to a new file named `.env`:
        ```bash
        cp .env.example .env
        ```
    * Open the `.env` file and add your Google Cloud Project ID:
        ```
        GCP_PROJECT_ID=your-gcp-project-id-here
        GCP_REGION=us-central1 # Or your preferred region
        ```
    * **Important:** The `.env` file is included in `.gitignore` and should *never* be committed to Git.

## How to Run

1.  Place the document images and text files you want to analyze into the `inputs/` directory.
2.  Run the main script from the root directory:
    ```bash
    python src/main.py
    ```
3.  Check the `outputs/` directory for the `results.json` file containing the extracted information and provenance.

---