import cv2 as cv
import numpy as np
DEPTH_SCALE = 0.0001 #MAKE SURE THIS WORKS 

depth_map = cv.imread("depth_map_test.png", cv.IMREAD_UNCHANGED) #cv.IMREAD_UNCHANGED ensures that the image is read with only 1 channel, otherwise it is 3 channels
print("depth_map[270, 480]", depth_map[240, 480])
print("depth_map[540, 960]", depth_map[540, 960])
print("depth_map[810, 1440]", depth_map[810, 1440])