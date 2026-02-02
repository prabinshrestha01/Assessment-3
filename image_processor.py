import os
print("FILES IN sample_images:", os.listdir("task2_image_processing/sample_images"))

import cv2
import os

class ImageProcessor:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)

    def grayscale(self):
        return cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def blur(self):
        return cv2.GaussianBlur(self.image, (15, 15), 0)

    def edges(self):
        return cv2.Canny(self.image, 100, 200)

    def brighten(self):
        return cv2.convertScaleAbs(self.image, beta=40)

    def contrast(self):
        return cv2.convertScaleAbs(self.image, alpha=1.5)

    def rotate_90(self):
        return cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)

    def flip_horizontal(self):
        return cv2.flip(self.image, 1)

    def resize(self):
        return cv2.resize(self.image, (300, 300))


# -------- SAFE IMAGE PATH --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "sample_images", "test.jpg")

processor = ImageProcessor(r"C:\Users\ACER\Documents\HIT137-Assignment3\task2_image_processing\sample_images\test.jpg")

cv2.imshow("Original", processor.image)
cv2.imshow("Grayscale", processor.grayscale())
cv2.imshow("Blur", processor.blur())
cv2.imshow("Edges", processor.edges())
cv2.imshow("Bright", processor.brighten())
cv2.imshow("Contrast", processor.contrast())
cv2.imshow("Rotate", processor.rotate_90())
cv2.imshow("Flip", processor.flip_horizontal())
cv2.imshow("Resize", processor.resize())

cv2.waitKey(0)
cv2.destroyAllWindows()
