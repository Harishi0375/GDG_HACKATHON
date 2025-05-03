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
# --- MODIFIED FUNCTION SIGNATURE ---
def analyze_content(file_path: str, model_id_override: str = None) -> str:
    """
    Analyzes content using a specified Vertex AI Gemini model.
    Uses the fine-tuned model by default unless overridden.

    Args:
        file_path: The absolute path to the input file (image, text, or PDF).
        model_id_override (str, optional): Specific model ID to use (e.g., base model ID).
                                            If None, uses the default fine-tuned model.

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
                # Use context manager for file opening
                with Image.open(file_path) as img:
                     # It's good practice to load the image data to ensure it's valid before verify
                     img.load()
                     img.verify() # Verify image integrity
                # Create Part after verification
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
            doc = None # Initialize doc
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
                doc.close() # Close inside try block after loop
                if not request_contents_list:
                    return f"Error: Could not render any pages from PDF {os.path.basename(file_path)}."

            except Exception as pdf_err:
                 logging.error(f"Failed to process PDF file {file_path}: {pdf_err}", exc_info=True)
                 if doc and not doc.is_closed: # Check if doc was opened and not closed
                     try: doc.close()
                     except Exception: pass
                 return f"Error: Could not process PDF file {os.path.basename(file_path)}."
            # Ensure doc is closed if loop finishes but error occurs later (though unlikely here)
            finally:
                if doc and not doc.is_closed:
                     try: doc.close()
                     except Exception: pass


        else: # Should not be reached if MIME type logic is correct
            logging.error(f"Unsupported file type slipped through: {mime_type} for file {os.path.basename(file_path)}")
            return f"Error: Unsupported file type '{mime_type}'."

        if not request_contents_list:
             logging.error(f"No content parts could be prepared for file: {file_path}")
             return f"Info: No processable content found in file {os.path.basename(file_path)}."

        # --- MODIFIED MODEL SELECTION LOGIC ---
        model = None
        model_name_to_use = None
        tuned_model_name = "projects/248124319532/locations/europe-west4/models/8219698240602243072" # Your tuned ID
        base_model_name = "gemini-2.0-flash-lite-001" # Define base model ID here too

        if model_id_override:
            model_name_to_use = model_id_override
            logging.info(f"Using OVERRIDDEN model: {model_name_to_use}")
            # Check if it looks like a tuned model ID (contains 'projects/')
            if "projects/" in model_name_to_use:
                 try:
                     # Use the specific class for clarity
                     model = vertexai.generative_models.GenerativeModel.from_pretrained(model_name_to_use)
                     logging.info(f"Successfully loaded OVERRIDDEN (tuned) model: {model_name_to_use}")
                 except Exception as load_err:
                     logging.error(f"Failed to load overridden tuned model '{model_name_to_use}': {load_err}", exc_info=True)
                     # Check specifically for the AttributeError again
                     if isinstance(load_err, AttributeError) and 'from_pretrained' in str(load_err):
                         logging.critical("AttributeError 'from_pretrained' encountered loading OVERRIDDEN model. Check SDK version/environment.")
                     return f"Error: Could not load fine-tuned model '{model_name_to_use}'"
            else: # Assume it's a base model ID
                try:
                    # Use the specific class for clarity
                    model = vertexai.generative_models.GenerativeModel(model_name_to_use)
                    logging.info(f"Successfully loaded OVERRIDDEN (base) model: {model_name_to_use}")
                except Exception as load_err:
                    logging.error(f"Failed to load overridden base model '{model_name_to_use}': {load_err}", exc_info=True)
                    return f"Error: Could not load base model '{model_name_to_use}'"

        else: # Default to the fine-tuned model if no override
            model_name_to_use = tuned_model_name
            logging.info(f"Using DEFAULT (tuned) model: {model_name_to_use}")
            try:
                # Use the specific class for clarity
                model = vertexai.generative_models.GenerativeModel.from_pretrained(model_name_to_use)
                logging.info(f"Successfully loaded DEFAULT (tuned) model: {model_name_to_use}")
            except Exception as load_err:
                logging.error(f"Failed to load default tuned model '{model_name_to_use}': {load_err}", exc_info=True)
                # Check specifically for the AttributeError again
                if isinstance(load_err, AttributeError) and 'from_pretrained' in str(load_err):
                     logging.critical("AttributeError 'from_pretrained' encountered loading DEFAULT model. Check SDK version/environment.")
                return f"Error: Could not load fine-tuned model '{model_name_to_use}'"
        # --- END MODIFIED MODEL SELECTION ---

        if not model:
             # This should only happen if an error occurred above and returned early
             logging.error("Model object could not be instantiated.")
             return "Error: Model object could not be instantiated (check previous errors)."

        # --- Define the prompt ---
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

        # --- Define safety and generation config ---
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

        # Use the determined model_name_to_use for logging
        logging.info(f"Sending request to Vertex AI Gemini model ({model_name_to_use}) for file: {os.path.basename(file_path)}...")
        # Use the instantiated 'model' object for the call
        responses = model.generate_content(
            request_contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )

        logging.info(f"Received response from model for file: {os.path.basename(file_path)}.")

        # --- Process the response ---
        analysis_result = "Error: Failed to process model response." # Default error
        try:
            # Check for blocked responses or empty candidates first
            if not responses.candidates:
                 feedback_reason = responses.prompt_feedback.block_reason if hasattr(responses, 'prompt_feedback') and responses.prompt_feedback else "UNKNOWN"
                 logging.error(f"Analysis failed for {os.path.basename(file_path)}. No candidates returned. Reason: {feedback_reason}. Response: {responses}")
                 analysis_result = f"Error: Analysis failed. No candidates returned. Reason: {feedback_reason}"
            # Check finish reason
            elif responses.candidates[0].finish_reason != FinishReason.STOP:
                finish_reason_name = FinishReason(responses.candidates[0].finish_reason).name
                logging.error(f"Analysis stopped for {os.path.basename(file_path)} due to finish reason: {finish_reason_name}")
                analysis_result = f"Error: Analysis stopped due to {finish_reason_name}. Check safety settings or input content."
            # Check for empty content parts
            elif not responses.candidates[0].content.parts:
                 logging.error(f"Model response for {os.path.basename(file_path)} had no content parts (FinishReason=STOP). Response: {responses}")
                 analysis_result = "Error: Model response was empty (no parts)."
            # Try to get text if everything looks okay
            else:
                 try:
                     analysis_result = responses.text
                 except ValueError as e: # Handle cases where .text might fail
                     logging.warning(f"Could not directly access text from response for {os.path.basename(file_path)}. Error: {e}. Full Parts: {responses.candidates[0].content.parts}")
                     # Fallback to joining text parts if available
                     analysis_result = " ".join(part.text for part in responses.candidates[0].content.parts if hasattr(part, 'text'))
                     if not analysis_result.strip(): # Check if joined text is also empty
                         analysis_result = "Error: Could not parse text from model response parts (empty after join)."
                     # If still no text, keep the error message

        except Exception as e_resp:
             logging.error(f"Unexpected error processing model response for {os.path.basename(file_path)}: {e_resp}", exc_info=True)
             analysis_result = f"Error: Unexpected error processing response: {e_resp}"

        logging.info(f"Analysis complete for file: {os.path.basename(file_path)}.")
        return analysis_result

    # --- Outer error handling ---
    except FileNotFoundError: # Catch specific errors if possible
        logging.error(f"File not found during processing: {file_path}")
        return "Error: File not found during processing."
    except ImportError:
        logging.error("Error: Required libraries (google-cloud-aiplatform, Pillow, PyMuPDF) not found. Please install requirements.")
        return "Error: Required libraries not installed."
    except Exception as e: # General catch-all
        logging.error(f"An unexpected error occurred during analysis for {os.path.basename(file_path)}: {e}", exc_info=True)
        return f"Error: An unexpected error occurred during analysis for {os.path.basename(file_path)}: {e}"

