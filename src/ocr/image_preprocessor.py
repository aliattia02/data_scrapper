"""
src/ocr/image_preprocessor.py - Advanced image preprocessing for Arabic OCR
"""
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple
import pytesseract


class ImagePreprocessor:
    """Advanced image preprocessing specifically for Arabic grocery flyers"""
    
    def __init__(self, skip_binarization: bool = False):
        self.min_width = 1000  # Minimum width to upscale to
        self.min_height = 1000  # Minimum height to upscale to
        self.skip_binarization = skip_binarization  # Option for colored flyers
    
    def preprocess(self, image_path: str, skip_binarization: Optional[bool] = None) -> np.ndarray:
        """
        Apply full preprocessing pipeline for OCR
        Returns processed image ready for Tesseract
        
        Args:
            image_path: Path to image file
            skip_binarization: Override instance setting for binarization
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Store original for rotation detection
        original = image.copy()
        
        # Apply preprocessing steps
        image = self._upscale_if_small(image)
        
        # Detect and correct rotation using Tesseract OSD
        image = self._detect_and_rotate(image)
        
        # Improved deskewing with text line detection
        image = self._deskew_with_text_lines(image)
        
        image = self._denoise(image)
        
        # Optionally skip binarization for colored flyers
        skip_binarize = skip_binarization if skip_binarization is not None else self.skip_binarization
        if not skip_binarize:
            image = self._binarize(image)
        
        return image
    
    def _detect_and_rotate(self, image: np.ndarray) -> np.ndarray:
        """
        Detect image orientation using Tesseract OSD (Orientation and Script Detection)
        and rotate if needed
        """
        try:
            # Convert to PIL Image for Tesseract OSD
            if len(image.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image)
            
            # Run OSD to detect orientation
            osd = pytesseract.image_to_osd(pil_image)
            
            # Parse rotation angle from OSD output
            rotation = 0
            for line in osd.split('\n'):
                if 'Rotate:' in line:
                    rotation = int(line.split(':')[1].strip())
                    break
            
            # Apply rotation if needed
            if rotation != 0:
                height, width = image.shape[:2]
                center = (width // 2, height // 2)
                
                # Create rotation matrix
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)
                
                # Calculate new dimensions to avoid cropping
                cos = np.abs(rotation_matrix[0, 0])
                sin = np.abs(rotation_matrix[0, 1])
                new_width = int((height * sin) + (width * cos))
                new_height = int((height * cos) + (width * sin))
                
                # Adjust rotation matrix for new dimensions
                rotation_matrix[0, 2] += (new_width / 2) - center[0]
                rotation_matrix[1, 2] += (new_height / 2) - center[1]
                
                # Rotate image
                image = cv2.warpAffine(
                    image, rotation_matrix, (new_width, new_height),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
        except Exception:
            # If OSD fails, continue with original image
            # Common failures: insufficient text, non-text images, etc.
            pass
        
        return image
    
    def _deskew_with_text_lines(self, image: np.ndarray) -> np.ndarray:
        """
        Improved deskewing using text line detection
        More accurate than edge-based Hough transform for text documents
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply binary threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours to find text-like regions
        text_contours = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter based on aspect ratio and size
            aspect_ratio = w / float(h) if h > 0 else 0
            if 0.1 < aspect_ratio < 20 and w > 10 and h > 10:
                text_contours.append(contour)
        
        if len(text_contours) < 3:
            return image
        
        # Fit minimum area rectangles to text contours
        angles = []
        for contour in text_contours:
            rect = cv2.minAreaRect(contour)
            angle = rect[2]
            
            # Normalize angle
            if angle < -45:
                angle += 90
            
            angles.append(angle)
        
        if not angles:
            return image
        
        # Get median angle (more robust than mean)
        median_angle = np.median(angles)
        
        # Only deskew if angle is significant (> 0.5 degrees)
        if abs(median_angle) > 0.5:
            # Rotate image
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            image = cv2.warpAffine(
                image, rotation_matrix, (width, height),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
        
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
    
    def preprocess_pil_image(self, pil_image: Image.Image, skip_binarization: Optional[bool] = None) -> np.ndarray:
        """
        Preprocess PIL Image object
        Useful when working with PDF pages converted to images
        
        Args:
            pil_image: PIL Image object
            skip_binarization: Override instance setting for binarization
        """
        # Convert PIL to numpy array
        image = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Apply preprocessing
        image = self._upscale_if_small(image)
        image = self._detect_and_rotate(image)
        image = self._deskew_with_text_lines(image)
        image = self._denoise(image)
        
        # Optionally skip binarization for colored flyers
        skip_binarize = skip_binarization if skip_binarization is not None else self.skip_binarization
        if not skip_binarize:
            image = self._binarize(image)
        
        return image
