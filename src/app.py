from cv2IP_module import *
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QSlider, QPushButton, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np

class PhotoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Editor")
        self.setGeometry(100, 100, 1000, 600)

        # Initialize variables
        self.original_image = None
        self.current_image = None

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create image display area
        self.image_label = QLabel()
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("QLabel { background-color: #f0f0f0; }")
        layout.addWidget(self.image_label)

        # Create controls panel
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        layout.addWidget(controls_widget)

        # Add file controls
        file_controls = QHBoxLayout()
        self.load_button = QPushButton("Load Image")
        self.save_button = QPushButton("Save Image")
        self.load_button.clicked.connect(self.load_image)
        self.save_button.clicked.connect(self.save_image)
        file_controls.addWidget(self.load_button)
        file_controls.addWidget(self.save_button)
        controls_layout.addLayout(file_controls)

        # Add adjustment sliders
        self.create_slider("Brightness", -100, 100, 0, self.adjust_brightness)
        self.create_slider("Contrast", -100, 100, 0, self.adjust_contrast)
        self.create_slider("Saturation", -100, 100, 0, self.adjust_saturation)

        # Add filter buttons
        filters_layout = QVBoxLayout()
        filters = [
            ("Grayscale", self.apply_grayscale),
            ("Blur", self.apply_blur),
            ("Sharpen", self.apply_sharpen),
            ("Edge Detection", self.apply_edge_detection)
        ]

        for filter_name, filter_func in filters:
            button = QPushButton(filter_name)
            button.clicked.connect(filter_func)
            filters_layout.addWidget(button)

        controls_layout.addLayout(filters_layout)

        # Add reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_image)
        controls_layout.addWidget(self.reset_button)

        # Add stretch to push controls to the top
        controls_layout.addStretch()

    def create_slider(self, name, min_val, max_val, default, callback):
        layout = QVBoxLayout()
        label = QLabel(name)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        slider.valueChanged.connect(callback)
        layout.addWidget(label)
        layout.addWidget(slider)
        self.centralWidget().layout().itemAt(1).widget().layout().addLayout(layout)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                 "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            self.original_image = cv2.imread(file_name)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.reset_image()

    def save_image(self):
        if self.current_image is not None:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                     "PNG (*.png);;JPEG (*.jpg *.jpeg)")
            if file_name:
                save_image = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_name, save_image)

    def update_display(self):
        if self.current_image is not None:
            height, width = self.current_image.shape[:2]
            bytes_per_line = 3 * width
            qt_image = QImage(self.current_image.data, width, height,
                            bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.image_label.size(),
                                        Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)

    def reset_image(self):
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.update_display()

    def adjust_brightness(self, value):
        if self.original_image is not None:
            self.current_image = cv2.convertScaleAbs(self.original_image,
                                                   alpha=1, beta=value)
            self.update_display()

    def adjust_contrast(self, value):
        if self.original_image is not None:
            factor = (259 * (value + 255)) / (255 * (259 - value))
            self.current_image = cv2.convertScaleAbs(self.original_image,
                                                   alpha=factor, beta=128*(1-factor))
            self.update_display()

    def adjust_saturation(self, value):
        if self.original_image is not None:
            img_hsv = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2HSV)
            img_hsv[:, :, 1] = cv2.convertScaleAbs(img_hsv[:, :, 1],
                                                  alpha=1 + value/100)
            self.current_image = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)
            self.update_display()

    def apply_grayscale(self):
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2GRAY)
            self.current_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            self.update_display()

    def apply_blur(self):
        if self.current_image is not None:
            self.current_image = cv2.GaussianBlur(self.current_image, (5, 5), 0)
            self.update_display()

    def apply_sharpen(self):
        if self.current_image is not None:
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            self.current_image = cv2.filter2D(self.current_image, -1, kernel)
            self.update_display()

    def apply_edge_detection(self):
        if self.current_image is not None:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            self.current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            self.update_display()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PhotoEditor()
    window.show()
    sys.exit(app.exec())
