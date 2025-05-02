# src/vllm_handler.py
import logging
import os
from PIL import Image # For handling images
import mimetypes # To determine file type

# Import Google Cloud Vertex AI libraries
import vertexai
# Import specific classes needed
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    FinishReason,
    Image as VertexImage # Renamed to avoid conflict with PIL.Image
)
import vertexai.preview.generative_models as generative_models # Keep for safety settings enums

# Import configuration variables (Project ID, Region)
try:
    from . import config # Use relative import within the package
except ImportError:
    import config # Fallback for direct execution (like testing)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize Vertex AI ---
_vertex_ai_initialized = False

def initialize_vertex_ai():
    """Initializes Vertex AI if not already done."""
    global _vertex_ai_initialized
    if _vertex_ai_initialized:
        return True # Indicate success if already initialized

    if not config.GCP_PROJECT_ID or not config.GCP_REGION:
         logging.error("GCP_PROJECT_ID or GCP_REGION not configured. Cannot initialize Vertex AI.")
         return False # Indicate failure

    try:
        logging.info(f"Initializing Vertex AI for project '{config.GCP_PROJECT_ID}' in region '{config.GCP_REGION}'")
        vertexai.init(project=config.GCP_PROJECT_ID, location=config.GCP_REGION)
        _vertex_ai_initialized = True
        logging.info("Vertex AI initialized successfully.")
        return True # Indicate success
    except Exception as e:
        logging.error(f"FATAL ERROR: Failed to initialize Vertex AI: {e}", exc_info=True)
        return False # Indicate failure

# --- Define the function to analyze content ---

