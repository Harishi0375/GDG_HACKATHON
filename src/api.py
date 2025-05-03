# src/api.py
import os
import tempfile
import sys
import logging # Keep logging for basicConfig
import traceback
# Import Flask components needed
from flask import Flask, request, jsonify, make_response # Removed 'g' as it wasn't used
from werkzeug.utils import secure_filename
from flask_cors import CORS # Import CORS

# --- Configure Logging (Keep basicConfig for initial setup) ---
# Configures the root logger. Flask's app logger will inherit this level unless configured otherwise.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Reduce noise from Google libraries
logging.getLogger("google.api_core").setLevel(logging.WARNING)
logging.getLogger("google.auth").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# --- Add src path ---
# Get the directory containing the current script (api.py)
src_dir = os.path.abspath(os.path.dirname(__file__))
# Use root logger here as app context isn't available yet
logging.info(f"Script directory (assumed src): {src_dir}")

# Add src_dir to sys.path if it's not already there
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
    # Now imports should work because src_dir is in sys.path
    from vllm_handler import analyze_content, initialize_vertex_ai
    logging.info("Successfully imported from vllm_handler.") # Use root logger
except ImportError as e:
    logging.error(f"Error importing from vllm_handler: {e}") # Use root logger
    # Define dummy functions if import fails, useful for testing API layer
    def initialize_vertex_ai(): logging.warning("Using dummy initialize_vertex_ai"); return True
    def analyze_content(fp, user_prompt, model_id_override=None): logging.warning(f"Using dummy analyze_content for {fp}"); return f"Dummy analysis for {os.path.basename(fp)}"


# --- Initialize Flask App and CORS ---
app = Flask(__name__)
# Configure Flask logger level if needed (INFO should be fine)
# app.logger.setLevel(logging.INFO)

# Enable CORS for the app using Flask-CORS defaults.
# This should handle OPTIONS preflight requests automatically.
CORS(app)


# --- Initialize Vertex AI ---
# Use Flask's app.logger once the app object exists
app.logger.info("Initializing Vertex AI for API server...")
if not initialize_vertex_ai():
    app.logger.critical("FATAL: Could not initialize Vertex AI on server startup.")
else:
    app.logger.info("Vertex AI initialized successfully.")


# --- Request Logging Hook ---
@app.before_request
def log_request_info():
    """Log details of incoming requests before routing."""
    log_message = (
        f"Incoming Request -- "
        f"Method: {request.method}, "
        f"Path: {request.path}, "
        f"Origin: {request.headers.get('Origin', 'N/A')}, "
        f"Remote Addr: {request.remote_addr}"
        # Uncomment below to log all headers (can be verbose)
        # f", Headers: {dict(request.headers)}"
    )
    app.logger.info(log_message) # Use app.logger


# --- API Endpoint ---
# Only POST is needed now, as Flask-CORS handles OPTIONS
@app.route('/api/analyze', methods=['POST'])
def handle_analyze():
    """Handles file uploads and analysis requests."""

    # POST request handling starts here
    app.logger.info("Handling POST request to /api/analyze")

    # Check if the 'files' part is present in the request
    if 'files' not in request.files:
        app.logger.error("Error: 'files' part not in request.files")
        return jsonify({"error": "No files part in the request"}), 400

    # Get the list of files and the prompt text
    files = request.files.getlist('files')
    prompt_text = request.form.get('prompt', '').strip() # Get prompt and remove leading/trailing whitespace
    app.logger.info(f"Received {len(files)} file(s). Prompt: '{prompt_text[:100]}...'") # Log snippet

    # Validate prompt presence
    if not prompt_text:
        app.logger.error("Error: Prompt text is missing or empty.")
        return jsonify({"error": "Prompt text is required"}), 400

    # Validate file presence
    if not files or all(f.filename == '' for f in files):
         app.logger.error("Error: No files selected or files have no names")
         return jsonify({"error": "No files selected"}), 400

    results = [] # To store successful analysis results
    errors = [] # To store errors for specific files

    # Create a temporary directory to store uploaded files securely
    with tempfile.TemporaryDirectory() as tmpdir:
        app.logger.info(f"Created temporary directory: {tmpdir}")
        for file in files:
            # Skip files with no filename
            if file.filename == '':
                app.logger.warning("Skipping file with empty filename.")
                continue

            # Secure the filename to prevent path traversal issues
            filename = secure_filename(file.filename)
            temp_path = os.path.join(tmpdir, filename)

            try:
                app.logger.info(f"Saving temporary file: {temp_path}")
                file.save(temp_path) # Save the uploaded file to the temp directory
                app.logger.info(f"File saved. Analyzing with prompt...")

                # --- Call your backend analysis logic ---
                analysis_result = analyze_content(temp_path, prompt_text)
                # ----------------------------------------

                app.logger.info(f"Analysis result snippet for {filename}: {str(analysis_result)[:100]}...")

                # Check if the analysis function returned an error string
                if isinstance(analysis_result, str) and analysis_result.startswith("Error:"):
                     app.logger.warning(f"Analysis error for {filename}: {analysis_result}")
                     errors.append({"filename": filename, "error": analysis_result})
                else:
                     # Store successful result associated with the original filename
                     results.append({
                         "filename": filename,
                         "analysis": analysis_result
                     })

            except Exception as e:
                # Catch unexpected errors during file processing or analysis call
                app.logger.error(f"Server error processing file {filename}: {e}")
                traceback.print_exc() # Print full traceback to server logs for debugging
                errors.append({"filename": filename, "error": f"Server processing error - {type(e).__name__}"})
            # The temporary file (temp_path) is automatically cleaned up when exiting the 'with' block

    app.logger.info(f"Finished processing all files. Results: {len(results)}, Errors: {len(errors)}")

    # --- Construct Response ---
    response_data = {}
    status_code = 200

    if errors and not results:
         # All files failed analysis
         response_data = {"error": "Analysis failed for all files", "details": errors}
         status_code = 500 # Internal Server Error might be appropriate
         app.logger.error(f"Responding with {status_code} - All files failed: {errors}")
    elif errors:
         # Some files succeeded, some failed
         response_data = {"message": "Partial success", "analysis": results, "errors": errors}
         status_code = 207 # Multi-Status
         app.logger.warning(f"Responding with {status_code} - Partial success. Results: {len(results)}, Errors: {len(errors)}")
    elif not results:
         # No files could be processed (e.g., skipped) but no explicit errors
         response_data = {"error": "No analysis could be performed (check file validity or logs)"}
         status_code = 400 # Bad Request
         app.logger.warning(f"Responding with {status_code} - No analysis performed.")
    else:
        # All files successful
        # If expecting only one file, return analysis directly. Otherwise return list.
        if len(results) == 1:
             response_data = {"analysis": results[0]['analysis']}
        else:
             response_data = {"analysis": results} # Keep as list for multiple files
        status_code = 200 # OK
        app.logger.info(f"Responding with {status_code} - Success for {len(results)} file(s).")

    # Return JSON response with appropriate status code
    return jsonify(response_data), status_code


# --- Main Execution (Only for running locally, not used by Gunicorn/Cloud Run) ---
if __name__ == '__main__':
    # This block allows running the Flask development server directly
    # e.g., python src/api.py
    app.logger.info("Starting Flask server directly for local testing on http://0.0.0.0:5000 ...")
    # Use host='0.0.0.0' to be accessible on your local network
    # debug=True enables auto-reload and provides more detailed error pages (DO NOT use in production)
    app.run(host='0.0.0.0', port=5000, debug=True)

