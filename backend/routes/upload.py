from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from services.storage_service import StorageService

upload_bp = Blueprint("upload", __name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


@upload_bp.route("/upload", methods=["POST"])
def upload_image():
    """
    Upload an outfit image
    
    Expected: multipart/form-data with 'image' file
    Returns: outfit_id and image_url
    """
    try:
        print(f"\n=== Upload Request Debug ===")
        print(f"Request files: {request.files}")
        print(f"Request form: {request.form}")
        print(f"Content-Type: {request.content_type}")
        print("=" * 50)
        
        # Check if image file is present
        if "image" not in request.files:
            print("ERROR: No image file in request")
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]

        # Check if file is selected
        if file.filename == "":
            print("ERROR: Empty filename")
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Use PNG, JPG, or JPEG"}), 400

        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"

        # Save file temporarily
        temp_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(temp_path)

        # Upload to Supabase Storage and create database record
        storage_service = StorageService()
        result = storage_service.upload_outfit_image(temp_path, unique_filename)

        # Keep the file locally for detection (Phase 2)
        # In production, we'd download from Supabase as needed
        # For now, keep it in uploads folder for YOLO detection

        return jsonify(result), 201

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({"error": "Failed to upload image", "details": str(e)}), 500
