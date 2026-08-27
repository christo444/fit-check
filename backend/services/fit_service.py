import math
from typing import Dict, List, Optional, Tuple


class FitEstimationService:
    """
    Service for calculating clothing fit and estimating sizes
    
    Takes pose landmarks (body measurements) and YOLO bounding boxes (clothing dimensions)
    to determine fit type and estimate clothing size
    """
    
    def __init__(self):
        """Initialize fit estimation service"""
        
        # Clothing categories
        self.upper_body_items = ['person', 'shirt', 'jacket', 'hoodie', 'dress', 'coat', 'sweater']
        self.lower_body_items = ['pants', 'shorts', 'skirt', 'jeans']
        
        # Fit ratio thresholds
        self.fit_thresholds = {
            'tight': (0.0, 0.8),
            'slim': (0.8, 1.0),
            'regular': (1.0, 1.2),
            'oversized': (1.2, float('inf'))
        }
        
        # Size estimation thresholds (in pixels) - these are normalized for ~500px image height
        # Will be adjusted based on actual image dimensions
        self.size_thresholds = {
            'upper_body': {
                'XS': {'shoulder_width': (0, 200), 'torso_length': (0, 250)},
                'S': {'shoulder_width': (200, 230), 'torso_length': (250, 280)},
                'M': {'shoulder_width': (230, 260), 'torso_length': (280, 320)},
                'L': {'shoulder_width': (260, 290), 'torso_length': (320, 360)},
                'XL': {'shoulder_width': (290, 320), 'torso_length': (360, 400)},
                'XXL': {'shoulder_width': (320, 500), 'torso_length': (400, 600)}
            },
            'lower_body': {
                'XS': {'hip_width': (0, 180), 'leg_length': (0, 250)},
                'S': {'hip_width': (180, 210), 'leg_length': (250, 290)},
                'M': {'hip_width': (210, 240), 'leg_length': (290, 330)},
                'L': {'hip_width': (240, 270), 'leg_length': (330, 370)},
                'XL': {'hip_width': (270, 300), 'leg_length': (370, 410)},
                'XXL': {'hip_width': (300, 500), 'leg_length': (410, 600)}
            }
        }
    
    def analyze_fit(
        self, 
        detections: List[Dict], 
        measurements: Dict,
        image_width: int,
        image_height: int
    ) -> Dict:
        """
        Analyze fit for all detected clothing items
        
        Args:
            detections: List of YOLO detection results
            measurements: Body measurements from pose detection
            image_width: Image width in pixels
            image_height: Image height in pixels
            
        Returns:
            Dictionary with fit analysis for each item
        """
        try:
            # Check if we have required measurements
            if not measurements:
                return {
                    'success': False,
                    'error': 'No body measurements available',
                    'items': []
                }
            
            # Check if we have pose data
            has_pose_data = 'shoulder_width' in measurements or 'hip_width' in measurements
            
            if not has_pose_data:
                return {
                    'success': False,
                    'error': 'Insufficient body measurements for fit analysis',
                    'items': []
                }
            
            # Analyze each detection
            items = []
            for idx, detection in enumerate(detections):
                fit_result = self._analyze_single_item(
                    detection, 
                    measurements, 
                    image_width, 
                    image_height,
                    idx
                )
                if fit_result:
                    items.append(fit_result)
            
            return {
                'success': True,
                'has_pose_data': has_pose_data,
                'body_measurements': measurements,
                'items': items,
                'total_items': len(items)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'items': []
            }
    
    def _analyze_single_item(
        self,
        detection: Dict,
        measurements: Dict,
        image_width: int,
        image_height: int,
        detection_id: int
    ) -> Optional[Dict]:
        """
        Analyze fit for a single clothing item
        
        Args:
            detection: YOLO detection result
            measurements: Body measurements
            image_width: Image width
            image_height: Image height
            detection_id: Detection index
            
        Returns:
            Fit analysis result or None if not applicable
        """
        try:
            class_name = detection['class_name'].lower()
            bbox = detection['bbox']
            
            # Determine if this is upper or lower body item
            is_upper_body = any(item in class_name for item in self.upper_body_items)
            is_lower_body = any(item in class_name for item in self.lower_body_items)
            
            # For 'person' class, treat as full body outfit
            if class_name == 'person':
                is_upper_body = True
            
            if not is_upper_body and not is_lower_body:
                # Skip items that aren't clothing
                return None
            
            # Calculate fit ratio
            fit_data = self._calculate_fit_ratio(
                bbox, 
                measurements, 
                is_upper_body
            )
            
            if not fit_data:
                return None
            
            # Estimate size
            size_data = self._estimate_size(
                measurements,
                is_upper_body,
                image_height
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                class_name,
                fit_data,
                size_data,
                is_upper_body
            )
            
            return {
                'detection_id': detection_id,
                'class_name': class_name,
                'fit_type': fit_data['fit_type'],
                'fit_confidence': fit_data['confidence'],
                'clothing_width': fit_data['clothing_width'],
                'body_width': fit_data['body_width'],
                'fit_ratio': fit_data['ratio'],
                'size_estimate': size_data['size'],
                'size_confidence': size_data['confidence'],
                'reasoning': reasoning
            }
            
        except Exception as e:
            print(f"Error analyzing item {detection_id}: {e}")
            return None
    
    def _calculate_fit_ratio(
        self,
        bbox: Dict,
        measurements: Dict,
        is_upper_body: bool
    ) -> Optional[Dict]:
        """
        Calculate fit ratio by comparing clothing width to body width
        
        Args:
            bbox: Bounding box with x1, y1, x2, y2, width, height
            measurements: Body measurements
            is_upper_body: Whether this is an upper body item
            
        Returns:
            Dictionary with fit type, ratio, and confidence
        """
        try:
            # Get clothing width from bounding box
            clothing_width = bbox['width']
            
            # Get appropriate body width
            if is_upper_body:
                if 'shoulder_width' not in measurements:
                    return None
                body_width = measurements['shoulder_width']
            else:
                if 'hip_width' not in measurements:
                    return None
                body_width = measurements['hip_width']
            
            # Calculate ratio
            if body_width == 0:
                return None
            
            ratio = clothing_width / body_width
            
            # Determine fit type
            fit_type = self._classify_fit_type(ratio)
            
            # Calculate confidence based on how clearly defined the fit is
            confidence = self._calculate_fit_confidence(ratio, fit_type)
            
            return {
                'fit_type': fit_type,
                'ratio': round(ratio, 2),
                'clothing_width': round(clothing_width, 2),
                'body_width': round(body_width, 2),
                'confidence': round(confidence, 2)
            }
            
        except Exception as e:
            print(f"Error calculating fit ratio: {e}")
            return None
    
    def _classify_fit_type(self, ratio: float) -> str:
        """
        Classify fit type based on ratio
        
        Args:
            ratio: Clothing width / body width ratio
            
        Returns:
            Fit type string
        """
        for fit_type, (min_ratio, max_ratio) in self.fit_thresholds.items():
            if min_ratio <= ratio < max_ratio:
                return fit_type
        return 'regular'  # Default
    
    def _calculate_fit_confidence(self, ratio: float, fit_type: str) -> float:
        """
        Calculate confidence score for fit classification
        
        Higher confidence when ratio is clearly within a category
        Lower confidence when near boundaries
        
        Args:
            ratio: Clothing to body width ratio
            fit_type: Classified fit type
            
        Returns:
            Confidence score (0-1)
        """
        min_ratio, max_ratio = self.fit_thresholds[fit_type]
        
        # Calculate distance from boundaries
        if max_ratio == float('inf'):
            # For oversized (no upper bound)
            distance_from_boundary = ratio - min_ratio
            confidence = min(0.95, 0.7 + (distance_from_boundary * 0.1))
        elif min_ratio == 0.0:
            # For tight (no lower bound)
            distance_from_boundary = max_ratio - ratio
            confidence = min(0.95, 0.7 + (distance_from_boundary * 0.2))
        else:
            # For slim and regular (bounded on both sides)
            range_size = max_ratio - min_ratio
            center = (min_ratio + max_ratio) / 2
            distance_from_center = abs(ratio - center)
            relative_distance = distance_from_center / (range_size / 2)
            confidence = max(0.65, min(0.95, 1.0 - (relative_distance * 0.3)))
        
        return confidence
    
    def _estimate_size(
        self,
        measurements: Dict,
        is_upper_body: bool,
        image_height: int
    ) -> Dict:
        """
        Estimate clothing size based on body measurements
        
        Args:
            measurements: Body measurements
            is_upper_body: Whether this is upper body clothing
            image_height: Image height for normalization
            
        Returns:
            Dictionary with size estimate and confidence
        """
        try:
            # Normalize measurements based on image height
            # Standard reference is ~500px height
            normalization_factor = 500.0 / image_height if image_height > 0 else 1.0
            
            # Get appropriate thresholds
            if is_upper_body:
                thresholds = self.size_thresholds['upper_body']
                shoulder_width = measurements.get('shoulder_width', 0) * normalization_factor
                torso_length = measurements.get('torso_length', 0) * normalization_factor
                
                if shoulder_width == 0 and torso_length == 0:
                    return {'size': 'M', 'confidence': 0.5}  # Default
                
                # Score each size
                scores = {}
                for size, ranges in thresholds.items():
                    score = 0
                    count = 0
                    
                    if shoulder_width > 0:
                        sw_min, sw_max = ranges['shoulder_width']
                        if sw_min <= shoulder_width <= sw_max:
                            # Perfect match
                            score += 1.0
                        else:
                            # Partial match based on distance
                            if shoulder_width < sw_min:
                                dist = sw_min - shoulder_width
                            else:
                                dist = shoulder_width - sw_max
                            score += max(0, 1.0 - (dist / 50))  # Penalty decreases with distance
                        count += 1
                    
                    if torso_length > 0:
                        tl_min, tl_max = ranges['torso_length']
                        if tl_min <= torso_length <= tl_max:
                            score += 1.0
                        else:
                            if torso_length < tl_min:
                                dist = tl_min - torso_length
                            else:
                                dist = torso_length - tl_max
                            score += max(0, 1.0 - (dist / 60))
                        count += 1
                    
                    if count > 0:
                        scores[size] = score / count
                
            else:  # Lower body
                thresholds = self.size_thresholds['lower_body']
                hip_width = measurements.get('hip_width', 0) * normalization_factor
                leg_length = measurements.get('left_leg_length', measurements.get('right_leg_length', 0)) * normalization_factor
                
                if hip_width == 0 and leg_length == 0:
                    return {'size': 'M', 'confidence': 0.5}
                
                # Score each size
                scores = {}
                for size, ranges in thresholds.items():
                    score = 0
                    count = 0
                    
                    if hip_width > 0:
                        hw_min, hw_max = ranges['hip_width']
                        if hw_min <= hip_width <= hw_max:
                            score += 1.0
                        else:
                            if hip_width < hw_min:
                                dist = hw_min - hip_width
                            else:
                                dist = hip_width - hw_max
                            score += max(0, 1.0 - (dist / 50))
                        count += 1
                    
                    if leg_length > 0:
                        ll_min, ll_max = ranges['leg_length']
                        if ll_min <= leg_length <= ll_max:
                            score += 1.0
                        else:
                            if leg_length < ll_min:
                                dist = ll_min - leg_length
                            else:
                                dist = leg_length - ll_max
                            score += max(0, 1.0 - (dist / 60))
                        count += 1
                    
                    if count > 0:
                        scores[size] = score / count
            
            # Find best size
            if not scores:
                return {'size': 'M', 'confidence': 0.5}
            
            best_size = max(scores, key=scores.get)
            confidence = scores[best_size]
            
            return {
                'size': best_size,
                'confidence': min(0.95, max(0.6, confidence))
            }
            
        except Exception as e:
            print(f"Error estimating size: {e}")
            return {'size': 'M', 'confidence': 0.5}
    
    def _generate_reasoning(
        self,
        class_name: str,
        fit_data: Dict,
        size_data: Dict,
        is_upper_body: bool
    ) -> str:
        """
        Generate human-readable reasoning for fit analysis
        
        Args:
            class_name: Clothing item class name
            fit_data: Fit calculation results
            size_data: Size estimation results
            is_upper_body: Whether upper body item
            
        Returns:
            Reasoning string
        """
        body_part = "shoulder width" if is_upper_body else "hip width"
        clothing_width = int(fit_data['clothing_width'])
        body_width = int(fit_data['body_width'])
        fit_type = fit_data['fit_type']
        ratio = fit_data['ratio']
        size = size_data['size']
        
        # Calculate percentage difference
        percent_diff = abs((ratio - 1.0) * 100)
        
        # Build reasoning string
        if ratio > 1.0:
            comparison = f"{percent_diff:.0f}% wider than"
        elif ratio < 1.0:
            comparison = f"{percent_diff:.0f}% narrower than"
        else:
            comparison = "equal to"
        
        reasoning = (
            f"The {class_name} width ({clothing_width}px) is {comparison} "
            f"the {body_part} ({body_width}px), indicating a {fit_type} fit. "
            f"Based on body measurements, the estimated size is {size}."
        )
        
        return reasoning
