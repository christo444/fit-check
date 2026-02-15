from flask import Blueprint, jsonify, current_app
from services.pose_service import PoseEstimationService
from services.storage_service import StorageService
import os

pose_bp = Blueprint("pose", __name__)
pose_service = PoseEstimationService()
storage_service = StorageService()


@pose_bp.route("/pose/<outfit_id>", methods=["POST"])
def detect_pose(outfit_id):
    """
    Run MediaPipe pose detection on an uploaded outfit
    
    Args:
        outfit_id: UUID of the outfit to analyze
        
    Returns:
        Pose landmarks, skeleton connections, and body measurements
    """
    try:
        # Get outfit from database
        outfit = storage_service.get_outfit_by_id(outfit_id)
        
        if not outfit:
            return jsonify({"error": "Outfit not found"}), 404
        
        # Extract filename from image_url
        image_url = outfit['image_url']
        filename = image_url.split('/')[-1].split('?')[0]  # Remove query parameters
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Debug logging
        print(f"\n=== Pose Detection Debug ===")
        print(f"Outfit ID: {outfit_id}")
        print(f"Image URL: {image_url}")
        print(f"Extracted filename: {filename}")
        print(f"Looking for file at: {image_path}")
        print(f"File exists: {os.path.exists(image_path)}")
        print("=" * 50)
        
        # Check if file exists locally
        if not os.path.exists(image_path):
            return jsonify({
                "error": "Image file not found locally",
                "hint": "File may have been cleaned up. Try uploading again.",
                "filename": filename,
                "path": image_path
            }), 400
        
        # Run MediaPipe pose detection
        pose_results = pose_service.detect_pose(image_path)
        
        if not pose_results['success']:
            return jsonify({
                "error": "Pose detection failed",
                "details": pose_results.get('error')
            }), 500
        
        return jsonify({
            "success": True,
            "outfit_id": outfit_id,
            "landmarks": pose_results['landmarks'],
            "total_landmarks": pose_results['total_landmarks'],
            "connections": pose_results['connections'],
            "measurements": pose_results['measurements'],
            "image_dimensions": {
                "width": pose_results['image_width'],
                "height": pose_results['image_height']
            }
        }), 200
        
    except Exception as e:
        print(f"Pose detection error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Pose detection failed",
            "details": str(e)
        }), 500
