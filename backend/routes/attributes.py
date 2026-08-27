from flask import Blueprint, jsonify, current_app
from services.yolo_service import YOLODetectionService
from services.color_service import ColorExtractionService
from services.pattern_service import PatternClassificationService
from services.storage_service import StorageService
import cv2
import os

attributes_bp = Blueprint("attributes", __name__)
yolo_service = YOLODetectionService()
color_service = ColorExtractionService(n_colors=5)
pattern_service = PatternClassificationService()
storage_service = StorageService()


@attributes_bp.route("/attributes/<outfit_id>", methods=["POST"])
def extract_attributes(outfit_id):
    """
    Extract color and pattern attributes for detected clothing items
    
    Args:
        outfit_id: UUID of the outfit to analyze
        
    Returns:
        JSON with per-item color and pattern attributes
    """
    try:
        # Get outfit from database
        outfit = storage_service.get_outfit_by_id(outfit_id)
        
        if not outfit:
            return jsonify({"error": "Outfit not found"}), 404
        
        # Extract filename from image URL
        image_url = outfit['image_url']
        filename = image_url.split('/')[-1].split('?')[0]
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists locally
        if not os.path.exists(image_path):
            return jsonify({
                "error": "Image file not found locally",
                "hint": "File may have been cleaned up. Try uploading again.",
                "filename": filename
            }), 400
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({"error": "Failed to load image"}), 500
        
        # Run YOLO detection to get bounding boxes
        detection_results = yolo_service.detect_clothing(image_path)
        
        if not detection_results['success']:
            return jsonify({
                "error": "Detection failed",
                "details": detection_results.get('error')
            }), 500
        
        detections = detection_results['detections']
        
        if len(detections) == 0:
            return jsonify({
                "success": True,
                "outfit_id": outfit_id,
                "items": [],
                "message": "No clothing items detected in image"
            }), 200
        
        # Extract attributes for each detected item
        items = []
        
        for idx, detection in enumerate(detections):
            bbox = detection['bbox']
            
            # Extract colors
            colors = color_service.extract_colors(image, bbox)
            
            # Classify pattern
            pattern = pattern_service.classify_pattern(image, bbox)
            
            item = {
                'detection_id': idx,
                'class_name': detection['class_name'],
                'class_id': detection['class_id'],
                'confidence': detection['confidence'],
                'bbox': bbox,
                'colors': colors,
                'pattern': pattern
            }
            
            items.append(item)
        
        return jsonify({
            "success": True,
            "outfit_id": outfit_id,
            "items": items,
            "total_items": len(items),
            "image_dimensions": {
                "width": detection_results['image_width'],
                "height": detection_results['image_height']
            }
        }), 200
        
    except Exception as e:
        print(f"Attribute extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Attribute extraction failed",
            "details": str(e)
        }), 500
