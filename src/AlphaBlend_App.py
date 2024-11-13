import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QPushButton, QFileDialog,
                           QSlider, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QImage, QPixmap, QPainter
from base_ip import BaseIP, AlphaSplit
import cv2
import numpy as np

class AlphaBlendingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alpha Blending Editor")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize BaseIP and AlphaSplit
        self.processor = AlphaSplit()

        # Initialize image variables
        self.foreground_img = None
        self.background_pixmap = None
        self.result_pixmap = None
        self.result_img = None  # Keep this for final result

        # Store original images
        self.original_foreground = None  # Store as QImage with alpha
        self.background_cv = None  # Store original CV2 image for final saving
        self.background_size = None

        # Initialize transform parameters
        self.scale_factor = 1.0
        self.x_offset = 0
        self.y_offset = 0
        self.rotation_angle = 0

        self.init_ui()

    def init_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create image display area
        image_layout = QHBoxLayout()

        # Foreground image display
        foreground_widget = QWidget()
        foreground_layout = QVBoxLayout(foreground_widget)
        self.foreground_label = QLabel()
        self.foreground_label.setMinimumSize(300, 300)
        self.foreground_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foreground_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")
        foreground_layout.addWidget(QLabel("Foreground Image (with Alpha)"))
        foreground_layout.addWidget(self.foreground_label)
        load_foreground_btn = QPushButton("Load Foreground")
        load_foreground_btn.clicked.connect(self.load_foreground)
        foreground_layout.addWidget(load_foreground_btn)
        image_layout.addWidget(foreground_widget)

        # Background image display
        background_widget = QWidget()
        background_layout = QVBoxLayout(background_widget)
        self.background_label = QLabel()
        self.background_label.setMinimumSize(300, 300)
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.background_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")
        background_layout.addWidget(QLabel("Background Image"))
        background_layout.addWidget(self.background_label)
        load_background_btn = QPushButton("Load Background")
        load_background_btn.clicked.connect(self.load_background)
        background_layout.addWidget(load_background_btn)
        image_layout.addWidget(background_widget)

        # Result image display
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        self.result_label = QLabel()
        self.result_label.setMinimumSize(300, 300)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")
        result_layout.addWidget(QLabel("Blended Result"))
        result_layout.addWidget(self.result_label)
        save_result_btn = QPushButton("Save Result")
        save_result_btn.clicked.connect(self.save_result)
        save_result_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
            }
        """)
        result_layout.addWidget(save_result_btn)
        image_layout.addWidget(result_widget)

        layout.addLayout(image_layout)

        # Add transform controls
        transform_group = QGroupBox("Transform Controls")
        transform_layout = QVBoxLayout()

        # Scale control
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale:"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(200)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.scale_changed)
        scale_layout.addWidget(self.scale_slider)
        self.scale_spin = QSpinBox()
        self.scale_spin.setMinimum(10)
        self.scale_spin.setMaximum(200)
        self.scale_spin.setValue(100)
        self.scale_spin.valueChanged.connect(self.scale_spin_changed)
        scale_layout.addWidget(self.scale_spin)
        transform_layout.addLayout(scale_layout)

        # Add Rotation control
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotation:"))
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotation_slider.setMinimum(-180)
        self.rotation_slider.setMaximum(180)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self.rotation_changed)
        rotation_layout.addWidget(self.rotation_slider)
        self.rotation_value_label = QLabel("0°")
        rotation_layout.addWidget(self.rotation_value_label)
        transform_layout.addLayout(rotation_layout)

        # X position control
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Position:"))
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setMinimum(-500)
        self.x_slider.setMaximum(1500)
        self.x_slider.setValue(0)
        self.x_slider.valueChanged.connect(self.x_position_changed)
        x_layout.addWidget(self.x_slider)
        self.x_value_label = QLabel("0")
        x_layout.addWidget(self.x_value_label)
        transform_layout.addLayout(x_layout)

        # Y position control
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y Position:"))
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setMinimum(-500)
        self.y_slider.setMaximum(1000)
        self.y_slider.setValue(0)
        self.y_slider.valueChanged.connect(self.y_position_changed)
        y_layout.addWidget(self.y_slider)
        self.y_value_label = QLabel("0")
        y_layout.addWidget(self.y_value_label)
        transform_layout.addLayout(y_layout)

        # Reset button
        reset_btn = QPushButton("Reset Edit")
        reset_btn.clicked.connect(self.reset_transform_controls)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                padding: 8px;
                font-size: 14px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        transform_layout.addWidget(reset_btn)

        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)


    def rotation_changed(self, value):
        self.rotation_angle = value
        self.rotation_value_label.setText(f"{value}")
        self.update_preview()

    def scale_changed(self, value):
        self.scale_spin.setValue(value)
        self.scale_factor = value / 100.0
        self.update_preview()

    def scale_spin_changed(self, value):
        self.scale_slider.setValue(value)
        self.scale_factor = value / 100.0
        self.update_preview()

    def x_position_changed(self, value):
        self.x_offset = value
        self.x_value_label.setText(str(value))
        self.update_preview()

    def y_position_changed(self, value):
        self.y_offset = value
        self.y_value_label.setText(str(value))
        self.update_preview()

    def reset_transform_controls(self):
        """Reset all transform controls to their default values"""
        self.scale_slider.setValue(100)
        self.scale_spin.setValue(100)
        self.x_slider.setValue(0)
        self.y_slider.setValue(0)
        self.rotation_slider.setValue(0)  # Reset rotation
        self.scale_factor = 1.0
        self.x_offset = 0
        self.y_offset = 0
        self.rotation_angle = 0  # Reset rotation angle
        self.x_value_label.setText("0")
        self.y_value_label.setText("0")
        self.rotation_value_label.setText("0°")
        self.update_preview()

    def load_foreground(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Foreground Image", "",
                                                 "Image Files (*.png);;All Files (*)")
        if file_name:
            try:
                fg_cv = self.processor.imread(file_name)
                if fg_cv is not None and fg_cv.shape[2] == 4:
                    # Convert BGRA to RGBA for Qt
                    fg_rgba = cv2.cvtColor(fg_cv, cv2.COLOR_BGRA2RGBA)
                    height, width = fg_rgba.shape[:2]

                    # Create QImage (keeping alpha channel)
                    self.original_foreground = QImage(fg_rgba.data, width, height,
                                                    fg_rgba.strides[0],
                                                    QImage.Format.Format_RGBA8888)

                    # Store a deep copy
                    self.original_foreground = self.original_foreground.copy()

                    # Display foreground
                    self.display_image(self.original_foreground, self.foreground_label)

                    # If background is loaded, resize foreground and update preview
                    if self.background_size is not None:
                        self.resize_foreground_to_background()

                    self.reset_transform_controls()
                else:
                    self.show_error("Please select an image with alpha channel (PNG)")
            except Exception as e:
                self.show_error(f"Error loading foreground: {str(e)}")

    def load_background(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Background Image", "",
                                                 "Image Files (*.png *.jpg *.jpeg);;All Files (*)")
        if file_name:
            try:
                # Store original CV2 image for final saving
                self.background_cv = self.processor.imread(file_name)
                if self.background_cv is not None:
                    # Convert to QPixmap for display
                    height, width = self.background_cv.shape[:2]
                    self.background_size = (width, height)

                    # Convert BGR to RGB for Qt
                    rgb_img = cv2.cvtColor(self.background_cv, cv2.COLOR_BGR2RGB)
                    q_img = QImage(rgb_img.data, width, height, rgb_img.strides[0],
                                 QImage.Format.Format_RGB888)
                    self.background_pixmap = QPixmap.fromImage(q_img)

                    # Display background
                    self.display_image(self.background_pixmap, self.background_label)

                    # If foreground is loaded, resize it and update preview
                    if self.original_foreground is not None:
                        self.resize_foreground_to_background()
                        self.update_preview()
            except Exception as e:
                self.show_error(f"Error loading background: {str(e)}")

    def resize_foreground_to_background(self):
        if self.original_foreground is None or self.background_size is None:
            return

        # Get dimensions
        fg_width = self.original_foreground.width()
        fg_height = self.original_foreground.height()
        bg_width, bg_height = self.background_size

        # Calculate aspect ratios
        fg_aspect_ratio = fg_width / fg_height
        bg_aspect_ratio = bg_width / bg_height

        # Calculate new dimensions maintaining aspect ratio
        if fg_aspect_ratio > bg_aspect_ratio:
            new_width = bg_width
            new_height = int(bg_width / fg_aspect_ratio)
        else:
            new_height = bg_height
            new_width = int(bg_height * fg_aspect_ratio)

        # Create scaled version of foreground
        scaled_fg = self.original_foreground.scaled(
            new_width, new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Create background-sized transparent image
        self.original_foreground = QImage(bg_width, bg_height, QImage.Format.Format_RGBA8888)
        self.original_foreground.fill(Qt.GlobalColor.transparent)

        # Draw scaled foreground centered on the transparent image
        painter = QPainter(self.original_foreground)
        x_offset = (bg_width - new_width) // 2
        y_offset = (bg_height - new_height) // 2
        painter.drawImage(x_offset, y_offset, scaled_fg)
        painter.end()

        # Display resized foreground
        self.display_image(self.original_foreground, self.foreground_label)
        self.update_preview()

    def update_preview(self):
        if self.original_foreground is None or self.background_pixmap is None:
            return

        try:
            # Create a new pixmap from the background
            result = QPixmap(self.background_pixmap)
            painter = QPainter(result)

            # Get current transform values
            scale = self.scale_slider.value() / 100.0
            x_offset = self.x_slider.value()
            y_offset = self.y_slider.value()

            # Calculate scaled size
            scaled_width = int(self.original_foreground.width() * scale)
            scaled_height = int(self.original_foreground.height() * scale)

            # Set composition mode for alpha blending
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # Set up the transformation
            painter.translate(x_offset + scaled_width/2, y_offset + scaled_height/2)
            painter.rotate(self.rotation_angle)
            painter.translate(-scaled_width/2, -scaled_height/2)

            # Draw the transformed foreground
            target_rect = QRect(0, 0, scaled_width, scaled_height)
            painter.drawImage(target_rect, self.original_foreground)

            painter.end()

            # Store and display the preview
            self.result_pixmap = result
            self.display_image(self.result_pixmap, self.result_label)

        except Exception as e:
            self.show_error(f"Error updating preview: {str(e)}")

    def blend_images(self):
        if self.original_foreground is None or self.background_cv is None:
            self.show_error("Please load both foreground and background images")
            return

        try:
            # Convert QImage (original_foreground) to CV2 format for blending
            fg_width = self.original_foreground.width()
            fg_height = self.original_foreground.height()
            fg_ptr = self.original_foreground.bits()
            fg_ptr.setsize(fg_height * fg_width * 4)

            # Convert to numpy array
            fg_arr = np.frombuffer(fg_ptr, np.uint8).reshape(
                fg_height, fg_width, 4
            )

            # Convert RGBA to BGRA
            fg_bgra = cv2.cvtColor(fg_arr, cv2.COLOR_RGBA2BGRA)

            # Split into RGB and alpha
            fg_rgb, alpha = self.processor.split_alpha(fg_bgra)

            # Do the blending
            self.result_img = self.processor.do_blending(
                fg_rgb.copy(),
                self.background_cv.copy(),
                alpha.copy(),
                self.scale_factor,
                self.x_offset,
                self.y_offset
            )
            self.display_image(self.result_img, self.result_label)
        except Exception as e:
            self.show_error(f"Error during blending: {str(e)}")

    def save_result(self):
        if self.result_pixmap is None:
            self.show_error("No result to save")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Result", "",
                                                "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if file_name:
            try:
                # Get current transform values
                scale = self.scale_slider.value() / 100.0
                x_offset = self.x_slider.value()
                y_offset = self.y_slider.value()
                rotation = self.rotation_angle

                # Convert QImage to CV2 format
                fg_width = self.original_foreground.width()
                fg_height = self.original_foreground.height()
                fg_ptr = self.original_foreground.bits()
                fg_ptr.setsize(fg_height * fg_width * 4)

                fg_arr = np.frombuffer(fg_ptr, np.uint8).reshape(
                    fg_height, fg_width, 4
                )

                # Convert RGBA to BGRA
                fg_bgra = cv2.cvtColor(fg_arr, cv2.COLOR_RGBA2BGRA)

                # Split into RGB and alpha
                fg_rgb, alpha = self.processor.split_alpha(fg_bgra)

                # Do the final high-quality blending with rotation
                result = self.processor.do_blending(
                    fg_rgb,
                    self.background_cv,
                    alpha,
                    scale,
                    x_offset,
                    y_offset,
                    rotation  # Add rotation parameter here
                )

                # Save the result
                self.processor.imwrite(file_name, result)

            except Exception as e:
                self.show_error(f"Error saving result: {str(e)}")

    def display_image(self, img, label):
        if isinstance(img, QImage):
            pixmap = QPixmap.fromImage(img)
        elif isinstance(img, QPixmap):
            pixmap = img
        else:
            return

        # Scale image to fit label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)

    def show_error(self, message):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AlphaBlendingApp()
    window.show()
    sys.exit(app.exec())
