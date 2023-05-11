import cv2 as cv
import numpy as np
import argparse

DEPTH_SCALE = 0.0001 #MAKE SURE THIS WORKS 

#depth_map = cv.imread("depth_map_test.png", cv.IMREAD_UNCHANGED) #cv.IMREAD_UNCHANGED ensures that the image is read with only 1 channel, otherwise it is 3 channels
#print("depth_map[270, 480]", depth_map[240, 480])
#print("depth_map[540, 960]", depth_map[540, 960])
#print("depth_map[810, 1440]", depth_map[810, 1440])

if __name__=="__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input", type=str, help="Path to the image")

    args = argParser.parse_args()
    img_16bit = cv.imread(args.input, cv.IMREAD_UNCHANGED)
    scale_factor = 255/np.amax(img_16bit)
    img_8bit = (img_16bit*scale_factor).astype(np.uint8)
    img_colorized = cv.applyColorMap(img_8bit, cv.COLORMAP_JET)
    cv.imshow("depth map", img_colorized)
    cv.waitKey(0)