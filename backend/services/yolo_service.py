from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Tuple
import os


class YOLODetectionService:
    """
    Service for detecting clothing items using YOLOv8
    
    Detects: person, shirt, pants, shoes, jacket, dress, hoodie, etc.
    Returns bounding boxes, confidence scores, and class labels
    """
    
    def __init__(self):
        """Initialize YOLO model"""
        # Using YOLOv8 nano model (fastest, good for clothing detection)
        self.model = YOLO('yolov8n.pt')  # Downloads automatically on first run
        
        # Clothing-related classes from COCO dataset
        # YOLO is pre-trained on COCO which includes these classes
        self.clothing_classes = {
            0: 'person',
            24: 'backpack',
            26: 'handbag',
            27: 'tie',
            28: 'suitcase',
            31: 'skis',
            32: 'snowboard',
            # Note: YOLO's base model doesn't have specific clothing classes
            # For now, we'll detect persons and later add custom clothing detection
        }
        
        # Confidence threshold
        self.confidence_threshold = 0.25
        
    def detect_clothing(self, image_path: str) -> Dict:
        """
        Detect clothing items in an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing detections with bounding boxes and confidence scores
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Get image dimensions
            height, width = image.shape[:2]
            
            # Run YOLO detection
            results = self.model(image, conf=self.confidence_threshold)
            
            # Extract detections
            detections = []
            
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get box coordinates (xyxy format)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get confidence and class
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    # Create detection object
                    detection = {
                        'class_id': class_id,
                        'class_name': class_name,
                        'confidence': round(confidence, 3),
                        'bbox': {
                            'x1': int(x1),
                            'y1': int(y1),
                            'x2': int(x2),
                            'y2': int(y2),
                            'width': int(x2 - x1),
                            'height': int(y2 - y1)
                        }
                    }
                    
                    detections.append(detection)
            
            return {
                'success': True,
                'image_width': width,
                'image_height': height,
                'detections': detections,
                'total_detections': len(detections)
            }
            
        except Exception as e:
            print(f"Detection error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'detections': []
            }
    
    def draw_detections(self, image_path: str, detections: List[Dict], output_path: str) -> bool:
        """
        Draw bounding boxes on image and save
        
        Args:
            image_path: Original image path
            detections: List of detection dictionaries
            output_path: Path to save annotated image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Draw each detection
            for detection in detections:
                bbox = detection['bbox']
                class_name = detection['class_name']
                confidence = detection['confidence']
                
                # Get coordinates
                x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
                
                # Choose color based on class (for variety)
                color = self._get_color_for_class(class_name)
                
                # Draw rectangle
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                
                # Create label
                label = f"{class_name} {confidence:.2f}"
                
                # Get text size for background
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                
                # Draw label background
                cv2.rectangle(
                    image,
                    (x1, y1 - label_height - 10),
                    (x1 + label_width, y1),
                    color,
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    image,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )
            
            # Save annotated image
            cv2.imwrite(output_path, image)
            return True
            
        except Exception as e:
            print(f"Error drawing detections: {str(e)}")
            return False
    
    def _get_color_for_class(self, class_name: str) -> Tuple[int, int, int]:
        """Get consistent color for each class"""
        colors = {
            'person': (0, 255, 0),      # Green
            'backpack': (255, 0, 0),    # Blue
            'handbag': (255, 0, 255),   # Magenta
            'tie': (0, 255, 255),       # Yellow
            'suitcase': (255, 165, 0),  # Orange
        }
        return colors.get(class_name, (0, 200, 200))  # Default cyan
