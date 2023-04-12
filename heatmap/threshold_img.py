import cv2 as cv
import numpy as np

img = cv.imread("data/jai/rgb/00027.png", cv.IMREAD_GRAYSCALE)

(thresh, bw_img) = cv.threshold(img, 10, 150, cv.THRESH_BINARY)
cv.imshow("temp", bw_img)
cv.waitKey(0)