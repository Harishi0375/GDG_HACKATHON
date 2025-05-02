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

# Log the loaded configuration (optional, good for debugging)
logging.info(f"GCP Project ID: {GCP_PROJECT_ID}")
logging.info(f"GCP Region: {GCP_REGION}")
logging.info(f"Input Directory: {INPUT_DIR}")
logging.info(f"Output Directory: {OUTPUT_DIR}")

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    logging.info(f"Creating output directory: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR)

