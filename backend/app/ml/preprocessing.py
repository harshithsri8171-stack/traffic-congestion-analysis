import cv2
import numpy as np
from typing import Tuple, Optional


class VideoPreprocessor:
    """Preprocess video frames for traffic analysis"""

    def __init__(self, target_size: Tuple[int, int] = (1280, 720)):
        """
        Initialize video preprocessor

        Args:
            target_size: Target frame size (width, height)
        """
        self.target_size = target_size

    def resize_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Resize frame to target size

        Args:
            frame: Input frame

        Returns:
            Resized frame
        """
        return cv2.resize(frame, self.target_size)

    def denoise(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction to frame

        Args:
            frame: Input frame

        Returns:
            Denoised frame
        """
        return cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)

    def enhance_contrast(self, frame: np.ndarray) -> np.ndarray:
        """
        Enhance frame contrast using CLAHE

        Args:
            frame: Input frame

        Returns:
            Contrast-enhanced frame
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # Merge channels and convert back to BGR
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        return enhanced

    def preprocess_frame(
        self,
        frame: np.ndarray,
        resize: bool = True,
        denoise: bool = False,
        enhance: bool = True
    ) -> np.ndarray:
        """
        Apply full preprocessing pipeline

        Args:
            frame: Input frame
            resize: Whether to resize frame
            denoise: Whether to apply denoising
            enhance: Whether to enhance contrast

        Returns:
            Preprocessed frame
        """
        processed = frame.copy()

        if resize:
            processed = self.resize_frame(processed)

        if denoise:
            processed = self.denoise(processed)

        if enhance:
            processed = self.enhance_contrast(processed)

        return processed

    def extract_frames(
        self,
        video_path: str,
        frame_skip: int = 5
    ) -> list:
        """
        Extract frames from video

        Args:
            video_path: Path to video file
            frame_skip: Process every Nth frame

        Returns:
            List of extracted frames
        """
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_skip == 0:
                processed_frame = self.preprocess_frame(frame)
                frames.append(processed_frame)

            frame_count += 1

        cap.release()
        return frames
