from google.cloud import storage
import posixpath

def list_and_read_llm_files(bucket_name, base_folder_blob):
    """
    Lists all files under a base folder, finds all files in 'llm' subdirectories,
    reads them, and compiles them into a single string.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    if not base_folder_blob.endswith('/'):
        base_folder_blob += '/'
        
    print(f"Scanning for 'llm' files in: gs://{bucket_name}/{base_folder_blob}")
    
    compiled_text = ""
    service_names = set()
    files_read = []

    blobs = storage_client.list_blobs(bucket_name, prefix=base_folder_blob)
    
    for blob in blobs:
        path_parts = blob.name.split('/')
        if 'llm' in path_parts:
            try:
                llm_index = path_parts.index('llm')
                service_name = path_parts[llm_index - 1]
                service_names.add(service_name)
                
                print(f"Reading file: {blob.name}")
                file_content = blob.download_as_text()
                
                compiled_text += f"\n\n--- START OF {service_name.upper()} SCAN ({blob.name}) ---\n"
                compiled_text += file_content
                compiled_text += f"\n--- END OF {service_name.upper()} SCAN ---\n"
                files_read.append(blob.name)

            except Exception as e:
                print(f"Failed to read or process blob {blob.name}: {e}")

    if not files_read:
        return None, None, f"No files found in any 'llm' subdirectories under {base_folder_blob}"

    print(f"Successfully compiled text from {len(files_read)} files across services: {service_names}")
    return compiled_text, list(service_names), None

def save_bytes_to_gcs(bucket_name, blob_name, file_bytes, content_type):
    """Saves raw bytes (like a PDF) to a GCS bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.upload_from_string(
            file_bytes, 
            content_type=content_type
        )
        print(f"Successfully saved file to '{blob_name}' in bucket '{bucket_name}'.")
        return True, None
    except Exception as e:
        print(f"Error saving to GCS: {e}")
        return False, str(e)
