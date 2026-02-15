from flask import Blueprint, jsonify, current_app
from services.yolo_service import YOLODetectionService
from services.storage_service import StorageService
import os

detect_bp = Blueprint("detect", __name__)
yolo_service = YOLODetectionService()
storage_service = StorageService()


@detect_bp.route("/detect/<outfit_id>", methods=["POST"])
def detect_clothing(outfit_id):
    """
    Run YOLO detection on an uploaded outfit
    
    Args:
        outfit_id: UUID of the outfit to analyze
        
    Returns:
        Detection results with bounding boxes
    """
    try:
        # Get outfit from database
        outfit = storage_service.get_outfit_by_id(outfit_id)
        
        if not outfit:
            return jsonify({"error": "Outfit not found"}), 404
        
        # Check if already processed
        if outfit.get('status') == 'completed':
            return jsonify({
                "message": "Outfit already processed",
                "outfit": outfit
            }), 200
        
        # Update status to processing
        storage_service.update_outfit_status(outfit_id, "processing")
        
        # Extract filename from image_url
        # URL format: https://xxx.supabase.co/storage/v1/object/public/outfits/filename.jpg
        image_url = outfit['image_url']
        filename = image_url.split('/')[-1].split('?')[0]  # Remove query parameters
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Debug logging
        print(f"\n=== Detection Debug ===")
        print(f"Outfit ID: {outfit_id}")
        print(f"Image URL: {image_url}")
        print(f"Extracted filename: {filename}")
        print(f"Looking for file at: {image_path}")
        print(f"File exists: {os.path.exists(image_path)}")
        print(f"Upload folder contents: {os.listdir(current_app.config['UPLOAD_FOLDER'])}")
        print("=" * 50)
        
        # Check if file exists locally
        if not os.path.exists(image_path):
            storage_service.update_outfit_status(outfit_id, "failed")
            return jsonify({
                "error": "Image file not found locally",
                "hint": "File may have been cleaned up. Try uploading again.",
                "filename": filename,
                "path": image_path
            }), 400
        
        # Run YOLO detection
        detection_results = yolo_service.detect_clothing(image_path)
        
        if not detection_results['success']:
            storage_service.update_outfit_status(outfit_id, "failed")
            return jsonify({
                "error": "Detection failed",
                "details": detection_results.get('error')
            }), 500
        
        # Save detection results to database
        # Note: We'll need to add a detections column to the outfit table
        # For now, we'll return the results
        
        # Update outfit status
        storage_service.update_outfit_status(outfit_id, "completed")
        
        return jsonify({
            "success": True,
            "outfit_id": outfit_id,
            "detections": detection_results['detections'],
            "total_detections": detection_results['total_detections'],
            "image_dimensions": {
                "width": detection_results['image_width'],
                "height": detection_results['image_height']
            }
        }), 200
        
    except Exception as e:
        print(f"Detection error: {str(e)}")
        storage_service.update_outfit_status(outfit_id, "failed")
        return jsonify({
            "error": "Detection failed",
            "details": str(e)
        }), 500
