# src/utils.py
import os
import logging
import json
import re # Import regular expressions for parsing
from typing import List, Dict, Any, Optional, Tuple, Generator
import io # For handling image bytes

# Try importing fitz (PyMuPDF) and handle potential ImportError
try:
    import fitz # PyMuPDF
except ImportError:
    logging.warning("PyMuPDF library not found. PDF processing will be disabled. "
                    "Install it using: pip install PyMuPDF")
    fitz = None # Set fitz to None if not installed

# Import configuration variables (Input/Output Dirs)
# This assumes config.py is in the same src directory
# and correctly loads variables from .env
try:
    from . import config
except ImportError:
    import config # Fallback for direct execution testing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define supported file extensions ---
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
SUPPORTED_TEXT_EXTENSIONS = {".txt"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}
# Combine all supported extensions for easier checking
ALL_SUPPORTED_EXTENSIONS = SUPPORTED_TEXT_EXTENSIONS | SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_PDF_EXTENSIONS

# --- UPDATED FUNCTION: Recursively find input files ---
def get_input_files(input_dir: str) -> List[str]:
    """
    Recursively scans the input directory and its subdirectories, returning
    a list of absolute paths to supported image, text, and PDF files.

    Args:
        input_dir: The path to the root directory containing input files/subfolders.

    Returns:
        A list of absolute file paths.
    """
    supported_files = []
    if not os.path.isdir(input_dir):
        logging.error(f"Input directory not found or is not a directory: {input_dir}")
        return supported_files # Return empty list

    logging.info(f"Recursively scanning for supported files in: {input_dir}")
    try:
        # os.walk yields (directory_path, subdirectories, filenames) for each directory
        for dirpath, dirnames, filenames in os.walk(input_dir):
            # Optional: Skip hidden directories if needed
            # dirnames[:] = [d for d in dirnames if not d.startswith('.')]

            for filename in filenames:
                # Skip hidden files
                if filename.startswith('.'):
                    continue

                # Check if the file extension is supported
                _, file_extension = os.path.splitext(filename.lower())
                if file_extension in ALL_SUPPORTED_EXTENSIONS:
                    # Special check for PDF if PyMuPDF is not installed
                    if file_extension in SUPPORTED_PDF_EXTENSIONS and not fitz:
                        logging.warning(f"Skipping PDF file due to missing PyMuPDF: {filename}")
                        continue

                    full_path = os.path.join(dirpath, filename)
                    supported_files.append(os.path.abspath(full_path)) # Store absolute path
                    logging.debug(f"Found supported file: {full_path}")
                else:
                    logging.debug(f"Skipping unsupported file type: {filename}")

    except Exception as e:
        logging.error(f"Error scanning input directory {input_dir}: {e}", exc_info=True)

    logging.info(f"Found {len(supported_files)} supported files across all subdirectories.")
    return supported_files
# --- END OF UPDATED FUNCTION ---

def save_results_to_json(results_data: Dict[str, Any], output_dir: str, filename: str):
    """
    Saves the analysis results dictionary to a JSON file.

    Args:
        results_data: A dictionary where keys are filenames and values are analysis results.
        output_dir: The path to the directory where the JSON file will be saved.
        filename: The name for the output JSON file (e.g., "results.json").
    """
    output_filepath = os.path.join(output_dir, filename)
    logging.info(f"Saving results to: {output_filepath}")

    try:
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            logging.warning(f"Output directory did not exist. Creating: {output_dir}")
            os.makedirs(output_dir)

        with open(output_filepath, 'w', encoding='utf-8') as f:
            # Use ensure_ascii=False to handle potential non-ASCII characters in analysis
            json.dump(results_data, f, indent=4, ensure_ascii=False)
        logging.info("Results saved successfully.")

    except TypeError as e:
        logging.error(f"Failed to serialize results to JSON: {e}. Data: {results_data}", exc_info=True)
    except IOError as e:
        logging.error(f"Failed to write results to file {output_filepath}: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred while saving results: {e}", exc_info=True)


