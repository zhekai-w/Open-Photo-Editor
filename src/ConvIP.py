from BaseIP import BaseIP
import enum
import numpy as np
import cv2

class SmType(enum.IntEnum):
    BLUR = 1
    BOX = 2
    GAUSSIAN = 3
    MEDIAN = 4
    BILARETAL = 5

class EdType(enum.IntEnum):
    SOBEL = 1
    CANNY = 2
    SCHARR = 3
    LAPLACE = 4
    ROBERTS = 5
    PREWITT = 6
    KRISCH = 7


class ConvIP(BaseIP):
    def __init__(self) -> None:
        super().__init__()

        self._roberts_kernel = [
            np.array([[1, 0], [0, -1]], dtype=np.float32),
            np.array([[0, 1], [-1, 0]], dtype=np.float32)
        ]

        # Initialize Prewitt kernels
        self._prewitt_kernel = [
            np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32),
            np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
        ]

        # Initialize Kirsch kernels (all 8 directions)
        self._krisch_kernel = [
            np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]], dtype=np.float32),
            np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]], dtype=np.float32),
            np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]], dtype=np.float32),
            np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]], dtype=np.float32),
            np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]], dtype=np.float32),
            np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]], dtype=np.float32),
            np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]], dtype=np.float32),
            np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]], dtype=np.float32)
        ]

    def Smooth2D(self, SrcImg, ksize, SmType):
        if SmType == SmType.BLUR:
            return cv2.blur(SrcImg, (ksize, ksize))
        elif SmType == SmType.BOX:
            return cv2.boxFilter(SrcImg, -1, (ksize, ksize))
        elif SmType == SmType.GAUSSIAN:
            return cv2.GaussianBlur(SrcImg, (ksize, ksize), 0)
        elif SmType == SmType.MEDIAN:
            return cv2.medianBlur(SrcImg, ksize)
        elif SmType == SmType.BILARETAL:
            return cv2.bilateralFilter(SrcImg, ksize, 75, 75)
        else:
            raise ValueError('Invalid smoothing type')

    def EdgeDetect(self, SrcImg, EdType):
        if len(SrcImg.shape) == 3:
            hsv = cv2.cvtColor(SrcImg, cv2.COLOR_BGR2HSV)
            SrcImg = hsv[:,:,2]

        if EdType == EdType.SOBEL:
            sobelx = cv2.Sobel(SrcImg, cv2.CV_32F, 1, 0, ksize=3)
            sobely = cv2.Sobel(SrcImg, cv2.CV_32F, 0, 1, ksize=3)
            # Calculate magnitude
            magnitude = np.sqrt(sobelx**2 + sobely**2)
            # Normalize for display
            sobel = np.uint8(magnitude * 255 / np.max(magnitude))
            return sobel
        elif EdType == EdType.CANNY:
            return cv2.Canny(SrcImg, 100, 200)
        elif EdType == EdType.SCHARR:
            scharrx = cv2.Scharr(SrcImg, cv2.CV_32F, 1, 0)
            scharry = cv2.Scharr(SrcImg, cv2.CV_32F, 0, 1)
            magnitude = cv2.magnitude(scharrx, scharry)
            scharr = np.uint8(magnitude * 255 / np.max(magnitude))
            return scharr
        elif EdType == EdType.LAPLACE:
            # blurred = cv2.GaussianBlur(SrcImg, (3, 3), 0)
            # Apply Laplacian
            laplacian = cv2.Laplacian(SrcImg, cv2.CV_32F)
            # Convert to absolute scale
            laplacian = np.uint8(np.absolute(laplacian))
            return laplacian
        elif EdType == EdType.ROBERTS:
            gx = cv2.filter2D(SrcImg, cv2.CV_32F, self._roberts_kernel[0])
            gy = cv2.filter2D(SrcImg, cv2.CV_32F, self._roberts_kernel[1])
            magnitude = cv2.magnitude(gx, gy)
            roberts = np.uint8(magnitude * 255/ np.max(magnitude))
            return roberts
        elif EdType == EdType.PREWITT:
            gx = cv2.filter2D(SrcImg, cv2.CV_32F, self._prewitt_kernel[0])
            gy = cv2.filter2D(SrcImg, cv2.CV_32F, self._prewitt_kernel[1])
            magnitude = cv2.magnitude(gx, gy)
            presitt = np.uint8(magnitude * 255 / np.max(magnitude))
            return presitt
        elif EdType == EdType.KRISCH:
            max_img = None
            for kernel in self._krisch_kernel:
                grad = cv2.filter2D(SrcImg, cv2.CV_32F, kernel)
                if max_img is None:
                    max_img = grad
                else:
                    max_img = cv2.max(max_img, grad)
            krisch = np.uint8(max_img * 255 / np.max(max_img))
            return krisch
        else:
            raise ValueError('Invalid edge detection type')


def test_smoothing(process, img):
    # Create a new matrix to hold all images
    images = []
    titles = []

    # Apply each smoothing type
    images.append(img)
    titles.append('Original')

    images.append(process.Smooth2D(img, 15, SmType.BLUR))
    titles.append('Blur')

    images.append(process.Smooth2D(img, 15, SmType.BOX))
    titles.append('Box')

    images.append(process.Smooth2D(img, 15, SmType.GAUSSIAN))
    titles.append('Gaussian')

    images.append(process.Smooth2D(img, 15, SmType.MEDIAN))
    titles.append('Median')

    images.append(process.Smooth2D(img, 15, SmType.BILARETAL))
    titles.append('Bilateral')

    # Display all images in subplots
    for i in range(len(images)):
        # images[i] = cv2.resize(images[i], (640, 480))
        plt_rows = 2
        plt_cols = 3
        plt_num = i + 1
        cv2.imshow(titles[i], images[i])

    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test_edge_detect(process, img):
    # Create a new matrix to hold all images
    images = []
    titles = []
    # Apply each edge detection type
    images.append(img)
    titles.append('Original')

    images.append(process.EdgeDetect(img, EdType.SOBEL))
    titles.append('Sobel')

    images.append(process.EdgeDetect(img, EdType.CANNY))
    titles.append('Canny')

    images.append(process.EdgeDetect(img, EdType.SCHARR))
    titles.append('Scharr')

    images.append(process.EdgeDetect(img, EdType.LAPLACE))
    titles.append('Laplacian')

    images.append(process.EdgeDetect(img, EdType.ROBERTS))
    titles.append('Roberts')

    images.append(process.EdgeDetect(img, EdType.PREWITT))
    titles.append('Prewitt')

    images.append(process.EdgeDetect(img, EdType.KRISCH))
    titles.append('Krisch')

    # Display all images
    for i in range(len(images)):
        plt_rows = 3
        plt_cols = 3
        plt_num = i + 1
        cv2.imshow(titles[i], images[i])
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__=="__main__":
    process = ConvIP()
    img = process.ImRead("/home/zack/python-projects/python_opencv/photos/landscape.jpg")
    # test_smoothing(process, img)
    test_edge_detect(process, img)
