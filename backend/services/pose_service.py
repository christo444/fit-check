import mediapipe as mp
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import math


class PoseEstimationService:
    """
    Service for detecting body pose using MediaPipe
    
    Detects 33 body landmarks including:
    - Face (nose, eyes, ears, mouth)
    - Upper body (shoulders, elbows, wrists, hands)
    - Torso (hips)
    - Lower body (knees, ankles, feet)
    
    Returns pose keypoints, skeleton connections, and body measurements
    """
    
    def __init__(self):
        """Initialize MediaPipe Pose"""
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize pose detector
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,  # 0, 1, or 2 (highest accuracy)
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Landmark connections for drawing skeleton
        self.POSE_CONNECTIONS = self.mp_pose.POSE_CONNECTIONS
        
    def detect_pose(self, image_path: str) -> Dict:
        """
        Detect body pose in an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing pose keypoints, connections, and measurements
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Get image dimensions
            height, width = image.shape[:2]
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image with MediaPipe
            results = self.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return {
                    'success': False,
                    'error': 'No person detected in image',
                    'landmarks': [],
                    'connections': [],
                    'measurements': {}
                }
            
            # Extract landmarks
            landmarks = []
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks.append({
                    'id': idx,
                    'name': self._get_landmark_name(idx),
                    'x': landmark.x,  # Normalized [0, 1]
                    'y': landmark.y,  # Normalized [0, 1]
                    'z': landmark.z,  # Depth (relative to hips)
                    'visibility': landmark.visibility
                })
            
            # Get skeleton connections
            connections = self._get_connections()
            
            # Calculate body measurements
            measurements = self._calculate_measurements(landmarks, width, height)
            
            return {
                'success': True,
                'landmarks': landmarks,
                'total_landmarks': len(landmarks),
                'connections': connections,
                'measurements': measurements,
                'image_width': width,
                'image_height': height
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'landmarks': [],
                'connections': [],
                'measurements': {}
            }
    
    def _get_landmark_name(self, idx: int) -> str:
        """Get human-readable landmark name"""
        landmark_names = {
            0: 'nose',
            1: 'left_eye_inner',
            2: 'left_eye',
            3: 'left_eye_outer',
            4: 'right_eye_inner',
            5: 'right_eye',
            6: 'right_eye_outer',
            7: 'left_ear',
            8: 'right_ear',
            9: 'mouth_left',
            10: 'mouth_right',
            11: 'left_shoulder',
            12: 'right_shoulder',
            13: 'left_elbow',
            14: 'right_elbow',
            15: 'left_wrist',
            16: 'right_wrist',
            17: 'left_pinky',
            18: 'right_pinky',
            19: 'left_index',
            20: 'right_index',
            21: 'left_thumb',
            22: 'right_thumb',
            23: 'left_hip',
            24: 'right_hip',
            25: 'left_knee',
            26: 'right_knee',
            27: 'left_ankle',
            28: 'right_ankle',
            29: 'left_heel',
            30: 'right_heel',
            31: 'left_foot_index',
            32: 'right_foot_index'
        }
        return landmark_names.get(idx, f'landmark_{idx}')
    
    def _get_connections(self) -> List[Tuple[int, int]]:
        """Get list of landmark connections for drawing skeleton"""
        return [(start, end) for start, end in self.POSE_CONNECTIONS]
    
    def _calculate_measurements(self, landmarks: List[Dict], width: int, height: int) -> Dict:
        """Calculate body measurements from landmarks"""
        try:
            # Helper function to get landmark by name
            def get_landmark(name: str) -> Optional[Dict]:
                for lm in landmarks:
                    if lm['name'] == name:
                        return lm
                return None
            
            # Helper function to calculate distance
            def calculate_distance(lm1: Dict, lm2: Dict, use_pixels: bool = True) -> float:
                if use_pixels:
                    x1, y1 = lm1['x'] * width, lm1['y'] * height
                    x2, y2 = lm2['x'] * width, lm2['y'] * height
                else:
                    x1, y1 = lm1['x'], lm1['y']
                    x2, y2 = lm2['x'], lm2['y']
                return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            
            measurements = {}
            
            # Shoulder width
            left_shoulder = get_landmark('left_shoulder')
            right_shoulder = get_landmark('right_shoulder')
            if left_shoulder and right_shoulder:
                measurements['shoulder_width'] = round(
                    calculate_distance(left_shoulder, right_shoulder), 2
                )
            
            # Hip width
            left_hip = get_landmark('left_hip')
            right_hip = get_landmark('right_hip')
            if left_hip and right_hip:
                measurements['hip_width'] = round(
                    calculate_distance(left_hip, right_hip), 2
                )
            
            # Body height (shoulder to ankle)
            left_ankle = get_landmark('left_ankle')
            if left_shoulder and left_ankle:
                measurements['body_height'] = round(
                    calculate_distance(left_shoulder, left_ankle), 2
                )
            
            # Arm length (shoulder to wrist)
            left_wrist = get_landmark('left_wrist')
            if left_shoulder and left_wrist:
                measurements['left_arm_length'] = round(
                    calculate_distance(left_shoulder, left_wrist), 2
                )
            
            right_wrist = get_landmark('right_wrist')
            if right_shoulder and right_wrist:
                measurements['right_arm_length'] = round(
                    calculate_distance(right_shoulder, right_wrist), 2
                )
            
            # Leg length (hip to ankle)
            if left_hip and left_ankle:
                measurements['left_leg_length'] = round(
                    calculate_distance(left_hip, left_ankle), 2
                )
            
            right_ankle = get_landmark('right_ankle')
            if right_hip and right_ankle:
                measurements['right_leg_length'] = round(
                    calculate_distance(right_hip, right_ankle), 2
                )
            
            # Torso length (shoulder to hip)
            if left_shoulder and left_hip:
                measurements['torso_length'] = round(
                    calculate_distance(left_shoulder, left_hip), 2
                )
            
            # Body proportions (ratios)
            if 'shoulder_width' in measurements and 'hip_width' in measurements:
                measurements['shoulder_to_hip_ratio'] = round(
                    measurements['shoulder_width'] / measurements['hip_width'], 2
                )
            
            if 'torso_length' in measurements and 'left_leg_length' in measurements:
                measurements['torso_to_leg_ratio'] = round(
                    measurements['torso_length'] / measurements['left_leg_length'], 2
                )
            
            return measurements
            
        except Exception as e:
            print(f"Error calculating measurements: {e}")
            return {}
    
    def draw_pose(self, image_path: str, output_path: str) -> bool:
        """
        Draw pose skeleton on image and save
        
        Args:
            image_path: Path to input image
            output_path: Path to save annotated image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return False
            
            # Draw landmarks and connections
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                self.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Save annotated image
            cv2.imwrite(output_path, image)
            return True
            
        except Exception as e:
            print(f"Error drawing pose: {e}")
            return False
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'pose'):
            self.pose.close()
