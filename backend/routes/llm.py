"""
LLM Style Analysis Routes
"""
import os
from flask import Blueprint, jsonify, current_app
from services.storage_service import StorageService
from services.llm_service import create_llm_service
from services.yolo_service import YOLODetectionService
from services.pose_service import PoseEstimationService
from services.color_service import ColorExtractionService
from services.pattern_service import PatternClassificationService
from services.fit_service import FitEstimationService
import logging

logger = logging.getLogger(__name__)

llm_bp = Blueprint("llm", __name__)


@llm_bp.route("/analyze-style/<outfit_id>", methods=["POST"])
def analyze_style(outfit_id):
    """
    Analyze outfit style using LLM
    
    POST /api/analyze-style/<outfit_id>
    
    Returns:
        JSON with style analysis, suggestions, keywords, and advice
    """
    try:
        # Get storage service
        storage_service = StorageService()

        # Fetch outfit from database
        outfit = storage_service.get_outfit_by_id(outfit_id)

        if not outfit:
            return jsonify({"error": "Outfit not found"}), 404

        image_url = outfit.get("image_url")

        if not image_url:
            return jsonify({"error": "Outfit has no image URL"}), 400

        # Get local image path
        # Extract filename from URL and remove any query parameters
        filename = image_url.split("/")[-1].split("?")[0]
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
        image_path = os.path.join(upload_folder, filename)

        if not os.path.exists(image_path):
            return jsonify({"error": "Image file not found on server"}), 404

        # Initialize analysis results
        detection_data = None
        pose_data = None
        color_data = None
        fit_data = None

        # Try to run YOLO detection (or get cached results)
        try:
            yolo_service = YOLODetectionService()
            detections = yolo_service.detect_clothing(image_path)
            detection_data = {
                "detections": detections["detections"],
                "total_detections": detections["total_detections"],
                "image_dimensions": detections["image_dimensions"]
            }
            logger.info(f"YOLO detection: {detections['total_detections']} items found")
        except Exception as e:
            logger.warning(f"YOLO detection failed: {e}")

        # Try to run pose detection (or get cached results)
        try:
            pose_service = PoseEstimationService()
            pose_result = pose_service.detect_pose(image_path)
            if pose_result.get("landmarks"):
                pose_data = {
                    "landmarks": pose_result["landmarks"],
                    "measurements": pose_result["measurements"]
                }
                logger.info(f"Pose detection: {len(pose_result['landmarks'])} landmarks found")
        except Exception as e:
            logger.warning(f"Pose detection failed: {e}")

        # Try to run color/pattern extraction (requires detections)
        if detection_data and detection_data.get("detections"):
            try:
                # Read image once for all analyses
                import cv2
                image = cv2.imread(image_path)
                
                color_service = ColorExtractionService()
                pattern_service = PatternClassificationService()
                
                items = []
                for detection in detection_data["detections"]:
                    bbox = detection["bbox"]
                    # Convert bbox to integer coordinates
                    bbox_int = {k: int(v) for k, v in bbox.items()}
                    
                    # Extract colors
                    colors = color_service.extract_colors(image, bbox_int)
                    
                    # Detect pattern
                    pattern = pattern_service.classify_pattern(image, bbox_int)
                    
                    items.append({
                        "class_name": detection["class_name"],
                        "colors": colors,
                        "pattern": pattern
                    })
                
                color_data = {"items": items}
                logger.info(f"Color/pattern extraction: {len(items)} items analyzed")
            except Exception as e:
                logger.warning(f"Color/pattern extraction failed: {e}")

        # Try to run fit analysis (requires detections and pose)
        if detection_data and pose_data:
            try:
                fit_service = FitEstimationService()
                fit_result = fit_service.analyze_fit(
                    detections=detection_data["detections"],
                    measurements=pose_data["measurements"],
                    image_dimensions=detection_data["image_dimensions"]
                )
                fit_data = {
                    "items": fit_result["items"]
                }
                logger.info(f"Fit analysis: {len(fit_result['items'])} items analyzed")
            except Exception as e:
                logger.warning(f"Fit analysis failed: {e}")

        # Check if we have any data to analyze
        logger.info(f"Detection data available: {detection_data is not None}")
        logger.info(f"Pose data available: {pose_data is not None}")
        logger.info(f"Color data available: {color_data is not None}")
        logger.info(f"Fit data available: {fit_data is not None}")
        
        if not any([detection_data, pose_data, color_data, fit_data]):
            return jsonify({
                "error": "No analysis data available",
                "message": "Please run detection, pose, or attribute extraction first"
            }), 400

        # Create LLM service
        llm_service = create_llm_service(current_app.config)
        
        # Debug logging
        logger.info(f"LLM Provider: {current_app.config.get('LLM_PROVIDER')}")
        logger.info(f"LLM Model: {current_app.config.get('LLM_MODEL')}")
        logger.info(f"Groq API Key configured: {bool(current_app.config.get('GROQ_API_KEY'))}")
        logger.info(f"LLM Service created: {llm_service is not None}")
        
        if not llm_service:
            return jsonify({
                "error": "LLM service not configured",
                "message": "Please configure LLM_PROVIDER and API keys in environment variables"
            }), 503

        # Analyze style with LLM
        try:
            style_result = llm_service.analyze_style(
                detection_data=detection_data,
                color_data=color_data,
                pose_data=pose_data,
                fit_data=fit_data
            )
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return jsonify({
                "error": "Style analysis failed",
                "message": str(e)
            }), 500

        # Return structured response
        return jsonify({
            "success": True,
            "outfit_id": outfit_id,
            "style": style_result.get("style", {}),
            "suggestions": style_result.get("suggestions", []),
            "keywords": style_result.get("keywords", []),
            "advice": style_result.get("advice", ""),
            "data_sources": {
                "detection": detection_data is not None,
                "pose": pose_data is not None,
                "colors": color_data is not None,
                "fit": fit_data is not None
            }
        }), 200

    except Exception as e:
        logger.error(f"Style analysis error: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500
