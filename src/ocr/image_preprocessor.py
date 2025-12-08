"""
src/ocr/image_preprocessor.py - Advanced image preprocessing for Arabic OCR
"""
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple


class ImagePreprocessor:
    """Advanced image preprocessing specifically for Arabic grocery flyers"""
    
    def __init__(self):
        self.min_width = 1000  # Minimum width to upscale to
        self.min_height = 1000  # Minimum height to upscale to
    
    def preprocess(self, image_path: str) -> np.ndarray:
        """
        Apply full preprocessing pipeline for OCR
        Returns processed image ready for Tesseract
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Apply preprocessing steps
        image = self._upscale_if_small(image)
        image = self._deskew(image)
        image = self._denoise(image)
        image = self._binarize(image)
        
        return image
    
    def _upscale_if_small(self, image: np.ndarray) -> np.ndarray:
        """Upscale image if it's too small for good OCR"""
        height, width = image.shape[:2]
        
        if width < self.min_width or height < self.min_height:
            # Calculate scale factor
            scale_w = self.min_width / width if width < self.min_width else 1.0
            scale_h = self.min_height / height if height < self.min_height else 1.0
            scale = max(scale_w, scale_h)
            
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Use INTER_CUBIC for upscaling
            image = cv2.resize(image, (new_width, new_height), 
                             interpolation=cv2.INTER_CUBIC)
        
        return image
    
    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew image by detecting text orientation
        Uses Hough transform to find dominant angle
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None:
            return image
        
        # Calculate angles
        angles = []
        for line in lines[:20]:  # Use first 20 lines
            rho, theta = line[0]
            angle = np.degrees(theta) - 90
            angles.append(angle)
        
        if not angles:
            return image
        
        # Get median angle
        median_angle = np.median(angles)
        
        # Only deskew if angle is significant (> 0.5 degrees)
        if abs(median_angle) > 0.5:
            # Rotate image
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            image = cv2.warpAffine(image, rotation_matrix, (width, height),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        
        return image
    
    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """
        Remove noise from scanned flyers
        Uses Non-local Means Denoising
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply denoising
        # Parameters optimized for scanned documents
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, 
                                           templateWindowSize=7,
                                           searchWindowSize=21)
        
        return denoised
    
    def _binarize(self, image: np.ndarray) -> np.ndarray:
        """
        Binarize image using Otsu's method
        Best for documents with varying lighting
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Otsu's thresholding
        _, binary = cv2.threshold(gray, 0, 255, 
                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def detect_text_regions(self, image: np.ndarray) -> list:
        """
        Detect text regions using MSER (Maximally Stable Extremal Regions)
        Useful for region-based OCR
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Create MSER detector
        mser = cv2.MSER_create()
        
        # Detect regions
        regions, _ = mser.detectRegions(gray)
        
        # Convert to bounding boxes
        bboxes = []
        for region in regions:
            x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
            # Filter out very small regions
            if w > 20 and h > 20:
                bboxes.append((x, y, w, h))
        
        return bboxes
    
    def preprocess_pil_image(self, pil_image: Image.Image) -> np.ndarray:
        """
        Preprocess PIL Image object
        Useful when working with PDF pages converted to images
        """
        # Convert PIL to numpy array
        image = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Apply preprocessing
        image = self._upscale_if_small(image)
        image = self._deskew(image)
        image = self._denoise(image)
        image = self._binarize(image)
        
        return image
