# src/vllm_handler.py
import logging
import os
from PIL import Image # Keep import for potential use elsewhere or future checks
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
    from . import config
    from . import utils
except ImportError:
    try:
        import config
        import utils
    except ImportError as e:
        logging.error(f"Fallback import failed: {e}")
        config = None
        utils = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("google.api_core").setLevel(logging.WARNING)
logging.getLogger("google.auth").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

_vertex_ai_initialized = False

def initialize_vertex_ai():
    """Initializes Vertex AI if not already done."""
    global _vertex_ai_initialized
    if _vertex_ai_initialized:
        return True

    if config is None:
         logging.error("Config module failed to load. Cannot initialize Vertex AI.")
         return False

    gcp_project_id = getattr(config, 'GCP_PROJECT_ID', None)
    gcp_region = getattr(config, 'GCP_REGION', None)

    if not gcp_project_id or not gcp_region:
         logging.error("GCP_PROJECT_ID or GCP_REGION not configured in config module.")
         return False

    try:
        logging.info(f"Initializing Vertex AI for project '{gcp_project_id}' in region '{gcp_region}'")
        vertexai.init(project=gcp_project_id, location=gcp_region)
        _vertex_ai_initialized = True
        logging.info("Vertex AI initialized successfully.")
        return True
    except Exception as e:
        logging.error(f"FATAL ERROR: Failed to initialize Vertex AI: {e}", exc_info=True)
        return False

