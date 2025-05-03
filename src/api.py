import os
import tempfile
import sys
import logging
import traceback
from flask import Flask, request, jsonify, make_response
from werkzeug.utils import secure_filename
from flask_cors import CORS

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("google.api_core").setLevel(logging.WARNING)
logging.getLogger("google.auth").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# --- Add src path ---
src_dir = os.path.abspath(os.path.dirname(__file__))
logging.info(f"Script directory (assumed src): {src_dir}")
if os.path.isdir(src_dir):
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
        logging.info(f"Added {src_dir} to sys.path")
    else:
        logging.info(f"{src_dir} already in sys.path")
else:
    logging.error(f"Script directory not found: {src_dir}")
    raise FileNotFoundError(f"Script directory not found: {src_dir}")

# --- Import Project Modules ---
try:
    # Import the function(s) we need
    from vllm_handler import analyze_content, initialize_vertex_ai
    logging.info("Successfully imported from vllm_handler.")
except ImportError as e:
    logging.error(f"Error importing from vllm_handler (checked sys.path, including {src_dir}): {e}")
    # Define dummy functions if import fails
    def initialize_vertex_ai(): logging.warning("Using dummy initialize_vertex_ai"); return True
    def analyze_content(fp, user_prompt, model_id_override=None): # Add user_prompt to dummy signature
        logging.warning(f"Using dummy analyze_content for {fp} with prompt '{user_prompt}'")
        return f"Dummy analysis for {os.path.basename(fp)} based on prompt: '{user_prompt}'"

# --- Initialize Flask App and CORS ---
app = Flask(__name__)
CORS(app) # Enable CORS for all origins by default for local testing

# --- Initialize Vertex AI ---
logging.info("Initializing Vertex AI for API server...")
if not initialize_vertex_ai():
    logging.critical("FATAL: Could not initialize Vertex AI on server startup.")
    # sys.exit("Vertex AI Initialization Failed")
else:
    logging.info("Vertex AI initialized successfully.")

# --- API Endpoint ---
@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def handle_analyze():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
         return _build_cors_preflight_response()

    # Handle POST request
    logging.info("Received POST request to /api/analyze")
    if 'files' not in request.files:
        logging.error("Error: 'files' part not in request.files")
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files')
    # --- Get the prompt text ---
    prompt_text = request.form.get('prompt', '').strip() # Get and strip whitespace
    # --- Log the received prompt ---
    logging.info(f"Received {len(files)} file(s). Prompt: '{prompt_text}'")

    # --- Add validation for prompt ---
    if not prompt_text:
        logging.error("Error: Prompt text is missing or empty.")
        return jsonify({"error": "Prompt text is required"}), 400

    if not files or all(f.filename == '' for f in files):
         logging.error("Error: No files selected or files have no names")
         return jsonify({"error": "No files selected"}), 400

    results = []
    errors = []

    # Create a temporary directory for this request's files
    with tempfile.TemporaryDirectory() as tmpdir:
        logging.info(f"Created temporary directory: {tmpdir}")
        for file in files:
            if file.filename == '':
                logging.warning("Skipping file with empty filename.")
                continue

            filename = secure_filename(file.filename)
            temp_path = os.path.join(tmpdir, filename)

            try:
                logging.info(f"Saving temporary file: {temp_path}")
                file.save(temp_path)
                logging.info(f"File saved. Analyzing with prompt...")

                # --- MODIFIED: Call backend logic with prompt_text ---
                analysis_result = analyze_content(temp_path, prompt_text)
                # ----------------------------------------------------

                logging.info(f"Analysis result snippet for {filename}: {str(analysis_result)[:100]}...")

                if isinstance(analysis_result, str) and analysis_result.startswith("Error:"):
                     logging.warning(f"Analysis error for {filename}: {analysis_result}")
                     errors.append({"filename": filename, "error": analysis_result})
                else:
                     results.append({
                         "filename": filename,
                         "analysis": analysis_result
                     })

            except Exception as e:
                logging.error(f"Server error processing file {filename}: {e}")
                traceback.print_exc()
                errors.append({"filename": filename, "error": f"Server processing error - {type(e).__name__}"})

    logging.info(f"Finished processing. Results: {len(results)}, Errors: {len(errors)}")

    # --- Construct Response ---
    response_data = {}
    status_code = 200

    if errors and not results:
         response_data = {"error": "Analysis failed for all files", "details": errors}
         status_code = 500
         logging.error(f"Responding with 500 - All files failed: {errors}")
    elif errors:
         response_data = {"message": "Partial success", "analysis": results, "errors": errors}
         status_code = 207
         logging.warning(f"Responding with 207 - Partial success. Results: {len(results)}, Errors: {len(errors)}")
    elif not results:
         response_data = {"error": "No analysis could be performed (check file validity or logs)"}
         status_code = 400
         logging.warning("Responding with 400 - No analysis performed.")
    else:
        # --- IMPORTANT: Return only the analysis part for single successful file ---
        # If you always expect only one file, simplify the response structure
        # For multiple files, returning the list `results` is correct as implemented
        if len(results) == 1:
             response_data = {"analysis": results[0]['analysis']} # Return only the analysis string
        else:
             # If handling multiple files, keep the list structure
             response_data = {"analysis": results}

        status_code = 200
        logging.info(f"Responding with 200 - Success for {len(results)} file(s).")

    return jsonify(response_data), status_code

# --- CORS Preflight Helper ---
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*") # Adjust for production
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "POST, OPTIONS")
    logging.info("Responded to CORS preflight (OPTIONS) request.")
    return response

# --- Main Execution ---
if __name__ == '__main__':
    logging.info("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000) # Ensure debug=True for development auto-reload
