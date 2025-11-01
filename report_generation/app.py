import os
import posixpath
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from utils.gcs_utils import list_and_read_llm_files, save_bytes_to_gcs
from utils.vertex_utils import generate_security_report
from utils.pdf_utils import create_pdf_report

app = Flask(__name__)

load_dotenv()

PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
LOCATION = os.environ.get('GCP_LOCATION')
INPUT_BUCKET = os.environ.get('DEFAULT_INPUT_BUCKET')
OUTPUT_BUCKET = os.environ.get('DEFAULT_OUTPUT_BUCKET')
PORT = int(os.environ.get('PORT', 8003)) 

if not all([PROJECT_ID, LOCATION, INPUT_BUCKET, OUTPUT_BUCKET]):
    raise EnvironmentError("FATAL ERROR: Missing one or more required environment variables. Check .env file or deployment environment.")

@app.route('/generate-report', methods=['POST'])
def generate_report_route():
    """
    API endpoint to generate a report based on a scanid and report type.
    Orchestrates calls to GCS, Vertex AI, and PDF utilities.
    """
    
    # --- 1. Get and Validate Input ---
    data = request.get_json()
    scanid = data.get('scanid')
    report_type = data.get('type') # Use 'report_type' to avoid Python keyword 'type'

    if not all([scanid, report_type]):
        return jsonify({"status": "error", "error_message": "Request body must include 'scanid' and 'type' (e.g., 'recon', 'vulnr')."}), 400

    # Basic validation for report_type
    if report_type.lower() not in ['recon', 'vulnr']:
        return jsonify({"status": "error", "error_message": "Invalid report 'type'. Must be 'recon' or 'vulnr'."}), 400

    # --- 2. Construct Paths ---
    try:
        # Input path, e.g., "data/recon_test_1/recon/"
        base_folder_blob = posixpath.join("data", scanid, report_type) + "/"
        
        # Output directory, e.g., "data/recon_test_1/reports/"
        report_save_dir = posixpath.join("data", scanid, "reports")
        
        # Output filename, e.g., "recon_test_1_recon_report.pdf"
        report_filename = f"{scanid}_{report_type}_report.pdf"
        
        # Full output blob path
        output_blob = posixpath.join(report_save_dir, report_filename)
        
    except Exception as e:
        print(f"Error parsing path: {e}")
        return jsonify({"status": "error", "error_message": "Invalid 'scanid' or 'type' format."}), 400

    try:
        compiled_text, service_names, error = list_and_read_llm_files(config.INPUT_BUCKET, base_folder_blob)
        if error:
            return jsonify({"status": "error", "error_message": f"GCS Read Error: {error}"}), 500

        report_dict, error = generate_security_report(PROJECT_ID, LOCATION, compiled_text)        if error:
            return jsonify({"status": "error", "error_message": f"Vertex AI Error: {error}"}), 500

        pdf_bytes = create_pdf_report(report_dict, report_type)

        saved, error = save_bytes_to_gcs(OUTPUT_BUCKET, output_blob, pdf_bytes, 'application/pdf')        if not saved:
            return jsonify({"status": "error", "error_message": f"GCS Write Error: {error}"}), 500

    except Exception as e:
        # Catch-all for unexpected errors
        print(f"Unhandled exception: {e}")
        return jsonify({"status": "error", "error_message": f"An unexpected error occurred: {e}"}), 500

    # --- 4. Return Success Response ---
    final_response = {
        "status": "success",
        "scanid": scanid,
        "report_type": report_type,
        "included_services": service_names,
        "report_location_gcs": f"gs://{OUTPUT_BUCKET}/{output_blob}",        
        "executive_summary": report_dict.get('executive_summary'),
        "correlated_findings": report_dict.get('correlated_findings'),
        "detailed_analysis": report_dict.get('detailed_analysis'),
        "error_message": None
    }
    return jsonify(final_response), 200


if __name__ == '__main__':
    # Use config values to run the app
    app.run(debug=True, port=config.PORT, host='0.0.0.0')

