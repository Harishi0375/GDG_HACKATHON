import os
import logging
import json
import re # Import regular expressions for parsing
from typing import List, Dict, Any, Optional

# Import configuration variables (Input/Output Dirs)
# This assumes config.py is in the same src directory
# and correctly loads variables from .env
try:
    from . import config
except ImportError:
    import config # Fallback for direct execution testing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define supported file extensions (can be expanded)
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
SUPPORTED_TEXT_EXTENSIONS = {".txt"}

def get_input_files(input_dir: str) -> List[str]:
    """
    Scans the input directory and returns a list of absolute paths
    to supported image and text files.

    Args:
        input_dir: The path to the directory containing input files.

    Returns:
        A list of absolute file paths.
    """
    supported_files = []
    if not os.path.isdir(input_dir):
        logging.error(f"Input directory not found or is not a directory: {input_dir}")
        return supported_files # Return empty list

    logging.info(f"Scanning for input files in: {input_dir}")
    try:
        for filename in os.listdir(input_dir):
            # Skip hidden files/folders like .DS_Store
            if filename.startswith('.'):
                continue
            file_path = os.path.join(input_dir, filename)
            if os.path.isfile(file_path):
                _, file_extension = os.path.splitext(filename.lower())
                if file_extension in SUPPORTED_IMAGE_EXTENSIONS or \
                   file_extension in SUPPORTED_TEXT_EXTENSIONS:
                    supported_files.append(os.path.abspath(file_path))
                    logging.debug(f"Found supported file: {file_path}")
                else:
                    logging.debug(f"Skipping unsupported file type: {filename}")
            else:
                logging.debug(f"Skipping non-file item: {filename}")

    except Exception as e:
        logging.error(f"Error scanning input directory {input_dir}: {e}", exc_info=True)

    logging.info(f"Found {len(supported_files)} supported files.")
    return supported_files

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
        # Ensure the output directory exists (config.py should create it, but double-check)
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


# --- NEW FUNCTION: Parse Gemini Analysis Text ---
def parse_gemini_analysis(analysis_text: str) -> Dict[str, Any]:
    """
    Parses the structured text output expected from the Gemini model based on the prompt.

    Args:
        analysis_text: The string output from the Gemini model.

    Returns:
        A dictionary containing parsed sections (Document Type, Summary,
        Key Information & Localization), or a default structure if parsing fails.
    """
    # Default structure to return, including the raw text
    parsed_data = {
        "document_type": "N/A",
        "summary": "N/A",
        "key_info_localization": "N/A", # Store this section as raw text for now
        "raw_text": analysis_text # Always include the original text
    }
    if not analysis_text or analysis_text.startswith("Error:"):
        logging.warning("Analysis text is empty or contains an error, cannot parse.")
        # Include the error message in the raw_text field if it's an error
        if analysis_text and analysis_text.startswith("Error:"):
             parsed_data["raw_text"] = analysis_text # Keep the error message
        return parsed_data # Return default structure

    try:
        # Use regex to find sections based on headings like "**Document Type:**"
        # Making the regex flexible for potential variations (e.g., bolding, colons, whitespace)
        # It looks for the heading and captures everything until the next potential heading or end of string.
        doc_type_match = re.search(r"^\s*\**Document Type:?\**\s*(.*?)(?=\n\s*\**\w+(\s*&\s*\w+)?:?\**\s*\n?|\Z)", analysis_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        summary_match = re.search(r"^\s*\**Summary:?\**\s*(.*?)(?=\n\s*\**\w+(\s*&\s*\w+)?:?\**\s*\n?|\Z)", analysis_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        # Find the start of Key Info section and capture everything after it
        key_info_match = re.search(r"^\s*\**Key Information(?: & Localization)?:?\**\s*\n?(.*)", analysis_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)

        if doc_type_match:
            parsed_data["document_type"] = doc_type_match.group(1).strip()
        else:
            logging.warning("Could not parse 'Document Type' section.")

        if summary_match:
            parsed_data["summary"] = summary_match.group(1).strip()
        else:
             logging.warning("Could not parse 'Summary' section.")

        if key_info_match:
            # Store the whole block for now. More complex parsing could extract individual items later if needed.
            parsed_data["key_info_localization"] = key_info_match.group(1).strip()
        else:
             logging.warning("Could not parse 'Key Information & Localization' section.")

    except Exception as e:
        logging.error(f"Error parsing analysis text: {e}", exc_info=True)
        # Return default structure but indicate parsing error
        parsed_data["document_type"] = "Parsing Error"
        parsed_data["summary"] = "Parsing Error"
        parsed_data["key_info_localization"] = f"Error during parsing: {e}"

    return parsed_data


# --- Example Usage (for testing this script directly) ---
if __name__ == '__main__':
    # This block runs only when the script is executed directly from the root folder using:
    # python -m src.utils

    print(f"--- Testing file scanning in: {config.INPUT_DIR} ---")
    files = get_input_files(config.INPUT_DIR)
    if files:
        print("Found files:")
        for f in files:
            print(f"- {f}")
    else:
        print(f"No supported files found in {config.INPUT_DIR}. Please add some .txt or image files.")

    print(f"\n--- Testing result saving to: {config.OUTPUT_DIR} ---")
    dummy_results = {
        "inputs/file1.txt": {"status": "success", "analysis": "Dummy analysis 1"},
        "inputs/image1.jpg": {"status": "error", "message": "Dummy error 1"}
    }
    save_results_to_json(dummy_results, config.OUTPUT_DIR, config.OUTPUT_FILENAME)
    output_file_path = os.path.join(config.OUTPUT_DIR, config.OUTPUT_FILENAME)
    if os.path.exists(output_file_path):
        print(f"Successfully saved dummy results to {output_file_path}")
    else:
        print(f"Failed to save dummy results to {output_file_path}")

    print("\n--- Testing analysis parsing ---")
    sample_analysis = """
    **Document Type:** Typed essay (scanned image)

    **Summary:** This document discusses the impact of AI on education. It covers benefits and challenges.

    **Key Information & Localization:**
    * Main Point: AI can personalize learning paths (Paragraph 2, near the middle).
    * Data Point: Student engagement increased by 15% (Found in the table titled 'Engagement Metrics', row 'With AI').
    * Definition: VLLM stands for Vision-Language Large Model (First paragraph, approximately line 3).
    * Challenge: Ensuring data privacy is crucial (Section 'Ethical Considerations', first bullet point).
    """
    parsed = parse_gemini_analysis(sample_analysis)
    print("Parsed Data:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False)) # Use ensure_ascii=False here too

    error_analysis = "Error: Model not found."
    parsed_error = parse_gemini_analysis(error_analysis)
    print("\nParsed Error Data:")
    print(json.dumps(parsed_error, indent=2, ensure_ascii=False))

    malformed_analysis = "**Summary:** Only summary found."
    parsed_malformed = parse_gemini_analysis(malformed_analysis)
    print("\nParsed Malformed Data:")
    print(json.dumps(parsed_malformed, indent=2, ensure_ascii=False))

