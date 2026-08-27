from flask import Blueprint, jsonify, current_app
from services.fit_service import FitEstimationService
from services.yolo_service import YOLODetectionService
from services.pose_service import PoseEstimationService
from services.storage_service import StorageService
import os

fit_bp = Blueprint("fit", __name__)
fit_service = FitEstimationService()
yolo_service = YOLODetectionService()
pose_service = PoseEstimationService()
storage_service = StorageService()


@fit_bp.route("/fit/<outfit_id>", methods=["POST"])
def analyze_fit(outfit_id):
    """
    Analyze clothing fit and estimate size for an uploaded outfit
    
    This endpoint orchestrates:
    1. YOLO detection to get clothing bounding boxes
    2. MediaPipe pose detection to get body measurements
    3. Fit analysis to compare clothing dimensions to body measurements
    
    Args:
        outfit_id: UUID of the outfit to analyze
        
    Returns:
        Fit analysis with fit type, size estimate, and reasoning for each item
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
        print(f"\n=== Fit Analysis Debug ===")
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
        
        # Step 1: Run YOLO detection to get clothing bounding boxes
        print("Step 1: Running YOLO detection...")
        detection_results = yolo_service.detect_clothing(image_path)
        
        if not detection_results['success']:
            return jsonify({
                "error": "YOLO detection failed",
                "details": detection_results.get('error')
            }), 500
        
        if detection_results['total_detections'] == 0:
            return jsonify({
                "error": "No clothing items detected in image",
                "hint": "Make sure the image contains clothing or a person"
            }), 400
        
        print(f"Found {detection_results['total_detections']} detections")
        
        # Step 2: Run pose detection to get body measurements
        print("Step 2: Running pose detection...")
        pose_results = pose_service.detect_pose(image_path)
        
        if not pose_results['success']:
            return jsonify({
                "error": "Pose detection failed",
                "details": pose_results.get('error'),
                "hint": "Fit analysis requires a person in the image for body measurements"
            }), 400
        
        print(f"Found {len(pose_results['measurements'])} body measurements")
        
        # Step 3: Analyze fit
        print("Step 3: Analyzing fit...")
        fit_results = fit_service.analyze_fit(
            detections=detection_results['detections'],
            measurements=pose_results['measurements'],
            image_width=detection_results['image_width'],
            image_height=detection_results['image_height']
        )
        
        if not fit_results['success']:
            return jsonify({
                "error": "Fit analysis failed",
                "details": fit_results.get('error')
            }), 500
        
        print(f"Analyzed {fit_results['total_items']} items")
        
        # Return comprehensive results
        return jsonify({
            "success": True,
            "outfit_id": outfit_id,
            "has_pose_data": fit_results['has_pose_data'],
            "body_measurements": fit_results['body_measurements'],
            "items": fit_results['items'],
            "total_items": fit_results['total_items'],
            "image_dimensions": {
                "width": detection_results['image_width'],
                "height": detection_results['image_height']
            }
        }), 200
        
    except Exception as e:
        print(f"Fit analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Fit analysis failed",
            "details": str(e)
        }), 500
