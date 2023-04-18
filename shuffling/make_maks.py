import cv2 as cv
import numpy as np

img = cv.imread("fish.png")
cv.imshow("img", img)
img_binary = np.zeros(img.shape)
img [img < 255] = 0
img [img == 255] = 1 
#print(img_binary.shape)
#cv.imshow("test", img_binary)
cv.waitKey(0)