# --- MODIFIED FUNCTION SIGNATURE ---
def analyze_content(file_path: str, user_prompt: str, model_id_override: str = None) -> str:
    """
    Analyzes content using a specified Vertex AI Gemini model, incorporating a user prompt.

    Args:
        file_path: Absolute path to the input file.
        user_prompt: The specific question or instruction from the user.
        model_id_override: Optional model ID or endpoint name to override defaults.

    Returns:
        A string containing the analysis result or an error message.
    """
    if not initialize_vertex_ai():
         return "Error: Vertex AI could not be initialized. Check configuration and logs."

    # --- Log the received user prompt ---
    logging.info(f"Analyzing file: {file_path} with user prompt: '{user_prompt[:100]}...'")
    print(f"DEBUG: analyze_content called for: {file_path}")
    print(f"DEBUG: User Prompt Received: '{user_prompt}'")

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        print(f"DEBUG: File does not exist: {file_path}")
        return f"Error: File not found at path '{file_path}'."

    if utils is None:
        logging.error("Utils module failed to load. Cannot determine supported file types.")
        return "Error: Utils module not loaded."

    supported_text_extensions = getattr(utils, 'SUPPORTED_TEXT_EXTENSIONS', {".txt"})
    supported_image_extensions = getattr(utils, 'SUPPORTED_IMAGE_EXTENSIONS', {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"})
    fitz_available = hasattr(utils, 'fitz') and utils.fitz is not None

    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            _, ext = os.path.splitext(file_path.lower())
            if ext == ".pdf": mime_type = "application/pdf"
            elif ext in supported_text_extensions: mime_type = "text/plain"
            elif ext in supported_image_extensions: mime_type = f"image/{ext[1:]}" if ext[1:] else "image/unknown"
            else:
                logging.warning(f"Could not determine MIME type for {file_path}. Skipping.")
                return f"Error: Unsupported file type or unknown extension for {os.path.basename(file_path)}."

        logging.info(f"Processing as MIME type: {mime_type}")
        print(f"DEBUG: Mime type: {mime_type}")
        request_contents_list = [] # Holds the file content parts (image, text, pdf pages)

        # --- File Content Processing (Image, Text, PDF) ---
        # ... (Your existing code for loading file content into request_contents_list) ...
        # --- Image Handling Block (Using manual PNG load, fallback to VertexImage for others) ---
        if mime_type.startswith("image/"):
            if mime_type == "image/png":
                print(f"DEBUG: Entering MANUAL PNG byte loading block for {os.path.basename(file_path)}")
                try:
                    with open(file_path, "rb") as f:
                        image_bytes = f.read()
                    if not image_bytes: raise ValueError("Read 0 bytes from image file.")
                    image_part = Part.from_data(data=image_bytes, mime_type="image/png")
                    request_contents_list.append(image_part)
                    logging.info(f"Prepared image part manually from PNG bytes for {os.path.basename(file_path)}")
                    print("DEBUG: Manual PNG byte loading successful.")
                except FileNotFoundError:
                    logging.error(f"File not found error during manual PNG loading: {file_path}")
                    print(f"DEBUG: FileNotFoundError caught manually loading PNG.")
                    return f"Error: File not found when trying to load PNG image {os.path.basename(file_path)}."
                except Exception as png_err:
                    logging.error(f"Failed to manually load PNG bytes from {file_path}: {png_err}", exc_info=True)
                    print(f"DEBUG: Exception caught manually loading PNG bytes: {type(png_err).__name__} - {png_err}")
                    return f"Error: Could not process PNG file {os.path.basename(file_path)} (Manual Load Error: {png_err})."
            else: # Fallback for JPEG and other image types
                print(f"DEBUG: Entering VertexImage.load_from_file block for {os.path.basename(file_path)} ({mime_type})")
                try:
                    print(f"DEBUG: Attempting VertexImage.load_from_file('{file_path}')...")
                    image_part = Part.from_image(VertexImage.load_from_file(file_path))
                    print("DEBUG: VertexImage.load_from_file successful.")
                    request_contents_list.append(image_part)
                    logging.info(f"Prepared image part using VertexImage for {os.path.basename(file_path)}")
                except FileNotFoundError:
                    logging.error(f"File not found error during VertexImage loading: {file_path}")
                    print(f"DEBUG: FileNotFoundError caught loading image.")
                    return f"Error: File not found when trying to load image {os.path.basename(file_path)}."
                except Exception as img_err:
                     logging.error(f"Failed to load image {file_path} using VertexImage: {img_err}", exc_info=True)
                     print(f"DEBUG: General Exception caught loading image via VertexImage: {type(img_err).__name__} - {img_err}")
                     if isinstance(img_err, AttributeError) and "'NoneType' object has no attribute 'close'" in str(img_err):
                          return f"Error: Could not load or invalid image file {os.path.basename(file_path)} (Internal Library Error)."
                     else:
                          return f"Error: Could not process image file {os.path.basename(file_path)} (Vertex Load Error: {img_err})."
        # --- End Image Handling ---

        # --- Text Handling Block ---
        elif mime_type.startswith("text/"):
            print(f"DEBUG: Entering text processing block for {os.path.basename(file_path)}")
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
            print(f"DEBUG: Entering PDF processing block for {os.path.basename(file_path)}")
            if not fitz_available:
                 logging.error("PyMuPDF (fitz) is not available in utils module.")
                 return "Error: PDF processing requires PyMuPDF. Please install it (`pip install PyMuPDF`)."
            doc = None
            try:
                MAX_PDF_PAGES_TO_SEND = 1 # Limit pages sent for analysis
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
                if not request_contents_list:
                    return f"Error: Could not render any pages from PDF {os.path.basename(file_path)}."
            except Exception as pdf_err:
                 logging.error(f"Failed to process PDF file {file_path}: {pdf_err}", exc_info=True)
                 return f"Error: Could not process PDF file {os.path.basename(file_path)}."
            finally:
                if doc and hasattr(doc, 'is_closed') and not doc.is_closed:
                     try: doc.close()
                     except Exception: pass
        # --- End PDF Handling ---

        else:
            logging.error(f"Unsupported MIME type: {mime_type} for file {os.path.basename(file_path)}")
            return f"Error: Unsupported file type '{mime_type}'."

        if not request_contents_list:
             logging.error(f"No content parts could be prepared for file: {file_path}")
             return f"Info: No processable content found in file {os.path.basename(file_path)}."

        # --- Model Selection Logic ---
        # ... (Your existing model selection logic remains the same) ...
        model = None
        model_name_to_use = None
        # Get IDs from config (ensure config.py is updated and loaded)
        default_tuned_model = getattr(config, 'TUNED_MODEL_ID', None)
        default_base_model = getattr(config, 'BASE_MODEL_ID', "gemini-2.0-flash-lite-001") # Ensure a default base model

        if not default_tuned_model:
            logging.warning("TUNED_MODEL_ID not found or is None in config.py. Defaulting to base model if no override.")
            tuned_model_name = None
        else:
            tuned_model_name = default_tuned_model

        base_model_name = default_base_model

        if model_id_override:
            model_name_to_use = model_id_override
            logging.info(f"Using OVERRIDDEN model: {model_name_to_use}")
            print(f"DEBUG: Using OVERRIDDEN model: {model_name_to_use}")
            try:
                print(f"DEBUG: Attempting GenerativeModel('{model_name_to_use}')...")
                model = GenerativeModel(model_name_to_use) # Use direct instantiation
                logging.info(f"Successfully loaded OVERRIDDEN model: {model_name_to_use}")
                print(f"DEBUG: Loaded OVERRIDDEN model successfully.")
            except Exception as load_err:
                logging.error(f"Failed to load overridden model '{model_name_to_use}': {load_err}", exc_info=True)
                print(f"DEBUG: Failed to load OVERRIDDEN model: {load_err}")
                error_prefix = "endpoint" if "endpoints/" in model_name_to_use else "model"
                if "not found" in str(load_err).lower() or "404" in str(load_err):
                    return f"Error: Could not load {error_prefix} '{model_name_to_use}' (Not Found or No Access)."
                else:
                    return f"Error: Could not load {error_prefix} '{model_name_to_use}' (Load Error: {load_err})."

        else: # Default model logic
            if tuned_model_name and "endpoints/" in tuned_model_name:
                model_name_to_use = tuned_model_name
                logging.info(f"Using DEFAULT (tuned endpoint) model: {model_name_to_use}")
                print(f"DEBUG: Using DEFAULT (tuned endpoint) model: {model_name_to_use}")
                try:
                    print(f"DEBUG: Attempting GenerativeModel('{model_name_to_use}')...")
                    model = GenerativeModel(model_name_to_use) # Use direct instantiation
                    logging.info(f"Successfully loaded DEFAULT (tuned endpoint) model: {model_name_to_use}")
                    print(f"DEBUG: Loaded DEFAULT tuned endpoint model successfully.")
                except Exception as load_err:
                    logging.error(f"Failed to load default tuned endpoint model '{model_name_to_use}': {load_err}", exc_info=True)
                    print(f"DEBUG: Failed to load DEFAULT tuned endpoint model: {load_err}")
                    if "not found" in str(load_err).lower() or "404" in str(load_err):
                        return f"Error: Could not load fine-tuned endpoint '{model_name_to_use}' (Not Found or No Access)."
                    else:
                        return f"Error: Could not load fine-tuned endpoint '{model_name_to_use}' (Load Error: {load_err})."
            else: # Fallback to base model
                 if not tuned_model_name:
                      logging.info(f"Tuned model ID not configured, using DEFAULT (base) model: {base_model_name}")
                 else: # Tuned model ID was set but wasn't an endpoint format
                      logging.warning(f"Configured TUNED_MODEL_ID '{tuned_model_name}' is not an endpoint format. Using DEFAULT (base) model: {base_model_name}")

                 model_name_to_use = base_model_name
                 print(f"DEBUG: Using DEFAULT (base) model: {model_name_to_use}")
                 try:
                    print(f"DEBUG: Attempting GenerativeModel('{model_name_to_use}')...")
                    model = GenerativeModel(model_name_to_use) # Use direct instantiation
                    logging.info(f"Successfully loaded DEFAULT (base) model: {model_name_to_use}")
                    print(f"DEBUG: Loaded DEFAULT base model successfully.")
                 except Exception as load_err:
                    logging.error(f"Failed to load default base model '{model_name_to_use}': {load_err}", exc_info=True)
                    print(f"DEBUG: Failed to load DEFAULT base model: {load_err}")
                    if "not found" in str(load_err).lower() or "404" in str(load_err):
                         return f"Error: Could not load base model '{model_name_to_use}' (Not Found or No Access)."
                    else:
                         return f"Error: Could not load base model '{model_name_to_use}' (Load Error: {load_err})."

        if not model:
             logging.error("Model object could not be instantiated.")
             print("DEBUG: Model object is None after selection block.")
             return "Error: Model object could not be instantiated (check previous errors)."

        # --- Define System Instructions/Structure Prompt ---
        # This prompt tells the model HOW to structure its response.
        system_instructions = """
        Your task is to act as an expert document analyst. Analyze the provided document content meticulously based *only* on the user's request.

        Follow these steps precisely and structure your output exactly as requested by the user, or if the user asks for specific information (like summary, key points, data extraction), structure your output clearly using Markdown headings based on their request.

        If the user asks a general question or requests analysis without specifying format, structure your output using the following default Markdown headings:

        **Document Type:**
        [Identify the type: e.g., Handwritten Notes, Typed Essay, Scientific Paper, Form, Receipt, General Text, PDF Page Image, Bar Chart, Line Graph, Diagram. Note if handwriting is present.]

        **Summary:**
        [Provide a concise 1-2 sentence summary of the main topic or purpose. For charts/graphs, describe what it represents.]

        **Key Information & Localization:**
        [Identify and extract crucial pieces of information relevant to the user's query (main points, arguments, data points from charts/graphs, axis labels, legends, titles, definitions, form fields/values). For EACH piece of information, describe its precise location (Text files: line/paragraph; Images/PDF pages: visual location like 'top-left', 'bar corresponding to 'Category A'', 'X-axis label', 'legend entry for Series 1'). Use bullet points for clarity.]
        * [Extracted Info 1]
            * Location: [Precise location description]
            * Confidence: [High, Medium, or Low]
        * [Extracted Info 2]
            * Location: [Precise location description]
            * Confidence: [High, Medium, or Low]
        * ... (continue for all key pieces relevant to the user's request)

        **Category:**
        [Assign ONE category based on the content from this list: Lecture Notes, Essay Draft, Research Paper, Assignment Submission, Admin Form, Data Visualization, Other. If unsure, state 'Other'.]

        ---
        Respond *only* based on the user's request applied to the provided document content. Do not add information not present in the document.
        """

        # --- Construct the final request content list ---
        # Order: User Prompt -> File Content -> System Instructions
        request_contents = [Part.from_text(user_prompt)] + request_contents_list + [Part.from_text(system_instructions)]
        print(f"DEBUG: Final request_contents length: {len(request_contents)}")
        print(f"DEBUG: First part type: {type(request_contents[0])}, Content snippet: {str(request_contents[0])[:100]}...") # Check user prompt part
        print(f"DEBUG: Last part type: {type(request_contents[-1])}, Content snippet: {str(request_contents[-1])[:100]}...") # Check system instructions part

        # --- Safety and Generation Config ---
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        generation_config = {
            "max_output_tokens": 2048,
            "temperature": 0.3, # Lower temperature for more factual/structured output
            "top_p": 0.95,
            "top_k": 40,
        }

        # --- API Call ---
        logging.info(f"Sending request to Vertex AI Gemini model ({model_name_to_use}) for file: {os.path.basename(file_path)}...")
        print(f"DEBUG: Sending request with model: {model_name_to_use}")
        # Ensure the model object is valid before calling generate_content
        if not isinstance(model, GenerativeModel):
             logging.error("Model object is not a valid GenerativeModel instance before API call.")
             return "Error: Invalid model object before API call."

        responses = model.generate_content(
            request_contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False, # Use stream=False for simpler response handling
        )
        logging.info(f"Received response from model for file: {os.path.basename(file_path)}.")
        print(f"DEBUG: Received response for {os.path.basename(file_path)}")

        # --- Response Processing ---
        analysis_result = "Error: Failed to process model response." # Default error
        try:
            # Use the built-in .text property for convenience if available and valid
            # It handles combining text parts and checks for blocked content.
            analysis_result = responses.text
            logging.info(f"Analysis complete for file: {os.path.basename(file_path)}.")
            print(f"DEBUG: Analysis complete via responses.text. Result length: {len(analysis_result)}")

        except ValueError as e:
            # Handle cases where .text raises ValueError (e.g., blocked content, no text parts)
            logging.warning(f"Could not directly access response.text: {e}. Checking finish reason and parts.")
            print(f"DEBUG: ValueError accessing response.text: {e}")
            # Check finish reason if available
            finish_reason_name = "UNKNOWN"
            if responses.candidates and responses.candidates[0].finish_reason != FinishReason.STOP:
                try: finish_reason_name = FinishReason(responses.candidates[0].finish_reason).name
                except ValueError: finish_reason_name = f"UNKNOWN_REASON_{responses.candidates[0].finish_reason}"
                logging.error(f"Analysis stopped for {os.path.basename(file_path)} due to finish reason: {finish_reason_name}")
                print(f"DEBUG: Analysis stopped. Finish Reason: {finish_reason_name}")
                analysis_result = f"Error: Analysis stopped due to {finish_reason_name}."
            # Check prompt feedback if available
            elif hasattr(responses, 'prompt_feedback') and responses.prompt_feedback and responses.prompt_feedback.block_reason:
                 feedback_reason = responses.prompt_feedback.block_reason
                 logging.error(f"Analysis failed for {os.path.basename(file_path)}. Prompt blocked. Reason: {feedback_reason}.")
                 print(f"DEBUG: Prompt blocked. Reason: {feedback_reason}")
                 analysis_result = f"Error: Analysis failed. Prompt Blocked. Reason: {feedback_reason}"
            # Check if there are any text parts manually as a fallback
            elif responses.candidates and responses.candidates[0].content and responses.candidates[0].content.parts:
                 text_parts = [part.text for part in responses.candidates[0].content.parts if hasattr(part, 'text')]
                 if text_parts:
                     analysis_result = " ".join(text_parts)
                     if not analysis_result.strip(): analysis_result = "Error: Model response parts contained empty text."
                 else: analysis_result = "Error: Could not parse text from model response parts (no text parts found)."
            else:
                analysis_result = f"Error: Analysis failed. Reason: {e}" # Use the ValueError message

        except Exception as e_resp:
             # Catch any other unexpected errors during response processing
             logging.error(f"Unexpected error processing model response: {e_resp}", exc_info=True)
             print(f"DEBUG: Exception processing response: {e_resp}")
             analysis_result = f"Error: Unexpected error processing response: {e_resp}"

        return analysis_result

    # --- Outer error handling ---
    except FileNotFoundError:
        logging.error(f"Outer FileNotFoundError: {file_path}")
        print(f"DEBUG: Outer FileNotFoundError caught.")
        return "Error: File not found during processing."
    except ImportError as e:
        logging.error(f"ImportError: {e}")
        print(f"DEBUG: Outer ImportError caught: {e}")
        return "Error: Required libraries not installed or import failed."
    except Exception as e:
        logging.error(f"Outer unexpected error for {os.path.basename(file_path)}: {e}", exc_info=True)
        print(f"DEBUG: Outer Exception caught: {type(e).__name__} - {e}")
        return f"Error: An unexpected error occurred during analysis for {os.path.basename(file_path)}: {e}"

# --- End of analyze_content function ---
