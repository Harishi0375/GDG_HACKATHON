# src/vllm_handler.py
import logging
import os
from PIL import Image # For handling images
import mimetypes # To determine file type
import io

# Import Google Cloud Vertex AI libraries
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    FinishReason,
    Image as VertexImage # Renamed to avoid conflict with PIL.Image
)
import vertexai.preview.generative_models as generative_models

# Import project modules
try:
    # Use relative import within the package
    from . import config
    from . import utils # Import utils to use the PDF renderer
except ImportError:
    # Fallback for direct execution (like testing)
    import config
    import utils

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
        # Ensure region is set correctly (e.g., us-central1 worked for flash model)
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
    Analyzes the content of an image, text, or PDF file using the specified Vertex AI Gemini model.
    For PDFs, it renders each page as an image.
    NOTE: Using gemini-2.0-flash-001 as the accessible model based on testing and mentor feedback.

    Args:
        file_path: The absolute path to the input file (image, text, or PDF).

    Returns:
        A string containing the combined analysis results from the Gemini model,
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
            # Guess based on extension if MIME type fails
            _, ext = os.path.splitext(file_path.lower())
            if ext == ".pdf":
                mime_type = "application/pdf"
            elif ext in utils.SUPPORTED_TEXT_EXTENSIONS:
                 mime_type = "text/plain"
            elif ext in utils.SUPPORTED_IMAGE_EXTENSIONS:
                 mime_type = f"image/{ext[1:]}" # Basic image MIME type guess
            else:
                logging.warning(f"Could not determine MIME type for {file_path}. Attempting as text.")
                mime_type = "text/plain"

        logging.info(f"Processing as MIME type: {mime_type}")

        # --- Prepare content parts based on type ---
        request_contents_list = [] # List to hold parts for the API request

        if mime_type.startswith("image/"):
            try:
                # Load image using Pillow first to ensure it's valid
                img = Image.open(file_path)
                # Convert to Vertex AI Image Part
                image_part = Part.from_image(VertexImage.load_from_file(file_path))
                request_contents_list.append(image_part)
                logging.info(f"Prepared image part for {os.path.basename(file_path)}")
            except Exception as img_err:
                 logging.error(f"Failed to load image file {file_path}: {img_err}", exc_info=True)
                 return f"Error: Could not load image file {os.path.basename(file_path)}."

        elif mime_type.startswith("text/"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                # Handle potentially empty text files
                if not text_content.strip():
                    logging.warning(f"Text file is empty or contains only whitespace: {file_path}")
                    # Return a specific message or analyze the empty string? Let's return a message.
                    return "Info: Input text file is empty."
                request_contents_list.append(Part.from_text(text_content))
                logging.info(f"Prepared text part for {os.path.basename(file_path)}")
            except Exception as txt_err:
                 logging.error(f"Failed to read text file {file_path}: {txt_err}", exc_info=True)
                 return f"Error: Could not read text file {os.path.basename(file_path)}."

        elif mime_type == "application/pdf":
            if not utils.fitz: # Check if PyMuPDF is available
                 return "Error: PDF processing requires PyMuPDF. Please install it (`pip install PyMuPDF`)."
            try:
                # Render each page as an image and add to request parts
                MAX_PDF_PAGES_TO_SEND = 5 # Limit pages to avoid exceeding API limits/cost
                doc = utils.fitz.open(file_path)
                num_pages = len(doc)
                logging.info(f"Processing PDF with {num_pages} pages. Sending first {min(num_pages, MAX_PDF_PAGES_TO_SEND)} pages.")

                for page_num in range(min(num_pages, MAX_PDF_PAGES_TO_SEND)):
                    img_bytes = utils.render_pdf_page_to_image_bytes(file_path, page_num)
                    if img_bytes:
                        # Create Vertex AI Image Part directly from bytes
                        pdf_image_part = Part.from_data(data=img_bytes, mime_type="image/png")
                        request_contents_list.append(pdf_image_part)
                        logging.info(f"Prepared image part for PDF page {page_num} of {os.path.basename(file_path)}")
                    else:
                        logging.warning(f"Could not render page {page_num} of PDF {file_path}.")
                doc.close()
                if not request_contents_list: # If no pages could be rendered
                    return f"Error: Could not render any pages from PDF {os.path.basename(file_path)}."

            except Exception as pdf_err:
                 logging.error(f"Failed to process PDF file {file_path}: {pdf_err}", exc_info=True)
                 # Ensure doc is closed if opened
                 if 'doc' in locals() and doc:
                     try:
                         doc.close()
                     except Exception as close_err:
                         logging.error(f"Error closing PDF after processing error: {close_err}")
                 return f"Error: Could not process PDF file {os.path.basename(file_path)}."

        else:
            logging.error(f"Unsupported file type: {mime_type} for file {os.path.basename(file_path)}")
            return f"Error: Unsupported file type '{mime_type}'."

        # Check if any content parts were actually prepared
        if not request_contents_list:
             logging.error(f"No content parts could be prepared for file: {file_path}")
             # This case might be hit if, e.g., a text file was empty and skipped
             return f"Info: No processable content found in file {os.path.basename(file_path)}."

        # --- Prepare and send request to Gemini ---
        # *** Using the accessible Flash model based on testing and mentor feedback ***
        model_name_to_use = "gemini-2.0-flash-001"
        model = GenerativeModel(model_name_to_use)
        logging.info(f"Using model: {model._model_name}")

        # *** Define the prompt including the Categorization step ***
        prompt = """
        Analyze the provided document content (which could be an image, text, or image(s) rendered from a PDF).
        Your goal is to act as an expert document analyst requiring high precision.

        Follow these steps precisely:
        1.  **Document Type:** Identify the type of document (e.g., handwritten notes, typed essay, scientific paper, form, receipt, general text, PDF page image). Note if handwriting is present.
        2.  **Summary:** Provide a concise summary (1-2 sentences) of the document's main topic or purpose.
        3.  **Key Information Extraction:** Identify and extract crucial pieces of information with high accuracy. Focus on:
            * **Main points or arguments.**
            * **Specific data points, numbers, dates, names, or definitions.**
            * **If student work: extract the core answers or thesis.**
            * **If a form: extract field names and their corresponding values.**
        4.  **Localization:** For *each* key piece of information extracted, describe *precisely* where it is located.
            * Text files: Approximate line number or paragraph.
            * Images/PDF pages: Visual location (e.g., "top-left corner", "table row 3, column 2", "handwritten below title"). Mention page number for PDFs if multiple pages were sent.
        5.  **Confidence Score:** For each extracted piece, provide a confidence level (High, Medium, Low).
        6.  **Category:** Based on the content, assign ONE category from the following list: [Lecture Notes, Essay Draft, Research Paper, Assignment Submission, Admin Form, Other].

        Present the results in a structured, easy-to-read format with clear headings for each section (Document Type, Summary, Key Information & Localization, Category).
        """

        # Combine the prompt and the content parts
        # Add the text prompt AFTER the image/text/pdf parts
        request_contents = request_contents_list + [Part.from_text(prompt)]

        # Configure safety settings
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        # Configure generation parameters
        generation_config = {
            "max_output_tokens": 2048, # Flash models might have lower limits than Pro
            "temperature": 0.3,      # Keep temperature low for extraction
            "top_p": 0.95,
            "top_k": 40,
        }

        # Send the request to the model
        logging.info(f"Sending request to Vertex AI Gemini model ({model_name_to_use}) for file: {os.path.basename(file_path)}...")
        responses = model.generate_content(
            request_contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False, # Process the whole response at once
        )

        logging.info(f"Received response from model for file: {os.path.basename(file_path)}.")

        # Process the response, checking for blocks
        try:
            # Check finish reason first for potential blocking
            if responses.candidates and responses.candidates[0].finish_reason != FinishReason.STOP:
                finish_reason_name = FinishReason(responses.candidates[0].finish_reason).name
                logging.error(f"Analysis stopped for {os.path.basename(file_path)} due to finish reason: {finish_reason_name}")
                analysis_result = f"Error: Analysis stopped due to {finish_reason_name}. Check safety settings or input content."
            elif hasattr(responses, 'text'):
                 analysis_result = responses.text
            else:
                 # If finish reason is STOP but no text, it's likely an empty response
                 logging.error(f"Model response for {os.path.basename(file_path)} was empty or unexpected (FinishReason=STOP, no text). Response: {responses}")
                 analysis_result = "Error: Model response was empty or unexpected."

        except ValueError as e:
            # This might catch issues if .text is not available even if finish_reason was STOP
            logging.warning(f"Could not directly access text from response for {os.path.basename(file_path)}. Error: {e}. Response: {responses}")
            analysis_result = "Error: Could not parse text from model response."
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
        # This might catch the PyMuPDF import error if it wasn't installed
        logging.error("Error: Required libraries (google-cloud-aiplatform, Pillow, PyMuPDF) not found. Please install requirements.")
        return "Error: Required libraries not installed."
    except Exception as e:
        # Catch other potential API errors or general exceptions
        logging.error(f"An error occurred during analysis for {os.path.basename(file_path)}: {e}", exc_info=True)
        return f"Error: An unexpected error occurred during analysis for {os.path.basename(file_path)}: {e}"

# --- Example Usage (for testing this script directly) ---
if __name__ == '__main__':
    # python -m src.vllm_handler

    if not config.GCP_PROJECT_ID or not config.GCP_REGION:
         print("Error: GCP_PROJECT_ID or GCP_REGION not set in .env file or environment.")
    else:
        # Prioritize testing PDF, then image, then text
        test_file_pdf = os.path.join(config.INPUT_DIR, "example_document.pdf") # CHANGE FILENAME if needed
        test_file_img = os.path.join(config.INPUT_DIR, "example_image.jpg") # CHANGE FILENAME if needed
        test_file_txt = os.path.join(config.INPUT_DIR, "example_text.txt") # CHANGE FILENAME if needed
        test_file_to_use = None

        if os.path.exists(test_file_pdf):
            test_file_to_use = test_file_pdf
        elif os.path.exists(test_file_img):
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
            print(f"Test file not found: No example PDF, image, or text file found in '{config.INPUT_DIR}'.")
            print(f"Please add a test file (e.g., example_document.pdf) to the '{config.INPUT_DIR}' directory.")

