# run_finetuning.py
import os
from google.cloud import aiplatform # Import the main aiplatform module
import logging
import datetime
import json # Needed for parameter serialization if complex types are used

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- User Configuration - VERIFY THESE VALUES ---
PROJECT_ID = "maximal-cider-458611-r5"
LOCATION = "europe-west4" # Make sure this is a region supporting the tuning pipeline
BASE_MODEL_NAME = "gemini-2.0-flash-lite-001" # Verify this is the correct API identifier
DATASET_GCS_URI = "gs://harishi-gdg-tuning-data/data/tuning_data.jsonl"
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
TUNED_MODEL_DISPLAY_NAME = f"gdg-documind-flash-lite-tuned-{timestamp}"

# --- Fine-Tuning Job Parameters ---
# These need to match the expected parameters of the pipeline template
TRAINING_STEPS = 100
LORA_RANK = 4

# --- Pipeline Template URI ---
# This URI points to the predefined Google Cloud Pipeline for supervised tuning.
# NOTE: This specific URI might change or need verification. Check Vertex AI Pipelines > Templates in Cloud Console.
# Common templates exist for different tasks. This is a plausible structure:
PIPELINE_TEMPLATE_URI = "https://us-kfp.pkg.dev/ml-pipeline/large-language-model-pipelines/tune-large-model/v2.0.0"
# Alternative structure seen in some docs (might be older or for different models):
# PIPELINE_TEMPLATE_URI = "gs://google-cloud-aiplatform/schema/pipeline/jobspec/google_cloud_pipeline_components_google.cloud.aiplatform.v1.pipeline_job_tune_hyperparameters_job_spec_yaml" # This seems less likely for SFT
# ** Best Practice: Find the correct template URI in the Cloud Console under Vertex AI -> Pipelines -> Templates **

# --- Script Execution ---

def launch_tuning_pipeline_job():
    """Initializes Vertex AI and launches the supervised fine-tuning job via PipelineJob."""

    # --- Initialize Vertex AI SDK ---
    try:
        logging.info(f"Initializing Vertex AI SDK for project {PROJECT_ID} in {LOCATION}...")
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        logging.info("Vertex AI SDK Initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize Vertex AI SDK: {e}", exc_info=True)
        return

    # --- Define Pipeline Parameters ---
    # These names MUST match the specific pipeline template's expected inputs
    pipeline_parameters = {
        "project": PROJECT_ID,
        "location": LOCATION, # Often needed within the pipeline itself
        "base_model_name": BASE_MODEL_NAME, # Parameter name could be 'base_model' or 'source_model' etc.
        "dataset_uri": DATASET_GCS_URI, # Parameter name could be 'dataset_uri', 'train_dataset', etc.
        "tuned_model_display_name": TUNED_MODEL_DISPLAY_NAME,
        "train_steps": TRAINING_STEPS, # Parameter name could be 'steps', 'train_steps', 'max_steps' etc.
        # PEFT/LoRA parameters are often passed within a JSON string or specific structure
        # Example for LoRA (parameter names like 'peft_config', 'lora_config', 'adapter_spec' vary by template):
        "adapter_spec": json.dumps({ # Serialize complex parameters to JSON string if needed
            "adapter_type": "LORA",
            "lora_config": {"rank": LORA_RANK}
        }),
        # Alternatively, some pipelines might take rank directly:
        # "lora_rank": LORA_RANK, # Check the template definition
        # Add other parameters if needed: e.g., 'learning_rate_multiplier', 'validation_dataset_uri'
    }
    logging.info(f"Pipeline Parameters: {pipeline_parameters}")

    # --- Create and Run the Pipeline Job ---
    try:
        # Generate a unique job ID
        job_id = f"tune-{BASE_MODEL_NAME.replace('.', '-')}-{timestamp}"
        logging.info(f"Creating PipelineJob with job_id: {job_id}")

        pipeline_job = aiplatform.PipelineJob(
            display_name=TUNED_MODEL_DISPLAY_NAME, # Name shown in the UI
            template_path=PIPELINE_TEMPLATE_URI,
            job_id=job_id, # Optional, but helps tracking
            parameter_values=pipeline_parameters,
            enable_caching=False, # Usually disable caching for tuning jobs
            # pipeline_root= # Optional: Specify a GCS path for pipeline outputs, otherwise defaults
        )

        logging.info("Submitting PipelineJob...")
        # Use submit() for asynchronous execution
        pipeline_job.submit()
        # Or use run() to block until completion (not recommended for long jobs)
        # pipeline_job.run()

        logging.info(f"Pipeline job submitted. Resource Name: {pipeline_job.resource_name}")
        logging.info(f"View Pipeline Job: {pipeline_job.dashboard_uri}")
        logging.info("Monitor the job progress in the Google Cloud Console -> Vertex AI -> Pipelines -> Runs & Jobs.")
        logging.info(f"Once completed, the tuned model should be available with display name: {TUNED_MODEL_DISPLAY_NAME}")

    except Exception as e:
        logging.error(f"Failed to create or submit PipelineJob: {e}", exc_info=True)

# --- Main execution block ---
if __name__ == "__main__":
    print("--- Preparing to Launch Fine-Tuning Pipeline Job ---")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Base Model: {BASE_MODEL_NAME}")
    print(f"Dataset URI: {DATASET_GCS_URI}")
    print(f"Pipeline Template URI: {PIPELINE_TEMPLATE_URI}")
    print(f"Tuned Model Display Name: {TUNED_MODEL_DISPLAY_NAME}")
    print(f"Training Steps: {TRAINING_STEPS}")
    print(f"LoRA Rank: {LORA_RANK}")
    print("-" * 30)
    launch_tuning_pipeline_job()