# --- UPDATED FUNCTION: Parse Gemini Analysis Text (with Category) ---
def parse_gemini_analysis(analysis_text: str) -> Dict[str, Any]:
    """
    Parses the structured text output expected from the Gemini model based on the prompt.

    Args:
        analysis_text: The string output from the Gemini model.

    Returns:
        A dictionary containing parsed sections (Document Type, Summary,
        Key Information & Localization, Category), or a default structure if parsing fails.
    """
    # Default structure to return, including the raw text and new category field
    parsed_data = {
        "document_type": "N/A",
        "summary": "N/A",
        "key_info_localization": "N/A",
        "category": "N/A", # Added category field
        "raw_text": analysis_text # Always include the original text
    }
    if not analysis_text or analysis_text.startswith("Error:") or analysis_text.startswith("Info:"):
        logging.warning("Analysis text is empty or contains an error/info message, cannot parse.")
        # Include the error/info message in the raw_text field
        if analysis_text:
             parsed_data["raw_text"] = analysis_text # Keep the message
        return parsed_data # Return default structure

    try:
        # Use regex to find sections based on headings like "**Document Type:**"
        # Regex looks for heading, captures content until next potential heading or end of string.
        # Made regex slightly more robust to variations in spacing and optional colons
        doc_type_match = re.search(r"^\s*\**Document Type:?\**\s*(.*?)(?=\n\s*\**\w+(\s*&\s*\w+)?\s*:?\**\s*\n?|\Z)", analysis_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        summary_match = re.search(r"^\s*\**Summary:?\**\s*(.*?)(?=\n\s*\**\w+(\s*&\s*\w+)?\s*:?\**\s*\n?|\Z)", analysis_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        # Allow "Key Information & Localization" or just "Key Information"
        key_info_match = re.search(r"^\s*\**Key Information(?: & Localization)?:?\**\s*\n?(.*?)(?=\n\s*\**\w+(\s*&\s*\w+)?\s*:?\**\s*\n?|\Z)", analysis_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        category_match = re.search(r"^\s*\**Category:?\**\s*(.*?)(?=\n\s*\**\w+(\s*&\s*\w+)?\s*:?\**\s*\n?|\Z)", analysis_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)


        if doc_type_match:
            parsed_data["document_type"] = doc_type_match.group(1).strip()
        else:
            logging.warning("Could not parse 'Document Type' section.")

        if summary_match:
            parsed_data["summary"] = summary_match.group(1).strip()
        else:
             logging.warning("Could not parse 'Summary' section.")

        if key_info_match:
            parsed_data["key_info_localization"] = key_info_match.group(1).strip()
        else:
             logging.warning("Could not parse 'Key Information & Localization' section.")

        # Extract the category
        if category_match:
            parsed_data["category"] = category_match.group(1).strip()
        else:
             logging.warning("Could not parse 'Category' section.")


    except Exception as e:
        logging.error(f"Error parsing analysis text: {e}", exc_info=True)
        # Return default structure but indicate parsing error
        parsed_data["document_type"] = "Parsing Error"
        parsed_data["summary"] = "Parsing Error"
        parsed_data["key_info_localization"] = "Parsing Error"
        parsed_data["category"] = "Parsing Error" # Indicate error here too

    return parsed_data


# --- UPDATED FUNCTION: Render PDF Page to Image Bytes ---
def render_pdf_page_to_image_bytes(pdf_path: str, page_num: int, zoom: int = 2) -> Optional[bytes]:
    """
    Renders a specific page of a PDF file into PNG image bytes using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file.
        page_num: The page number to render (0-indexed).
        zoom: The zoom factor to apply (higher zoom = higher resolution). Default is 2.

    Returns:
        PNG image data as bytes, or None if an error occurs or PyMuPDF is not installed.
    """
    if not fitz:
        logging.error("PyMuPDF (fitz) is not installed. Cannot render PDF.")
        return None

    doc = None # Initialize doc to None
    try:
        doc = fitz.open(pdf_path)
        if page_num < 0 or page_num >= len(doc):
            logging.error(f"Invalid page number {page_num} for PDF {pdf_path} with {len(doc)} pages.")
            # Ensure doc is closed before returning None
            if doc: doc.close()
            return None

        page = doc.load_page(page_num)

        # Configure the matrix for zooming
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Use tobytes() instead of save() for in-memory bytes
        img_bytes = pix.tobytes(output="png") # Get bytes directly

        doc.close() # Close the PDF document
        logging.debug(f"Successfully rendered page {page_num} of {pdf_path} to image bytes.")
        return img_bytes

    except Exception as e:
        logging.error(f"Failed to render page {page_num} of PDF {pdf_path}: {e}", exc_info=True)
        # Ensure doc is closed even if error occurs during rendering
        if doc:
            try:
                doc.close()
            except Exception as close_err:
                logging.error(f"Error closing PDF document after rendering error: {close_err}")
        return None


# --- Example Usage (for testing this script directly) ---
if __name__ == '__main__':
    # This block runs only when the script is executed directly from the root folder using:
    # python -m src.utils

    # Test the updated get_input_files function
    print(f"--- Testing recursive file scanning in: {config.INPUT_DIR} ---")
    files = get_input_files(config.INPUT_DIR) # Use the updated function
    if files:
        print("Found files:")
        for f in files:
            print(f"- {f}")
    else:
        print(f"No supported files found recursively in {config.INPUT_DIR}.")

    # --- Other tests remain the same ---
    print(f"\n--- Testing result saving to: {config.OUTPUT_DIR} ---")
    dummy_results = {
        "inputs/file1.txt": {"status": "success", "analysis": "Dummy analysis 1"},
        "inputs/image1.jpg": {"status": "error", "message": "Dummy error 1"}
    }
    # Ensure config defines OUTPUT_FILENAME
    output_filename = getattr(config, 'OUTPUT_FILENAME', 'results.json') # Use default if not in config
    save_results_to_json(dummy_results, config.OUTPUT_DIR, output_filename)
    output_file_path = os.path.join(config.OUTPUT_DIR, output_filename)
    if os.path.exists(output_file_path):
        print(f"Successfully saved dummy results to {output_file_path}")
    else:
        print(f"Failed to save dummy results to {output_file_path}")

    print("\n--- Testing analysis parsing ---")
    sample_analysis_with_category = """
    **Document Type:** Typed essay (scanned image)

    **Summary:** This document discusses the impact of AI on education. It covers benefits and challenges.

    **Key Information & Localization:**
    * Main Point: AI can personalize learning paths (Paragraph 2, near the middle).
    * Data Point: Student engagement increased by 15% (Found in the table titled 'Engagement Metrics', row 'With AI').
    * Definition: VLLM stands for Vision-Language Large Model (First paragraph, approximately line 3).
    * Challenge: Ensuring data privacy is crucial (Section 'Ethical Considerations', first bullet point).

    **Category:** Research Paper
    """
    parsed = parse_gemini_analysis(sample_analysis_with_category)
    print("Parsed Data (with Category):")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))

    error_analysis = "Error: Model not found."
    parsed_error = parse_gemini_analysis(error_analysis)
    print("\nParsed Error Data:")
    print(json.dumps(parsed_error, indent=2, ensure_ascii=False))

    malformed_analysis = "**Summary:** Only summary found."
    parsed_malformed = parse_gemini_analysis(malformed_analysis)
    print("\nParsed Malformed Data:")
    print(json.dumps(parsed_malformed, indent=2, ensure_ascii=False))


    # --- Testing PDF Rendering (Add a PDF to inputs/pdf/ or other subfolder) ---
    print("\n--- Testing PDF Rendering ---")
    # Try finding an example PDF within the potentially nested structure
    example_pdf_found = None
    for f_path in files: # Use the list of files found recursively
        if f_path.lower().endswith(".pdf"):
            example_pdf_found = f_path
            break

    if example_pdf_found:
        print(f"Attempting to render page 0 of {example_pdf_found}")
        img_bytes = render_pdf_page_to_image_bytes(example_pdf_found, 0)
        if img_bytes:
            print(f"Successfully rendered page 0 to {len(img_bytes)} bytes.")
            # Optionally save the image bytes to a file for verification
            try:
                # Ensure output dir exists
                os.makedirs(config.OUTPUT_DIR, exist_ok=True)
                render_output_path = os.path.join(config.OUTPUT_DIR, "rendered_page_0.png")
                with open(render_output_path, "wb") as img_file:
                    img_file.write(img_bytes)
                print(f"Saved rendered page to {render_output_path}")
            except Exception as save_err:
                print(f"Error saving rendered image: {save_err}")
        else:
            print("Failed to render PDF page.")
    else:
        print(f"No example PDF file found within '{config.INPUT_DIR}' or its subdirectories to test rendering.")