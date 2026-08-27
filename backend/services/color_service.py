import cv2
import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple
import webcolors


class ColorExtractionService:
    """
    Service for extracting dominant colors from image regions
    
    Uses K-means clustering to identify the most prominent colors
    in detected clothing items
    """
    
    def __init__(self, n_colors: int = 5):
        """
        Initialize color extraction service
        
        Args:
            n_colors: Number of dominant colors to extract (default: 5)
        """
        self.n_colors = n_colors
        
    def extract_colors(self, image: np.ndarray, bbox: Dict) -> List[Dict]:
        """
        Extract dominant colors from a bounding box region
        
        Args:
            image: Full image as numpy array (BGR format from OpenCV)
            bbox: Bounding box dictionary with x1, y1, x2, y2
            
        Returns:
            List of color dictionaries with RGB, hex, percentage, and name
        """
        try:
            # Extract region of interest
            x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
            roi = image[y1:y2, x1:x2]
            
            # Check if ROI is valid
            if roi.size == 0:
                return []
            
            # Convert BGR to RGB
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            
            # Reshape image to be a list of pixels
            pixels = roi_rgb.reshape(-1, 3)
            
            # Remove very dark pixels (likely shadows/background)
            # Keep pixels with average value > 20
            pixel_means = pixels.mean(axis=1)
            bright_pixels = pixels[pixel_means > 20]
            
            # If too few pixels remain, use all pixels
            if len(bright_pixels) < 100:
                bright_pixels = pixels
            
            # Determine number of colors (use minimum of n_colors and available pixels)
            n_clusters = min(self.n_colors, len(bright_pixels))
            if n_clusters < 1:
                return []
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            kmeans.fit(bright_pixels)
            
            # Get cluster centers (dominant colors)
            colors = kmeans.cluster_centers_.astype(int)
            
            # Count pixels in each cluster
            labels = kmeans.labels_
            label_counts = np.bincount(labels)
            percentages = (label_counts / len(labels)) * 100
            
            # Sort by percentage (most dominant first)
            sorted_indices = np.argsort(percentages)[::-1]
            
            # Build result list
            color_list = []
            for idx in sorted_indices:
                rgb = colors[idx].tolist()
                percentage = float(percentages[idx])
                
                # Skip very small percentages
                if percentage < 2.0:
                    continue
                
                color_dict = {
                    'rgb': rgb,
                    'hex': self._rgb_to_hex(rgb),
                    'percentage': round(percentage, 1),
                    'name': self._get_color_name(rgb)
                }
                
                color_list.append(color_dict)
            
            return color_list
            
        except Exception as e:
            print(f"Color extraction error: {str(e)}")
            return []
    
    def _rgb_to_hex(self, rgb: List[int]) -> str:
        """Convert RGB values to hex color code"""
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    
    def _get_color_name(self, rgb: List[int]) -> str:
        """
        Get the closest CSS3 color name for an RGB value
        
        Args:
            rgb: RGB color as [r, g, b]
            
        Returns:
            Color name string
        """
        try:
            # Try to get exact match
            color_name = webcolors.rgb_to_name(rgb)
            return color_name
        except ValueError:
            # Find closest color name
            min_distance = float('inf')
            closest_name = 'unknown'
            
            # Compare with CSS3 colors
            for name, hex_code in webcolors.CSS3_HEX_TO_NAMES.items():
                r, g, b = webcolors.hex_to_rgb(name)
                # Calculate Euclidean distance in RGB space
                distance = sum((c1 - c2) ** 2 for c1, c2 in zip(rgb, (r, g, b)))
                
                if distance < min_distance:
                    min_distance = distance
                    closest_name = hex_code
            
            return closest_name
    
    def get_dominant_color(self, image: np.ndarray, bbox: Dict) -> Dict:
        """
        Get only the single most dominant color from a region
        
        Args:
            image: Full image as numpy array
            bbox: Bounding box dictionary
            
        Returns:
            Single color dictionary
        """
        colors = self.extract_colors(image, bbox)
        return colors[0] if colors else None
