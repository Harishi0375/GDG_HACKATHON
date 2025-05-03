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
    # This might fail if utils.py also relies on relative imports
    # It's better to run scripts using `python -m src.main` from the project root
    try:
        import config
        import utils
    except ImportError as e:
        logging.error(f"Fallback import failed. Ensure running from project root or utils/config available: {e}")
        config = None # Set to None to handle gracefully later
        utils = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Add specific loggers to suppress if needed
logging.getLogger("google.api_core").setLevel(logging.WARNING)
logging.getLogger("google.auth").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)


# --- Initialize Vertex AI ---
_vertex_ai_initialized = False

def initialize_vertex_ai():
    """Initializes Vertex AI if not already done."""
    global _vertex_ai_initialized
    if _vertex_ai_initialized:
        return True # Indicate success if already initialized

    # Check if config attributes exist before accessing
    # Check if config was loaded successfully
    if config is None:
         logging.error("Config module failed to load. Cannot initialize Vertex AI.")
         return False

    gcp_project_id = getattr(config, 'GCP_PROJECT_ID', None)
    gcp_region = getattr(config, 'GCP_REGION', None)

    if not gcp_project_id or not gcp_region:
         logging.error("GCP_PROJECT_ID or GCP_REGION not configured in config module.")
         return False # Indicate failure

    try:
        logging.info(f"Initializing Vertex AI for project '{gcp_project_id}' in region '{gcp_region}'")
        # Ensure region is set correctly
        vertexai.init(project=gcp_project_id, location=gcp_region)
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
    print(f"DEBUG: analyze_content called for: {file_path}") # DEBUG

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        print(f"DEBUG: File does not exist: {file_path}") # DEBUG
        return f"Error: File not found at path '{file_path}'."

    # Define supported extensions within the function or ensure utils is loaded
    # Check if utils was loaded successfully
    if utils is None:
        logging.error("Utils module failed to load. Cannot determine supported file types.")
        return "Error: Utils module not loaded."

    supported_text_extensions = getattr(utils, 'SUPPORTED_TEXT_EXTENSIONS', {".txt"})
    supported_image_extensions = getattr(utils, 'SUPPORTED_IMAGE_EXTENSIONS', {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"})
    fitz_available = hasattr(utils, 'fitz') and utils.fitz is not None

    try:
        # Determine file type (MIME type)
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            _, ext = os.path.splitext(file_path.lower())
            if ext == ".pdf":
                mime_type = "application/pdf"
            elif ext in supported_text_extensions:
                 mime_type = "text/plain"
            elif ext in supported_image_extensions:
                 mime_type = f"image/{ext[1:]}" if ext[1:] else "image/unknown"
            else:
                logging.warning(f"Could not determine MIME type for {file_path}. Skipping.")
                return f"Error: Unsupported file type or unknown extension for {os.path.basename(file_path)}."

        logging.info(f"Processing as MIME type: {mime_type}")
        print(f"DEBUG: Mime type: {mime_type}") # DEBUG
        request_contents_list = []

        # --- Simplified Image Handling Block ---
        if mime_type.startswith("image/"):
            print(f"DEBUG: Entering SIMPLIFIED image processing block for {os.path.basename(file_path)}") # DEBUG
            try:
                # Directly use VertexImage.load_from_file
                print(f"DEBUG: Attempting VertexImage.load_from_file('{file_path}')...") # DEBUG
                image_part = Part.from_image(VertexImage.load_from_file(file_path))
                print("DEBUG: VertexImage.load_from_file successful.") # DEBUG
                request_contents_list.append(image_part)
                logging.info(f"Prepared image part for {os.path.basename(file_path)}")
            except FileNotFoundError:
                logging.error(f"File not found error during VertexImage loading: {file_path}")
                print(f"DEBUG: FileNotFoundError caught loading image.") # DEBUG
                return f"Error: File not found when trying to load image {os.path.basename(file_path)}."
            except Exception as img_err:
                 # Catch specific Vertex AI / Google API errors if possible, otherwise general
                 logging.error(f"Failed to load image using Vertex AI library {file_path}: {img_err}", exc_info=True)
                 print(f"DEBUG: Exception caught loading VertexImage: {type(img_err).__name__} - {img_err}") # DEBUG
                 return f"Error: Could not load image file {os.path.basename(file_path)} using Vertex AI."
        # --- End Simplified Image Handling ---

        # --- Text Handling Block ---
        elif mime_type.startswith("text/"):
            print(f"DEBUG: Entering text processing block for {os.path.basename(file_path)}") # DEBUG
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                if not text_content.strip():
                    logging.warning(f"Text file is empty: {file_path}")
                    return "Info: Input text file is empty."
                request_contents_list.append(Part.from_text(text_content))
                logging.info(f"Prepared text part for {os.path.basename(file_path)}")
            except Exception as txt_err:
                 logging.error(f"Failed to read text file {file_path}: {txt_err}", exc_info=True)
                 return f"Error: Could not read text file {os.path.basename(file_path)}."

        # --- PDF Handling Block ---
        elif mime_type == "application/pdf":
            print(f"DEBUG: Entering PDF processing block for {os.path.basename(file_path)}") # DEBUG
            if not fitz_available:
                 logging.error("PyMuPDF (fitz) is not available in utils module.")
                 return "Error: PDF processing requires PyMuPDF. Please install it (`pip install PyMuPDF`)."
            doc = None
            try:
                MAX_PDF_PAGES_TO_SEND = 1 # Render only the first page
                doc = utils.fitz.open(file_path) # Use utils.fitz
                num_pages = len(doc)
                logging.info(f"Processing PDF with {num_pages} pages. Sending first {min(num_pages, MAX_PDF_PAGES_TO_SEND)} pages.")
                for page_num in range(min(num_pages, MAX_PDF_PAGES_TO_SEND)):
                    # Assuming render_pdf_page_to_image_bytes is in utils
                    img_bytes = utils.render_pdf_page_to_image_bytes(file_path, page_num)
                    if img_bytes:
                        pdf_image_part = Part.from_data(data=img_bytes, mime_type="image/png")
                        request_contents_list.append(pdf_image_part)
                        logging.info(f"Prepared image part for PDF page {page_num} of {os.path.basename(file_path)}")
                    else:
                        logging.warning(f"Could not render page {page_num} of PDF {file_path}.")
                if not request_contents_list:
                    return f"Error: Could not render any pages from PDF {os.path.basename(file_path)}."
            except Exception as pdf_err:
                 logging.error(f"Failed to process PDF file {file_path}: {pdf_err}", exc_info=True)
                 return f"Error: Could not process PDF file {os.path.basename(file_path)}."
            finally:
                if doc and hasattr(doc, 'is_closed') and not doc.is_closed:
                     try: doc.close()
                     except Exception: pass

        else:
            logging.error(f"Unsupported MIME type: {mime_type} for file {os.path.basename(file_path)}")
            return f"Error: Unsupported file type '{mime_type}'."

        if not request_contents_list:
             logging.error(f"No content parts could be prepared for file: {file_path}")
             return f"Info: No processable content found in file {os.path.basename(file_path)}."

        # --- MODIFIED MODEL SELECTION LOGIC ---
        model = None
        model_name_to_use = None
        # Ensure config attributes are accessible
        # Provide default values directly here if config might not load
        default_tuned_model = "projects/248124319532/locations/europe-west4/models/8219698240602243072"
        default_base_model = "gemini-2.0-flash-lite-001"

        tuned_model_name = getattr(config, 'TUNED_MODEL_ID', default_tuned_model) if config else default_tuned_model
        base_model_name = getattr(config, 'BASE_MODEL_ID', default_base_model) if config else default_base_model


        if model_id_override:
            model_name_to_use = model_id_override
            logging.info(f"Using OVERRIDDEN model: {model_name_to_use}")
            print(f"DEBUG: Using OVERRIDDEN model: {model_name_to_use}") # DEBUG
            if "projects/" in model_name_to_use:
                 try:
                     print(f"DEBUG: Attempting GenerativeModel.from_pretrained('{model_name_to_use}')...") # DEBUG
                     model = vertexai.generative_models.GenerativeModel.from_pretrained(model_name_to_use)
                     logging.info(f"Successfully loaded OVERRIDDEN (tuned) model: {model_name_to_use}")
                     print(f"DEBUG: Loaded OVERRIDDEN tuned model successfully.") # DEBUG
                 except AttributeError as ae:
                     logging.critical(f"AttributeError 'from_pretrained' encountered loading OVERRIDDEN model. Check SDK version/environment. Error: {ae}", exc_info=True)
                     print(f"DEBUG: AttributeError on from_pretrained for OVERRIDDEN tuned model.") # DEBUG
                     return f"Error: SDK Error loading fine-tuned model '{model_name_to_use}' (AttributeError)"
                 except Exception as load_err:
                     logging.error(f"Failed to load overridden tuned model '{model_name_to_use}': {load_err}", exc_info=True)
                     print(f"DEBUG: Failed to load OVERRIDDEN tuned model: {load_err}") # DEBUG
                     return f"Error: Could not load fine-tuned model '{model_name_to_use}'"
            else: # Assume it's a base model ID
                try:
                    print(f"DEBUG: Attempting GenerativeModel('{model_name_to_use}')...") # DEBUG
                    model = vertexai.generative_models.GenerativeModel(model_name_to_use)
                    logging.info(f"Successfully loaded OVERRIDDEN (base) model: {model_name_to_use}")
                    print(f"DEBUG: Loaded OVERRIDDEN base model successfully.") # DEBUG
                except Exception as load_err:
                    logging.error(f"Failed to load overridden base model '{model_name_to_use}': {load_err}", exc_info=True)
                    print(f"DEBUG: Failed to load OVERRIDDEN base model: {load_err}") # DEBUG
                    return f"Error: Could not load base model '{model_name_to_use}'"

        else: # Default to the fine-tuned model if no override
            model_name_to_use = tuned_model_name
            logging.info(f"Using DEFAULT (tuned) model: {model_name_to_use}")
            print(f"DEBUG: Using DEFAULT (tuned) model: {model_name_to_use}") # DEBUG
            try:
                print(f"DEBUG: Attempting GenerativeModel.from_pretrained('{model_name_to_use}')...") # DEBUG
                model = vertexai.generative_models.GenerativeModel.from_pretrained(model_name_to_use)
                logging.info(f"Successfully loaded DEFAULT (tuned) model: {model_name_to_use}")
                print(f"DEBUG: Loaded DEFAULT tuned model successfully.") # DEBUG
            except AttributeError as ae:
                 logging.critical(f"AttributeError 'from_pretrained' encountered loading DEFAULT model. Check SDK version/environment. Error: {ae}", exc_info=True)
                 print(f"DEBUG: AttributeError on from_pretrained for DEFAULT tuned model.") # DEBUG
                 return f"Error: SDK Error loading fine-tuned model '{model_name_to_use}' (AttributeError)"
            except Exception as load_err:
                logging.error(f"Failed to load default tuned model '{model_name_to_use}': {load_err}", exc_info=True)
                print(f"DEBUG: Failed to load DEFAULT tuned model: {load_err}") # DEBUG
                return f"Error: Could not load fine-tuned model '{model_name_to_use}'"
        # --- END MODIFIED MODEL SELECTION ---

        if not model:
             logging.error("Model object could not be instantiated.")
             print("DEBUG: Model object is None after selection block.") # DEBUG
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

        # --- API Call ---
        logging.info(f"Sending request to Vertex AI Gemini model ({model_name_to_use}) for file: {os.path.basename(file_path)}...")
        print(f"DEBUG: Sending request with model: {model_name_to_use}") # DEBUG
        responses = model.generate_content(
            request_contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )
        logging.info(f"Received response from model for file: {os.path.basename(file_path)}.")
        print(f"DEBUG: Received response for {os.path.basename(file_path)}") # DEBUG

        # --- Process the response ---
        analysis_result = "Error: Failed to process model response." # Default error
        try:
            # Check for blocked responses or empty candidates first
            if not responses.candidates:
                 feedback_reason = responses.prompt_feedback.block_reason if hasattr(responses, 'prompt_feedback') and responses.prompt_feedback else "UNKNOWN"
                 logging.error(f"Analysis failed for {os.path.basename(file_path)}. No candidates returned. Reason: {feedback_reason}.")
                 print(f"DEBUG: No candidates in response. Reason: {feedback_reason}") # DEBUG
                 analysis_result = f"Error: Analysis failed. No candidates returned. Reason: {feedback_reason}"
            # Check finish reason
            elif responses.candidates[0].finish_reason != FinishReason.STOP:
                # Use try-except for FinishReason conversion as it might be an int
                try:
                    finish_reason_name = FinishReason(responses.candidates[0].finish_reason).name
                except ValueError:
                    finish_reason_name = f"UNKNOWN_REASON_{responses.candidates[0].finish_reason}"
                logging.error(f"Analysis stopped for {os.path.basename(file_path)} due to finish reason: {finish_reason_name}")
                print(f"DEBUG: Analysis stopped. Finish Reason: {finish_reason_name}") # DEBUG
                analysis_result = f"Error: Analysis stopped due to {finish_reason_name}."
            # Check for empty content parts
            elif not hasattr(responses.candidates[0], 'content') or not responses.candidates[0].content or not responses.candidates[0].content.parts:
                 logging.error(f"Model response for {os.path.basename(file_path)} had no content parts.")
                 print(f"DEBUG: Response has no content parts.") # DEBUG
                 analysis_result = "Error: Model response was empty (no parts)."
            # Try to get text if everything looks okay
            else:
                 try:
                     print("DEBUG: Attempting to access response.text...") # DEBUG
                     analysis_result = responses.text
                     print("DEBUG: Accessed response.text successfully.") # DEBUG
                 except ValueError as e:
                     logging.warning(f"Could not directly access text from response: {e}.")
                     print(f"DEBUG: ValueError accessing response.text: {e}") # DEBUG
                     analysis_result = " ".join(part.text for part in responses.candidates[0].content.parts if hasattr(part, 'text'))
                     if not analysis_result.strip():
                         analysis_result = "Error: Could not parse text from model response parts."

        except Exception as e_resp:
             logging.error(f"Unexpected error processing model response: {e_resp}", exc_info=True)
             print(f"DEBUG: Exception processing response: {e_resp}") # DEBUG
             analysis_result = f"Error: Unexpected error processing response: {e_resp}"

        logging.info(f"Analysis complete for file: {os.path.basename(file_path)}.")
        print(f"DEBUG: Analysis complete for {os.path.basename(file_path)}. Result length: {len(analysis_result)}") # DEBUG
        return analysis_result

    # --- Outer error handling ---
    except FileNotFoundError:
        logging.error(f"Outer FileNotFoundError: {file_path}")
        print(f"DEBUG: Outer FileNotFoundError caught.") # DEBUG
        return "Error: File not found during processing."
    except ImportError as e:
        logging.error(f"ImportError: {e}")
        print(f"DEBUG: Outer ImportError caught: {e}") # DEBUG
        return "Error: Required libraries not installed or import failed."
    except Exception as e:
        logging.error(f"Outer unexpected error for {os.path.basename(file_path)}: {e}", exc_info=True)
        print(f"DEBUG: Outer Exception caught: {type(e).__name__} - {e}") # DEBUG
        return f"Error: An unexpected error occurred during analysis for {os.path.basename(file_path)}: {e}"

# --- End of analyze_content function ---

# --- Keep the __main__ block if used for direct testing ---
# if __name__ == '__main__':
#    # Ensure config and utils are loaded if running directly
#    # Example:
#    # if config and utils:
#    #    # Define base_model_name if needed for direct testing
#    #    base_model_name = "gemini-2.0-flash-lite-001"
#    #    test_file_to_use = os.path.join(config.BASE_DIR, "inputs", "jpeg", "1.jpeg")
#    #    if os.path.exists(test_file_to_use):
#    #        print(f"--- Testing analysis directly for: {os.path.basename(test_file_to_use)} ---")
#    #        # Decide whether to test base or tuned by default when run directly
#    #        result = analyze_content(test_file_to_use, model_id_override=base_model_name)
#    #        # Or use the tuned model: result = analyze_content(test_file_to_use)
#    #        print("\n--- Analysis Result ---")
#    #        print(result)
#    #        print("-----------------------")
#    #    else:
#    #        print(f"Test file not found: '{test_file_to_use}'")
#    # else:
#    #    print("Cannot run direct test: config or utils module not loaded.")
#    pass # Placeholder