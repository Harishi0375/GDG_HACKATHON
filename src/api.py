import os
import tempfile
import sys
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename # For secure filenames

# --- Add src path --- Ensure this matches your project structure
# Assuming api_server.py is in the root, same level as 'src/' and 'frontend/'
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"Added {src_path} to sys.path")

try:
    # Import your existing handler logic from the 'src' directory
    from vllm_handler import analyze_content, initialize_vertex_ai
    print("Successfully imported from vllm_handler.")
except ImportError as e:
    print(f"Error importing from vllm_handler (path: {src_path}): {e}")
    # Define dummy functions if import fails, so Flask can at least start
    def initialize_vertex_ai(): print("WARN: Using dummy initialize_vertex_ai"); return True
    def analyze_content(fp, model_id_override=None): print(f"WARN: Using dummy analyze_content for {fp}"); return f"Dummy analysis for {os.path.basename(fp)}"

app = Flask(__name__)

# --- Configuration ---
# Allow larger file uploads if needed (e.g., 50MB limit)
# app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Initialize Vertex AI once when the server starts
print("Initializing Vertex AI for API server...")
if not initialize_vertex_ai():
    print("FATAL: Could not initialize Vertex AI on server startup.")
    # Consider exiting if Vertex AI is essential for the server to function
    # sys.exit("Vertex AI Initialization Failed")
else:
    print("Vertex AI initialized successfully.")


@app.route('/api/analyze', methods=['POST'])
def handle_analyze():
    print("Received request to /api/analyze") # Debug print
    if 'files' not in request.files:
        print("Error: 'files' part not in request.files")
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files') # Handle multiple files
    prompt_text = request.form.get('prompt', '') # Get the prompt text
    print(f"Received {len(files)} file(s). Prompt: '{prompt_text}'")

    if not files or all(f.filename == '' for f in files):
         print("Error: No files selected or files have no names")
         return jsonify({"error": "No files selected"}), 400

    results = []
    errors = []

    # Create a temporary directory for this request's files
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Created temporary directory: {tmpdir}")
        for file in files:
            if file.filename == '':
                continue # Skip if no filename provided

            # Secure the filename before saving
            filename = secure_filename(file.filename)
            temp_path = os.path.join(tmpdir, filename)

            try:
                print(f"Saving temporary file: {temp_path}")
                file.save(temp_path) # Save the uploaded file
                print(f"File saved. Analyzing...")

                # --- Call your backend logic ---
                # Adapt this if analyze_content needs the prompt text as well
                analysis_result = analyze_content(temp_path)
                # --------------------------------

                print(f"Analysis result for {filename}: {analysis_result[:100]}...") # Log snippet

                if isinstance(analysis_result, str) and analysis_result.startswith("Error:"):
                     errors.append(f"{filename}: {analysis_result}")
                else:
                     # Store result associated with the original filename
                     results.append({
                         "filename": filename,
                         "analysis": analysis_result
                     })

            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                import traceback
                traceback.print_exc() # Print full traceback for debugging
                errors.append(f"{filename}: Server processing error - {type(e).__name__}")
            # temp_path is automatically cleaned up when exiting 'with' block

    print(f"Finished processing. Results: {len(results)}, Errors: {len(errors)}")

    if errors and not results:
         return jsonify({"error": "Analysis failed for all files", "details": errors}), 500
    elif errors:
         # Return partial success with errors
         return jsonify({"message": "Partial success", "results": results, "errors": errors}), 207 # 207 Multi-Status
    elif not results:
         return jsonify({"error": "No analysis could be performed"}), 500
    else:
        # --- How to return multiple results? ---
        # Option 1: Return only the first result (simplest for your current Vue code)
        # final_analysis = results[0]['analysis']

        # Option 2: Concatenate results (if they are strings)
        # final_analysis = "\n\n---\n\n".join([f"Analysis for {r['filename']}:\n{r['analysis']}" for r in results])

        # Option 3: Return the whole list (Vue code needs adjustment to display this)
        final_analysis = results

        print(f"Sending back analysis: {str(final_analysis)[:100]}...")
        # For now, let's return the structure your Vue code might handle best (single string or first result)
        # If you expect multiple files, returning the list (Option 3) is better, adjust Vue accordingly.
        return jsonify({"analysis": results[0]['analysis'] if len(results) == 1 else results })
        #-----------------------------------------

if __name__ == '__main__':
    # Run on port 5000 for local development
    # debug=True auto-reloads when code changes and provides a debugger
    # Use host='0.0.0.0' if you need to access it from another device on your network
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)