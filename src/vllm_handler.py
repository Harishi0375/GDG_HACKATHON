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
        # Ensure region is set correctly
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
    Uses the fine-tuned model endpoint if available and configured.

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
        return f"Error: File not found at path '{file_path}'."

    try:
        # Determine file type (MIME type)
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            _, ext = os.path.splitext(file_path.lower())
            if ext == ".pdf":
                mime_type = "application/pdf"
            elif ext in utils.SUPPORTED_TEXT_EXTENSIONS:
                 mime_type = "text/plain"
            elif ext in utils.SUPPORTED_IMAGE_EXTENSIONS:
                 mime_type = f"image/{ext[1:]}" if ext[1:] else "image/unknown"
            else:
                logging.warning(f"Could not determine MIME type for {file_path}. Skipping.")
                return f"Error: Unsupported file type or unknown extension for {os.path.basename(file_path)}."

        logging.info(f"Processing as MIME type: {mime_type}")

        # --- Prepare content parts based on type ---
        request_contents_list = []

        if mime_type.startswith("image/"):
            try:
                with Image.open(file_path) as img:
                    img.verify()
                image_part = Part.from_image(VertexImage.load_from_file(file_path))
                request_contents_list.append(image_part)
                logging.info(f"Prepared image part for {os.path.basename(file_path)}")
            except FileNotFoundError:
                logging.error(f"File not found error during image loading: {file_path}")
                return f"Error: File not found when trying to load image {os.path.basename(file_path)}."
            except Exception as img_err:
                 logging.error(f"Failed to load or invalid image file {file_path}: {img_err}", exc_info=True)
                 return f"Error: Could not load or invalid image file {os.path.basename(file_path)}."

        elif mime_type.startswith("text/"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                if not text_content.strip():
                    logging.warning(f"Text file is empty or contains only whitespace: {file_path}")
                    return "Info: Input text file is empty."
                request_contents_list.append(Part.from_text(text_content))
                logging.info(f"Prepared text part for {os.path.basename(file_path)}")
            except Exception as txt_err:
                 logging.error(f"Failed to read text file {file_path}: {txt_err}", exc_info=True)
                 return f"Error: Could not read text file {os.path.basename(file_path)}."

        elif mime_type == "application/pdf":
            if not utils.fitz:
                 return "Error: PDF processing requires PyMuPDF. Please install it (`pip install PyMuPDF`)."
            try:
                MAX_PDF_PAGES_TO_SEND = 5
                doc = utils.fitz.open(file_path)
                num_pages = len(doc)
                logging.info(f"Processing PDF with {num_pages} pages. Sending first {min(num_pages, MAX_PDF_PAGES_TO_SEND)} pages.")

                for page_num in range(min(num_pages, MAX_PDF_PAGES_TO_SEND)):
                    img_bytes = utils.render_pdf_page_to_image_bytes(file_path, page_num)
                    if img_bytes:
                        pdf_image_part = Part.from_data(data=img_bytes, mime_type="image/png")
                        request_contents_list.append(pdf_image_part)
                        logging.info(f"Prepared image part for PDF page {page_num} of {os.path.basename(file_path)}")
                    else:
                        logging.warning(f"Could not render page {page_num} of PDF {file_path}.")
                doc.close()
                if not request_contents_list:
                    return f"Error: Could not render any pages from PDF {os.path.basename(file_path)}."

            except Exception as pdf_err:
                 logging.error(f"Failed to process PDF file {file_path}: {pdf_err}", exc_info=True)
                 if 'doc' in locals() and doc and not doc.is_closed:
                     try: doc.close()
                     except Exception: pass
                 return f"Error: Could not process PDF file {os.path.basename(file_path)}."

        else:
            logging.error(f"Unsupported file type slipped through: {mime_type} for file {os.path.basename(file_path)}")
            return f"Error: Unsupported file type '{mime_type}'."

        if not request_contents_list:
             logging.error(f"No content parts could be prepared for file: {file_path}")
             return f"Info: No processable content found in file {os.path.basename(file_path)}."

        # --- Prepare and send request to Gemini ---

        # *** MODIFICATION START: Use the Fine-Tuned Model ID ***
        # Comment out the base model loading
        # model_name_to_use = "gemini-2.0-flash-lite-001"
        # model = GenerativeModel(model_name_to_use)

        # Define the identifier for your successfully tuned model
        tuned_model_name = "projects/248124319532/locations/europe-west4/models/8219698240602243072"

        logging.info(f"Using TUNED model: {tuned_model_name}")
        # Load the fine-tuned model using from_pretrained
        try:
            model = GenerativeModel.from_pretrained(tuned_model_name)
            # Optional: Log the actual loaded model name if available
            # if hasattr(model, '_model_name'):
            #    logging.info(f"Successfully loaded tuned model reference: {model._model_name}")
            # else:
            #    logging.info("Successfully obtained tuned model reference.")
        except Exception as load_err:
            logging.error(f"Failed to load tuned model '{tuned_model_name}': {load_err}", exc_info=True)
            return f"Error: Could not load fine-tuned model '{tuned_model_name}'"
        # *** MODIFICATION END ***

        prompt = """
        Your task is to act as an expert document analyst. Analyze the provided document content meticulously. Even if the content is very short, analyze the content itself.

        Follow these steps precisely and structure your output exactly as shown using Markdown headings:

        **Document Type:**
        [Identify the type: e.g., Handwritten Notes, Typed Essay, Scientific Paper, Form, Receipt, General Text, PDF Page Image, Bar Chart, Line Graph, Diagram. Note if handwriting is present.]

        **Summary:**
        [Provide a concise 1-2 sentence summary of the main topic or purpose. For charts/graphs, describe what it represents.]

        **Key Information & Localization:**
        [Identify and extract crucial pieces of information (main points, arguments, data points from charts/graphs, axis labels, legends, titles, definitions, form fields/values). For EACH piece of information, describe its precise location (Text files: line/paragraph; Images/PDF pages: visual location like 'top-left', 'bar corresponding to 'Category A'', 'X-axis label', 'legend entry for Series 1'). Use bullet points for clarity.]
        * [Extracted Info 1]
            * Location: [Precise location description]
            * Confidence: [High, Medium, or Low]
        * [Extracted Info 2]
            * Location: [Precise location description]
            * Confidence: [High, Medium, or Low]
        * ... (continue for all key pieces)

        **Category:**
        [Assign ONE category based on the content from this list: Lecture Notes, Essay Draft, Research Paper, Assignment Submission, Admin Form, Data Visualization, Other. If unsure, state 'Other'.]
        """

        request_contents = request_contents_list + [Part.from_text(prompt)]

        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        generation_config = {
            "max_output_tokens": 2048,
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
        }

        logging.info(f"Sending request to Vertex AI Gemini model ({tuned_model_name}) for file: {os.path.basename(file_path)}...")
        responses = model.generate_content(
            request_contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )

        logging.info(f"Received response from model for file: {os.path.basename(file_path)}.")

        analysis_result = "Error: Failed to process model response."
        try:
            if not responses.candidates:
                 feedback_reason = responses.prompt_feedback.block_reason if hasattr(responses, 'prompt_feedback') and responses.prompt_feedback else "UNKNOWN"
                 logging.error(f"Analysis failed for {os.path.basename(file_path)}. No candidates returned. Reason: {feedback_reason}. Response: {responses}")
                 analysis_result = f"Error: Analysis failed. No candidates returned. Reason: {feedback_reason}"
            elif responses.candidates[0].finish_reason != FinishReason.STOP:
                finish_reason_name = FinishReason(responses.candidates[0].finish_reason).name
                logging.error(f"Analysis stopped for {os.path.basename(file_path)} due to finish reason: {finish_reason_name}")
                analysis_result = f"Error: Analysis stopped due to {finish_reason_name}. Check safety settings or input content."
            elif not responses.candidates[0].content.parts:
                 logging.error(f"Model response for {os.path.basename(file_path)} had no content parts (FinishReason=STOP). Response: {responses}")
                 analysis_result = "Error: Model response was empty (no parts)."
            else:
                 try:
                     analysis_result = responses.text
                 except ValueError as e:
                     logging.warning(f"Could not directly access text from response for {os.path.basename(file_path)}. Error: {e}. Full Parts: {responses.candidates[0].content.parts}")
                     analysis_result = " ".join(part.text for part in responses.candidates[0].content.parts if hasattr(part, 'text'))
                     if not analysis_result:
                         analysis_result = "Error: Could not parse text from model response parts."

        except Exception as e_resp:
             logging.error(f"Unexpected error processing model response for {os.path.basename(file_path)}: {e_resp}", exc_info=True)
             analysis_result = f"Error: Unexpected error processing response: {e_resp}"

        logging.info(f"Analysis complete for file: {os.path.basename(file_path)}.")
        return analysis_result

    except FileNotFoundError:
        logging.error(f"File not found during processing: {file_path}")
        return "Error: File not found during processing."
    except ImportError:
        logging.error("Error: Required libraries (google-cloud-aiplatform, Pillow, PyMuPDF) not found. Please install requirements.")
        return "Error: Required libraries not installed."
    except Exception as e:
        logging.error(f"An error occurred during analysis for {os.path.basename(file_path)}: {e}", exc_info=True)
        return f"Error: An unexpected error occurred during analysis for {os.path.basename(file_path)}: {e}"

# --- Example Usage (for testing this script directly) ---
if __name__ == '__main__':
    # Run this specific script from the project root directory using:
    # python -m src.vllm_handler

    if not config.GCP_PROJECT_ID or not config.GCP_REGION:
         print("Error: GCP_PROJECT_ID or GCP_REGION not set in .env file or environment.")
    else:
        # Define the specific file to test
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # --- !! CHANGE THIS PATH TO TEST DIFFERENT FILES !! ---
        # Example: Test the PDF used in tuning
        test_file_to_use = os.path.join(project_root, "inputs", "pdf", "ML - assignment 4.pdf")
        # Example: Test the JPG used in tuning
        # test_file_to_use = os.path.join(project_root, "inputs", "jpg", "test.jpg")
        # Example: Test the PNG chart used in tuning
        # test_file_to_use = os.path.join(project_root, "inputs", "png", "output.png")
        # ----------------------------------------------------
        test_file_to_use = os.path.abspath(test_file_to_use)

        print(f"Attempting to test analysis using the TUNED model for: {test_file_to_use}")

        if os.path.exists(test_file_to_use):
            print(f"--- Testing analysis for: {os.path.basename(test_file_to_use)} ---")
            result = analyze_content(test_file_to_use) # This now uses the tuned model ID
            print("\n--- Analysis Result ---")
            print(result)
            print("-----------------------")
        else:
            print(f"Test file not found: '{test_file_to_use}'")
            print(f"Please ensure the file exists at that location relative to the project structure.")