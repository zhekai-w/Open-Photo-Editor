from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QFileDialog,
                            QComboBox, QGroupBox, QSlider, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import sys
import cv2
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from HistIP import HistIP, ColorType

class HistogramApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hist_ip = HistIP()
        self.src_image = None
        self.ref_image = None
        self.result_image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Histogram Processing')
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create controls group
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout()

        # Equalization controls
        equalize_btn = QPushButton("Load Image for Equalization")
        equalize_btn.clicked.connect(self.load_equalize_image)
        apply_equalize_btn = QPushButton("Apply Equalization")
        apply_equalize_btn.clicked.connect(self.apply_equalization)

        # Save result image
        save_result_btn = QPushButton("Save Result Image")
        save_result_btn.clicked.connect(self.save_result_image)

        # Matching controls
        load_src_btn = QPushButton("Load Source Image")
        load_src_btn.clicked.connect(self.load_src_image)
        load_ref_btn = QPushButton("Load Reference Image")
        load_ref_btn.clicked.connect(self.load_ref_image)

        self.match_type_combo = QComboBox()
        self.match_type_combo.addItems(["RGB", "HSV", "YUV"])

        apply_match_btn = QPushButton("Apply Matching")
        apply_match_btn.clicked.connect(self.apply_matching)

        # Add matching intensity
        self.match_intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.match_intensity_slider.setMinimum(0)
        self.match_intensity_slider.setMaximum(100)
        self.match_intensity_slider.setValue(100)  # Default to 100%
        self.match_intensity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.match_intensity_slider.setTickInterval(10)

        # Add a label for the slider
        self.intensity_label = QLabel("Matching Intensity: 100%")
        self.match_intensity_slider.valueChanged.connect(self.update_intensity_label)

        # Add to controls_layout
        controls_layout.addWidget(self.intensity_label)
        controls_layout.addWidget(self.match_intensity_slider)

        # Add controls to layout
        controls_layout.addWidget(equalize_btn)
        controls_layout.addWidget(apply_equalize_btn)
        controls_layout.addWidget(load_src_btn)
        controls_layout.addWidget(load_ref_btn)
        controls_layout.addWidget(self.match_type_combo)
        controls_layout.addWidget(apply_match_btn)
        controls_group.setLayout(controls_layout)
        controls_layout.addWidget(save_result_btn)

        # Create image display area
        display_layout = QHBoxLayout()

        # Source image and histogram
        src_group = QGroupBox("Source Image")
        src_layout = QVBoxLayout()
        self.src_label = QLabel()
        self.src_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.src_hist_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        src_layout.addWidget(self.src_label)
        src_layout.addWidget(self.src_hist_canvas)
        src_group.setLayout(src_layout)

        # Reference image and histogram
        ref_group = QGroupBox("Reference Image")
        ref_layout = QVBoxLayout()
        self.ref_label = QLabel()
        self.ref_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ref_hist_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        ref_layout.addWidget(self.ref_label)
        ref_layout.addWidget(self.ref_hist_canvas)
        ref_group.setLayout(ref_layout)

        # Result image and histogram
        result_group = QGroupBox("Result Image")
        result_layout = QVBoxLayout()
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_hist_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.result_hist_canvas)
        result_group.setLayout(result_layout)

        display_layout.addWidget(src_group)
        display_layout.addWidget(ref_group)
        display_layout.addWidget(result_group)

        # Add all layouts to main layout
        main_layout.addWidget(controls_group)
        main_layout.addLayout(display_layout)

    def save_result_image(self):
        if self.result_image is not None:
            fname, _ = QFileDialog.getSaveFileName(self, 'Save Result Image', '',
                "Image files (*.jpg *.jpeg *.png *.bmp)")
            if fname:
                cv2.imwrite(fname, self.result_image)
                QMessageBox.information(self, "Success", "Image saved successfully!")
        else:
            QMessageBox.warning(self, "Warning", "No result image to save!")

    def load_equalize_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '',
            "Image files (*.jpg *.jpeg *.png *.bmp)")
        if fname:
            self.src_image = self.hist_ip.ImRead(fname)
            self.update_image_display(self.src_image, self.src_label, self.src_hist_canvas)

    def load_src_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '',
            "Image files (*.jpg *.jpeg *.png *.bmp)")
        if fname:
            self.src_image = self.hist_ip.ImRead(fname)
            self.update_image_display(self.src_image, self.src_label, self.src_hist_canvas, self.match_type_combo.currentText())

    def load_ref_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '',
            "Image files (*.jpg *.jpeg *.png *.bmp)")
        if fname:
            self.ref_image = self.hist_ip.ImRead(fname)
            self.update_image_display(self.ref_image, self.ref_label, self.ref_hist_canvas, self.match_type_combo.currentText())

    def apply_equalization(self):
        if self.src_image is not None:
            if len(self.src_image.shape) == 2:  # Grayscale
                self.result_image = self.hist_ip.MonoEqualize_gray(self.src_image)
                print("fuck !")
            else:  # Color
                self.result_image = self.hist_ip.MonoEqualize_rgb(self.src_image)
                print("fucked !")
                self.update_image_display(self.result_image, self.result_label, self.result_hist_canvas, self.match_type_combo.currentText())
                self.update_image_display(self.src_image, self.src_label, self.src_hist_canvas, self.match_type_combo.currentText())
                self.update_image_display(self.ref_image, self.ref_label, self.ref_hist_canvas, self.match_type_combo.currentText())

    def apply_matching(self):
        if self.src_image is not None and self.ref_image is not None:
            match_type = self.match_type_combo.currentText()
            intensity = self.match_intensity_slider.value() / 100.0  # Convert to 0-1 range
            if match_type == "RGB":
                color_type = ColorType.USE_RGB
            elif match_type == "HSV":
                color_type = ColorType.USE_HSV
            elif match_type == "YUV":
                color_type = ColorType.USE_YUV
            else:  # Grayscale
                self.src_image = cv2.cvtColor(self.src_image, cv2.COLOR_BGR2GRAY)
                self.ref_image = cv2.cvtColor(self.ref_image, cv2.COLOR_BGR2GRAY)

            self.result_image = self.hist_ip.HistMatching(self.src_image, self.ref_image, CType=color_type, intensity=intensity)
            self.update_image_display(self.result_image, self.result_label, self.result_hist_canvas, match_type)
            self.update_image_display(self.src_image, self.src_label, self.src_hist_canvas, self.match_type_combo.currentText())
            self.update_image_display(self.ref_image, self.ref_label, self.ref_hist_canvas, self.match_type_combo.currentText())



    def update_intensity_label(self, value):
        self.intensity_label.setText(f"Matching Intensity: {value}%")


    def update_image_display(self, image, label, hist_canvas, color_space=None):
        if image is None:
            label.clear()
            hist_canvas.figure.clear()
            hist_canvas.draw()
            return

        # Update image display
        height, width = image.shape[:2]
        scale = min(300/height, 400/width)
        new_height, new_width = int(height*scale), int(width*scale)

        if len(image.shape) == 2:  # Grayscale
            q_img = QImage(image.data, width, height, width, QImage.Format.Format_Grayscale8)
        else:  # Color
            q_img = QImage(image.data, width, height, 3*width, QImage.Format.Format_RGB888).rgbSwapped()

        pixmap = QPixmap.fromImage(q_img)
        label.setPixmap(pixmap.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio))

        # Update histogram display based on color space
        hist_canvas.figure.clear()
        ax = hist_canvas.figure.add_subplot(111)

        if len(image.shape) == 2:  # Grayscale
            hist = self.hist_ip.CalcGrayHist(image)
            ax.plot(hist, color='k', label='Gray')
            ax.set_title('Grayscale Histogram')
        else:  # Color
            if color_space == "HSV":
                hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv_img)
                h_hist = cv2.calcHist([h], [0], None, [180], [0, 180])  # Hue has range 0-180
                s_hist = cv2.calcHist([s], [0], None, [256], [0, 256])
                v_hist = cv2.calcHist([v], [0], None, [256], [0, 256])

                # Normalize by dividing by total pixels to get percentage
                total_pixels = h.shape[0] * h.shape[1]
                h_hist = (h_hist / total_pixels) * 100
                s_hist = (s_hist / total_pixels) * 100
                v_hist = (v_hist / total_pixels) * 100

                ax.plot(h_hist, color='r', label='Hue')
                ax.plot(s_hist, color='g', label='Saturation')
                ax.plot(v_hist, color='b', label='Value')
                ax.set_title('HSV Histogram')
                ax.legend(loc='upper left')
            elif color_space == "YUV":
                yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
                y, u, v = cv2.split(yuv_img)
                y_hist = cv2.calcHist([y], [0], None, [256], [0, 256])
                u_hist = cv2.calcHist([u], [0], None, [256], [0, 256])
                v_hist = cv2.calcHist([v], [0], None, [256], [0, 256])

                # Normalize by dividing by total pixels to get percentage
                total_pixels = y.shape[0] * y.shape[1]
                y_hist = (y_hist / total_pixels) * 100
                u_hist = (u_hist / total_pixels) * 100
                v_hist = (v_hist / total_pixels) * 100

                ax.plot(y_hist, color='k', label='Y (Luminance)')
                ax.plot(u_hist, color='b', label='U (Chrominance)')
                ax.plot(v_hist, color='r', label='V (Chrominance)')
                ax.set_title('YUV Histogram')
                ax.legend(loc='upper left')

            else:  # Default RGB
                b_hist, g_hist, r_hist = self.hist_ip.CalcColorHist(image)
                b, g, r = cv2.split(image)
                # Normalize by dividing by total pixels to get percentage
                total_pixels = b.shape[0] * b.shape[1]
                b_hist = (b_hist / total_pixels) * 100
                g_hist = (g_hist / total_pixels) * 100
                r_hist = (r_hist / total_pixels) * 100

                ax.plot(b_hist, color='b', label='Blue')
                ax.plot(g_hist, color='g', label='Green')
                ax.plot(r_hist, color='r', label='Red')
                ax.set_title('RGB Histogram')
                ax.legend(loc='upper left')

        ax.legend()
        ax.set_xlabel('Pixel Value')
        ax.set_ylabel('Percentage of Pixels (%)')
        hist_canvas.draw()

def main():
    app = QApplication(sys.argv)
    ex = HistogramApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
