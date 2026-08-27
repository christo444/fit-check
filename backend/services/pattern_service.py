import cv2
import numpy as np
from typing import Dict, Tuple


class PatternClassificationService:
    """
    Service for classifying clothing patterns using computer vision
    
    Detects patterns like: solid, striped, checkered, floral, graphic, abstract, plain
    Uses edge detection, texture analysis, and frequency domain analysis
    """
    
    def __init__(self):
        """Initialize pattern classification service"""
        pass
    
    def classify_pattern(self, image: np.ndarray, bbox: Dict) -> Dict:
        """
        Classify the pattern in a clothing item
        
        Args:
            image: Full image as numpy array (BGR format)
            bbox: Bounding box dictionary with x1, y1, x2, y2
            
        Returns:
            Dictionary with pattern type and confidence score
        """
        try:
            # Extract region of interest
            x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
            roi = image[y1:y2, x1:x2]
            
            # Check if ROI is valid
            if roi.size == 0:
                return {'type': 'unknown', 'confidence': 0.0}
            
            # Resize to standard size for consistent analysis
            standard_size = (200, 200)
            roi_resized = cv2.resize(roi, standard_size)
            
            # Convert to grayscale for texture analysis
            gray = cv2.cvtColor(roi_resized, cv2.COLOR_BGR2GRAY)
            
            # Calculate features
            edge_score = self._calculate_edge_density(gray)
            variance_score = self._calculate_variance(gray)
            frequency_score = self._analyze_frequency(gray)
            
            # Classify based on features
            pattern_type, confidence = self._determine_pattern(
                edge_score, variance_score, frequency_score
            )
            
            return {
                'type': pattern_type,
                'confidence': round(confidence, 2)
            }
            
        except Exception as e:
            print(f"Pattern classification error: {str(e)}")
            return {'type': 'unknown', 'confidence': 0.0}
    
    def _calculate_edge_density(self, gray_image: np.ndarray) -> float:
        """
        Calculate edge density using Canny edge detection
        High edge density suggests patterns like stripes or checks
        """
        edges = cv2.Canny(gray_image, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        return edge_density
    
    def _calculate_variance(self, gray_image: np.ndarray) -> float:
        """
        Calculate pixel intensity variance
        Low variance suggests solid colors
        High variance suggests complex patterns
        """
        variance = np.var(gray_image)
        # Normalize to 0-1 range (assuming max variance around 10000)
        normalized_variance = min(variance / 10000.0, 1.0)
        return normalized_variance
    
    def _analyze_frequency(self, gray_image: np.ndarray) -> float:
        """
        Analyze frequency domain to detect repetitive patterns
        Uses FFT to detect periodic patterns (stripes, checks)
        """
        # Apply FFT
        f_transform = np.fft.fft2(gray_image)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        
        # Calculate energy in high frequencies (excluding DC component)
        height, width = magnitude.shape
        center_y, center_x = height // 2, width // 2
        
        # Mask out the DC component (center)
        mask = np.ones((height, width))
        mask[center_y-10:center_y+10, center_x-10:center_x+10] = 0
        
        high_freq_energy = np.sum(magnitude * mask)
        total_energy = np.sum(magnitude)
        
        # Ratio of high frequency energy
        freq_ratio = high_freq_energy / (total_energy + 1e-10)
        
        return freq_ratio
    
    def _determine_pattern(self, edge_score: float, variance_score: float, 
                          frequency_score: float) -> Tuple[str, float]:
        """
        Determine pattern type based on calculated features
        
        Returns:
            Tuple of (pattern_type, confidence)
        """
        # Solid/Plain: Low variance, low edges
        if variance_score < 0.15 and edge_score < 0.05:
            return ('solid', 0.85)
        
        # Striped: High frequency, moderate to high edges
        if frequency_score > 0.3 and edge_score > 0.1:
            return ('striped', 0.75)
        
        # Checkered: Very high frequency, high edges
        if frequency_score > 0.4 and edge_score > 0.15:
            return ('checkered', 0.70)
        
        # Graphic/Text: High edges, moderate variance
        if edge_score > 0.15 and variance_score > 0.3:
            return ('graphic', 0.65)
        
        # Floral/Complex: High variance, moderate edges, lower frequency
        if variance_score > 0.4 and edge_score > 0.08 and frequency_score < 0.3:
            return ('floral', 0.60)
        
        # Abstract: Moderate to high variance, varied features
        if variance_score > 0.25:
            return ('abstract', 0.55)
        
        # Plain: Default for simple patterns
        if variance_score < 0.25 and edge_score < 0.1:
            return ('plain', 0.70)
        
        # Unknown: Didn't fit any clear pattern
        return ('textured', 0.50)
    
    def get_pattern_features(self, image: np.ndarray, bbox: Dict) -> Dict:
        """
        Get detailed pattern features for debugging/analysis
        
        Args:
            image: Full image as numpy array
            bbox: Bounding box dictionary
            
        Returns:
            Dictionary with detailed feature scores
        """
        try:
            x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
            roi = image[y1:y2, x1:x2]
            
            if roi.size == 0:
                return {}
            
            roi_resized = cv2.resize(roi, (200, 200))
            gray = cv2.cvtColor(roi_resized, cv2.COLOR_BGR2GRAY)
            
            return {
                'edge_density': round(self._calculate_edge_density(gray), 4),
                'variance': round(self._calculate_variance(gray), 4),
                'frequency_score': round(self._analyze_frequency(gray), 4)
            }
            
        except Exception as e:
            print(f"Feature extraction error: {str(e)}")
            return {}