def analyze_content(file_path: str) -> str:
    """
    Analyzes the content of an image or text file using Vertex AI Gemini Pro Vision.

    Args:
        file_path: The absolute path to the input file (image or text).

    Returns:
        A string containing the analysis results from the Gemini model,
        or an error message if analysis fails.
    """
    # Ensure Vertex AI is initialized before proceeding
    if not initialize_vertex_ai():
         return "Error: Vertex AI could not be initialized. Check configuration and logs."

    logging.info(f"Analyzing file: {file_path}")

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return "Error: File not found."

    try:
        # Determine file type (MIME type)
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            logging.warning(f"Could not determine MIME type for {file_path}. Assuming text.")
            mime_type = "text/plain" # Default assumption

        logging.info(f"Detected MIME type: {mime_type}")

        # Prepare the content part for the API request
        if mime_type.startswith("image/"):
            try:
                # Load image using Pillow first to ensure it's valid
                img = Image.open(file_path)
                # Convert to Vertex AI Image Part
                image_part = Part.from_image(VertexImage.load_from_file(file_path))
                content_parts = [image_part]
            except Exception as img_err:
                 logging.error(f"Failed to load image file {file_path}: {img_err}", exc_info=True)
                 return f"Error: Could not load image file {os.path.basename(file_path)}."

        elif mime_type.startswith("text/"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                content_parts = [Part.from_text(text_content)]
            except Exception as txt_err:
                 logging.error(f"Failed to read text file {file_path}: {txt_err}", exc_info=True)
                 return f"Error: Could not read text file {os.path.basename(file_path)}."
        else:
            logging.error(f"Unsupported file type: {mime_type} for file {os.path.basename(file_path)}")
            return f"Error: Unsupported file type '{mime_type}'."

        # *** FIX 1: Change the model name ***
        # Use the standard stable vision model instead of the preview one
        model = GenerativeModel("gemini-1.0-pro-vision-001")
        logging.info(f"Using model: {model._model_name}") # Log the model being used

        # Define the prompt for information extraction and localization
        # (Keep the detailed prompt from the previous version)
        prompt = """
        Analyze the provided document (which could be an image of a document or a text file).
        Your goal is to act as an expert document analyst.

        Follow these steps precisely:
        1.  **Document Type:** Identify the type of document if possible (e.g., handwritten notes, typed essay, scientific paper, form, receipt, general text). If it's an image, mention if it appears scanned or a photo. Note if handwriting is present.
        2.  **Summary:** Provide a concise summary (1-2 sentences) of the document's main topic or purpose.
        3.  **Key Information Extraction:** Identify and extract crucial pieces of information. Focus on:
            * **Main points or arguments.**
            * **Specific data points, numbers, dates, names, or definitions.**
            * **If it looks like student work (e.g., exam answers, essay), extract the core answers or thesis.**
            * **If it's a form, extract field names and their corresponding values.**
        4.  **Localization:** For *each* key piece of information extracted in step 3, describe *precisely* where it is located in the document.
            * For text files: Mention the approximate line number or paragraph.
            * For images: Describe the location visually (e.g., "top-left corner", "middle section, below the title", "handwritten in the bottom margin", "inside the table, row 3, column 2"). Be as specific as possible.
        5.  **Confidence Score (Optional but helpful):** For each extracted piece of information, provide a confidence level (e.g., High, Medium, Low) based on clarity and certainty.

        Present the results in a structured and easy-to-read format. Use clear headings for each section (Document Type, Summary, Key Information & Localization).
        """

        # Combine the prompt and the content (image or text)
        request_contents = content_parts + [Part.from_text(prompt)]

        # Configure safety settings
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        # Configure generation parameters
        generation_config = {
            "max_output_tokens": 2048, # Adjusted for gemini-1.0-pro-vision limits if needed
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
        }

        # Send the request to the model
        logging.info(f"Sending request to Vertex AI Gemini model for file: {os.path.basename(file_path)}...")
        responses = model.generate_content(
            request_contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )

        logging.info(f"Received response from model for file: {os.path.basename(file_path)}.")

        # *** FIX 2: Check response for blocking using finish_reason ***
        try:
            # Access the text content safely
            analysis_result = responses.text
        except ValueError as e:
            # Handle cases where the response might be blocked or lack text content
            logging.warning(f"Could not directly access text from response for {os.path.basename(file_path)}. Checking finish reason. Error: {e}")
            # Check finish reason in the first candidate if available
            if responses.candidates and responses.candidates[0].finish_reason != FinishReason.STOP:
                finish_reason_name = FinishReason(responses.candidates[0].finish_reason).name
                logging.error(f"Analysis stopped for {os.path.basename(file_path)} due to finish reason: {finish_reason_name}")
                analysis_result = f"Error: Analysis stopped due to {finish_reason_name}. Check safety settings or input content."
            else:
                # If no clear blocking reason, report as empty/unexpected
                logging.error(f"Model response for {os.path.basename(file_path)} was empty or in an unexpected format. Response: {responses}")
                analysis_result = "Error: Model response was empty or unexpected."
        except Exception as e_resp:
             # Catch other potential errors accessing response parts
             logging.error(f"Unexpected error processing model response for {os.path.basename(file_path)}: {e_resp}", exc_info=True)
             analysis_result = f"Error: Unexpected error processing response: {e_resp}"


        logging.info(f"Analysis complete for file: {os.path.basename(file_path)}.")
        return analysis_result

    except FileNotFoundError:
        logging.error(f"File not found during processing: {file_path}")
        return "Error: File not found during processing."
    except ImportError:
        logging.error("Error: Required libraries (google-cloud-aiplatform, Pillow) not found. Please install requirements.")
        return "Error: Required libraries not installed."
    # Removed the specific BlockedPromptException catch block as it caused an error
    except Exception as e:
        # Catch other potential API errors or general exceptions
        logging.error(f"An error occurred during analysis for {os.path.basename(file_path)}: {e}", exc_info=True)
        return f"Error: An unexpected error occurred during analysis for {os.path.basename(file_path)}: {e}"

# --- Example Usage (for testing this script directly) ---
if __name__ == '__main__':
    # This block runs only when the script is executed directly from the root folder using:
    # python -m src.vllm_handler

    # Ensure config is loaded when run directly
    if not config.GCP_PROJECT_ID or not config.GCP_REGION:
         print("Error: GCP_PROJECT_ID or GCP_REGION not set in .env file or environment.")
    else:
        # Try analyzing an image first, then text if image fails or doesn't exist
        test_file_img = os.path.join(config.INPUT_DIR, "example_image.jpg") # CHANGE FILENAME if needed
        test_file_txt = os.path.join(config.INPUT_DIR, "example_text.txt") # CHANGE FILENAME if needed
        test_file_to_use = None

        if os.path.exists(test_file_img):
            test_file_to_use = test_file_img
        elif os.path.exists(test_file_txt):
             test_file_to_use = test_file_txt

        if test_file_to_use:
            print(f"--- Testing analysis for: {test_file_to_use} ---")
            result = analyze_content(test_file_to_use)
            print("\n--- Analysis Result ---")
            print(result)
            print("-----------------------")
        else:
            print(f"Test file not found: Neither '{os.path.basename(test_file_img)}' nor '{os.path.basename(test_file_txt)}' found in '{config.INPUT_DIR}'.")
            print(f"Please add a test file (e.g., example_image.jpg or example_text.txt) to the '{config.INPUT_DIR}' directory.")
