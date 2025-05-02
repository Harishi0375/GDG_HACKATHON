# GDG Hackathon - Build with AI (Constructor University Bremen)

![GDG Hackathon Banner](https://res.cloudinary.com/startup-grind/image/upload/c_fill,dpr_2.0,f_auto,g_center,h_1080,q_100,w_1080/v1/gcs/platform-data-goog/event_banners/gdev-ecc-site-banners-events_1Gv50j1.png) **Event:** GDG on Campus Constructor University Bremen - Build with AI Hackathon (May 2-5, 2025)
**Team Member:** Harishi

---

## Project Overview

This project is an entry for the GDG Build with AI Hackathon. The goal is to create a system leveraging Vision-Language Models (VLLMs) to analyze input content (images and text files), extract relevant information, and provide clear provenance (indicating which file the information came from). The target is to achieve high accuracy in information extraction using Google AI technologies.

## Task

Develop a VLLM-powered application that can:
1.  Accept image files (`.jpg`, `.png`, etc.) and text files (`.txt`) as input.
2.  Utilize a Google VLLM (specifically, the **Google Gemini API**) to understand the content of these files.
3.  Extract key information from the content.
4.  Output the extracted information in a structured format (e.g., JSON).
5.  Clearly indicate the source file for each piece of extracted information (provenance).
6.  Strive for the highest possible accuracy in the extraction process.

## Technology Stack

* **Programming Language:** Python 3.10+
* **Core AI Model:** Google Gemini API (via `google-generativeai` SDK)
* **Image Handling:** Pillow
* **Environment Management:** Conda / venv
* **Secrets Management:** python-dotenv

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
2.  **Create and activate a Python virtual environment:**
    ```bash
    # Using venv
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate    # On Windows

    # Or using Conda (if you prefer)
    # conda create -n gdg_hack_env python=3.10
    # conda activate gdg_hack_env
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up API Key:**
    * Get your Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).
    * Copy the `.env.example` file to a new file named `.env`:
        ```bash
        cp .env.example .env
        ```
    * Open the `.env` file and paste your API key:
        ```
        GOOGLE_API_KEY=YOUR_API_KEY_HERE
        ```
    * **Important:** The `.env` file is included in `.gitignore` and should *never* be committed to Git.

## How to Run

1.  Place the image and text files you want to analyze into the `inputs/` directory.
2.  Run the main script from the root directory:
    ```bash
    python src/main.py
    ```
3.  Check the `outputs/` directory for the `results.json` file containing the extracted information and provenance.

---

