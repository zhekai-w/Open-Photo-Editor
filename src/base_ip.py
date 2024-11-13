import cv2
import numpy as np
from enum import Enum
import os

class ImageType(Enum):
    RGB = "RGB"
    BGR = "BGR"
    RGBA = "RGBA"
    BGRA = "BGRA"
    GRAY = "GRAY"

class BaseIP:
    def __init__(self) -> None:
        self.img_path = "None"
        self.image_type = None

    @staticmethod
    def imread(img_path):
        """Read image from path with error handling and type detection"""
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image path does not exist: {img_path}")

        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Failed to load image: {img_path}")
        return img

    @staticmethod
    def imshow(winname, img):
        """Display image with proper normalization and type handling"""
        if img is None:
            raise ValueError("No image data provided")

        # Convert float images to 8-bit for display
        if img.dtype == np.float32 or img.dtype == np.float64:
            display_img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        else:
            display_img = img

        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
        cv2.imshow(winname, display_img)
        cv2.waitKey(0)
        cv2.destroyWindow(winname)

    @staticmethod
    def imwrite(write_path, img):
        """Save image with error handling"""
        if img is None:
            raise ValueError("No image data to save")

        directory = os.path.dirname(write_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        success = cv2.imwrite(write_path, img)
        if not success:
            raise IOError(f"Failed to save image to {write_path}")

    @staticmethod
    def get_image_type(img):
        """Determine image type based on channels"""
        if img is None:
            return None

        if len(img.shape) == 2:
            return ImageType.GRAY
        elif len(img.shape) == 3:
            channels = img.shape[2]
            if channels == 3:
                return ImageType.BGR  # OpenCV default
            elif channels == 4:
                return ImageType.BGRA
        return None

    @staticmethod
    def normalize_image(img):
        """Normalize image to 0-1 range"""
        if img is None:
            return None

        if img.dtype == np.uint8:
            return img.astype(np.float32) / 255.0
        return img

    @staticmethod
    def denormalize_image(img):
        """Convert normalized image back to uint8"""
        if img is None:
            return None

        if img.dtype == np.float32 or img.dtype == np.float64:
            return (np.clip(img, 0, 1) * 255).astype(np.uint8)
        return img

    @staticmethod
    def check_image_compatibility(img1, img2):
        """Check if two images are compatible for operations"""
        if img1 is None or img2 is None:
            return False

        if img1.shape[:2] != img2.shape[:2]:
            return False

        return True

    @staticmethod
    def resize_image(img, target_size, keep_aspect_ratio=True, background_color=None):
        """
        Resize image to target size with option to maintain aspect ratio

        Args:
            img: Input image
            target_size: Tuple of (width, height)
            keep_aspect_ratio: If True, maintain aspect ratio and pad if necessary
            background_color: Color for padding if keep_aspect_ratio is True
                            (default: [0,0,0] for RGB/BGR, [0,0,0,0] for RGBA/BGRA)

        Returns:
            Resized image
        """
        if img is None:
            return None

        # Get current dimensions
        current_height, current_width = img.shape[:2]
        target_width, target_height = target_size

        if not keep_aspect_ratio:
            # Simple resize without keeping aspect ratio
            return cv2.resize(img, (target_width, target_height),
                            interpolation=cv2.INTER_LINEAR)

        # Calculate aspect ratios
        current_aspect = current_width / current_height
        target_aspect = target_width / target_height

        if current_aspect > target_aspect:
            # Image is wider than target: fit to width
            new_width = target_width
            new_height = int(target_width / current_aspect)
        else:
            # Image is taller than target: fit to height
            new_height = target_height
            new_width = int(target_height * current_aspect)

        # Resize image while maintaining aspect ratio
        resized = cv2.resize(img, (new_width, new_height),
                           interpolation=cv2.INTER_LINEAR)

        # Create background for padding
        channels = img.shape[2] if len(img.shape) > 2 else 1
        if background_color is None:
            background_color = [0] * channels

        # Create canvas with target size
        if channels == 1:
            canvas = np.full((target_height, target_width), background_color[0],
                           dtype=img.dtype)
        else:
            canvas = np.full((target_height, target_width, channels),
                           background_color, dtype=img.dtype)

        # Calculate positioning
        y_offset = (target_height - new_height) // 2
        x_offset = (target_width - new_width) // 2

        # Place resized image on canvas
        canvas[y_offset:y_offset + new_height,
               x_offset:x_offset + new_width] = resized

        return canvas

    @staticmethod
    def transform_image(img, scale_factor, x_offset, y_offset, canvas_size, rotation_angle=0):
        """
        Transform image with scaling, translation and rotation

        Args:
            img: Input image
            scale_factor: Scale multiplier
            x_offset: Horizontal translation
            y_offset: Vertical translation
            canvas_size: (width, height) of output image
            rotation_angle: Rotation in degrees (default: 0)
        """
        if img is None:
            return None

        canvas_width, canvas_height = canvas_size

        # Create empty canvas first
        channels = img.shape[2] if len(img.shape) > 2 else 1
        canvas = np.zeros((canvas_height, canvas_width, channels) if channels > 1 else (canvas_height, canvas_width),
                        dtype=img.dtype)

        # Calculate scaled dimensions
        orig_height, orig_width = img.shape[:2]
        new_width = round(orig_width * scale_factor)
        new_height = round(orig_height * scale_factor)

        # Scale image if needed
        if abs(scale_factor - 1.0) > 0.01:
            resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        else:
            resized = img.copy()

        # Apply rotation if needed
        if rotation_angle != 0:
            center = (new_width // 2, new_height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, -rotation_angle, 1.0)
            resized = cv2.warpAffine(resized, rotation_matrix, (new_width, new_height),
                                    flags=cv2.INTER_LINEAR)

        # Calculate valid regions for both source and destination
        src_x_start = max(0, -x_offset)
        src_y_start = max(0, -y_offset)

        dst_x_start = max(0, x_offset)
        dst_y_start = max(0, y_offset)

        # Calculate widths and heights to copy
        width_to_copy = min(new_width - src_x_start, canvas_width - dst_x_start)
        height_to_copy = min(new_height - src_y_start, canvas_height - dst_y_start)

        # Only proceed if we have valid dimensions
        if width_to_copy > 0 and height_to_copy > 0:
            src_region = resized[src_y_start:src_y_start + height_to_copy,
                            src_x_start:src_x_start + width_to_copy]
            canvas[dst_y_start:dst_y_start + height_to_copy,
                dst_x_start:dst_x_start + width_to_copy] = src_region

        return canvas

class AlphaSplit(BaseIP):
    def __init__(self):
        super().__init__()

    @staticmethod
    def split_alpha(img):
        """Split alpha channel from RGBA/BGRA image"""
        if img is None:
            raise ValueError("No image provided")

        # Check if image has alpha channel
        if len(img.shape) != 3 or img.shape[2] != 4:
            raise ValueError("Image must have an alpha channel (4 channels)")

        # Split the channels
        if BaseIP.get_image_type(img) == ImageType.BGRA:
            b, g, r, a = cv2.split(img)
            bgr = cv2.merge([b, g, r])
        else:  # RGBA
            r, g, b, a = cv2.split(img)
            bgr = cv2.merge([b, g, r])

        return bgr, a

    @staticmethod
    def do_blending(foreground, background, alpha, scale_factor=1.0, x_offset=0, y_offset=0, rotation_angle=0):
        if not all([foreground is not None, background is not None, alpha is not None]):
            raise ValueError("All inputs (foreground, background, alpha) must be provided")

        # Transform foreground and alpha
        transformed_fg = BaseIP.transform_image(foreground, scale_factor, x_offset, y_offset,
                                            (background.shape[1], background.shape[0]), rotation_angle)
        transformed_alpha = BaseIP.transform_image(alpha, scale_factor, x_offset, y_offset,
                                                (background.shape[1], background.shape[0]), rotation_angle)

        # Normalize alpha channel
        alpha_norm = transformed_alpha.astype(np.float32) / 255.0
        if len(alpha_norm.shape) > 2:
            alpha_norm = cv2.cvtColor(alpha_norm, cv2.COLOR_BGR2GRAY)

        # Expand alpha to 3 channels
        alpha_3ch = np.stack([alpha_norm] * 3, axis=2)

        # Perform blending
        foreground_float = transformed_fg.astype(np.float32)
        background_float = background.astype(np.float32)
        blended = (foreground_float * alpha_3ch + background_float * (1 - alpha_3ch)).astype(np.uint8)

        return blended
