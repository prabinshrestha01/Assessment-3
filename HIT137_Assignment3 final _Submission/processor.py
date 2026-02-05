"""
this module defines the ImageProcessor class, which encapsulates all the image processing functionalities required by the assignment using OpenCV. It provides static methods for various operations such as converting to grayscale, applying Gaussian blur, performing Canny edge detection, adjusting brightness and contrast, rotating, flipping, and resizing images. Each method takes an input image in BGR format (as used by OpenCV) and returns a processed image in the same format. The class also includes a utility method to ensure that pixel values are properly clipped and cast to uint8 format. The ImageInfo dataclass is a simple container for metadata about the currently loaded image, including its file path and dimensions, along with a property to return a formatted string of the image size.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional

import cv2
import numpy as np


@dataclass(frozen=True)
class ImageInfo:
    """Simple metadata about the currently loaded image."""
    path: str
    width: int
    height: int

    @property
    def size_text(self) -> str:
        return f"{self.width}x{self.height}px"


class ImageProcessor:
    """
    it encapsulates all the image processing functionalities required by the assignment using OpenCV. 
    It provides static methods for various operations such as converting to grayscale, applying Gaussian blur, performing Canny edge detection, adjusting brightness and contrast, rotating, flipping, and resizing images. 
    Each method takes an input image in BGR format (as used by OpenCV) and returns a processed image in the same format. 
    The class also includes a utility method to ensure that pixel values are properly clipped and cast to uint8 format. 
    The ImageInfo dataclass is a simple container for metadata about the currently loaded image, including its file path and dimensions, along with a property to return a formatted string of the image size.
    """

    # ---------- Utilities ----------
    @staticmethod
    def ensure_uint8(img: np.ndarray) -> np.ndarray:
        """Clip and cast to uint8."""
        return np.clip(img, 0, 255).astype(np.uint8)

    @staticmethod
    def to_gray(img_bgr: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def blur_gaussian(img_bgr: np.ndarray, intensity: int) -> np.ndarray:
        """
        Gaussian blur with adjustable intensity.
        intensity: 0..50 (recommended). Kernel size derived from intensity.
        """
        intensity = int(max(0, intensity))
        if intensity == 0:
            return img_bgr.copy()

        # Kernel must be odd and >= 3
        k = max(3, (intensity // 2) * 2 + 1)
        return cv2.GaussianBlur(img_bgr, (k, k), 0)

    @staticmethod
    def edge_canny(img_bgr: np.ndarray, threshold1: int, threshold2: int) -> np.ndarray:
        threshold1 = int(max(0, threshold1))
        threshold2 = int(max(threshold1 + 1, threshold2))
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, threshold1, threshold2)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def adjust_brightness(img_bgr: np.ndarray, beta: int) -> np.ndarray:
        """
        Brightness adjustment by adding beta (-100..100 typically).
        Uses cv2.convertScaleAbs for safe clipping.
        """
        beta = int(beta)
        return cv2.convertScaleAbs(img_bgr, alpha=1.0, beta=beta)

    @staticmethod
    def adjust_contrast(img_bgr: np.ndarray, alpha: float) -> np.ndarray:
        """
        Contrast adjustment by scaling alpha (0.5..3.0 typically).
        """
        alpha = float(alpha)
        alpha = max(0.1, min(alpha, 5.0))
        return cv2.convertScaleAbs(img_bgr, alpha=alpha, beta=0)

    @staticmethod
    def rotate(img_bgr: np.ndarray, degrees: int) -> np.ndarray:
        """
        Rotate image by 90, 180, or 270 degrees (clockwise).
        """
        deg = degrees % 360
        if deg == 90:
            return cv2.rotate(img_bgr, cv2.ROTATE_90_CLOCKWISE)
        if deg == 180:
            return cv2.rotate(img_bgr, cv2.ROTATE_180)
        if deg == 270:
            return cv2.rotate(img_bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)
        # If not one of the required angles, return copy
        return img_bgr.copy()

    @staticmethod
    def flip(img_bgr: np.ndarray, mode: str) -> np.ndarray:
        """
        mode: 'horizontal' or 'vertical'
        """
        if mode == "horizontal":
            return cv2.flip(img_bgr, 1)
        if mode == "vertical":
            return cv2.flip(img_bgr, 0)
        return img_bgr.copy()

    @staticmethod
    def resize(img_bgr: np.ndarray, new_w: int, new_h: int) -> np.ndarray:
        new_w = int(max(1, new_w))
        new_h = int(max(1, new_h))
        return cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
