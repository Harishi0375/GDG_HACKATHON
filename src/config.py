# src/config.py
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
# This line looks for a .env file in the current directory or parent directories
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # Assumes .env is in the root dir, one level up from src/
logging.info(f"Looking for .env file at: {os.path.abspath(dotenv_path)}")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    logging.info(".env file loaded successfully.")
else:
    logging.warning(".env file not found. Relying on system environment variables.")
    # Attempt to load from system environment if .env is missing (useful in deployed environments)
    load_dotenv()

# --- Google Cloud Configuration ---

# Get the Google Cloud Project ID from environment variables
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
# Get the Google Cloud Region from environment variables
GCP_REGION = os.getenv("GCP_REGION")

# --- Model Configuration ---
# Define the base model ID used for comparison and potentially as a fallback
BASE_MODEL_ID = "gemini-2.0-flash-lite-001"
# Define the fine-tuned model endpoint resource name
# IMPORTANT: Replace YOUR_PROJECT_NUMBER with your actual Google Cloud project number (e.g., 123456789012)
TUNED_MODEL_ID = "projects/248124319532/locations/europe-west4/endpoints/6177691842566422528"

# --- Input/Output Configuration ---
# Define relative paths for input and output directories based on this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Project root directory
INPUT_DIR = os.path.join(BASE_DIR, "inputs")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
OUTPUT_FILENAME = "results.json" # Name for the output JSON file

# --- Validation ---
# Check if essential configuration variables are set
if not GCP_PROJECT_ID:
    logging.error("FATAL ERROR: GCP_PROJECT_ID environment variable not set.")
    raise ValueError("GCP_PROJECT_ID must be set in the .env file or environment variables.")

if not GCP_REGION:
    logging.error("FATAL ERROR: GCP_REGION environment variable not set.")
    raise ValueError("GCP_REGION must be set in the .env file or environment variables.")

# Check if the placeholder in TUNED_MODEL_ID has been replaced
if "YOUR_PROJECT_NUMBER" in TUNED_MODEL_ID:
     logging.warning("WARNING: TUNED_MODEL_ID in config.py still contains 'YOUR_PROJECT_NUMBER'. Please replace it with your actual project number.")
     # Optionally, you could raise an error here if you want to force the user to change it:
     # raise ValueError("TUNED_MODEL_ID must be updated with your actual project number.")

# Log the loaded configuration (optional, good for debugging)
logging.info(f"GCP Project ID: {GCP_PROJECT_ID}")
logging.info(f"GCP Region: {GCP_REGION}")
logging.info(f"Base Model ID: {BASE_MODEL_ID}")
logging.info(f"Tuned Model ID: {TUNED_MODEL_ID}")
logging.info(f"Input Directory: {INPUT_DIR}")
logging.info(f"Output Directory: {OUTPUT_DIR}")

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    logging.info(f"Creating output directory: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR)

