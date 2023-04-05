import cv2 as cv 
import numpy as np
import random as rnd

DATA_PATH = "data/jai/rgb"

def create_img(_idx):
    img = np.ones((720,1280,3))*255
    #cv.rectangle(img, (350, 350), (1000, 600), (0, 0, 0), -1)
    #if _idx % 1 == 0:
    #    cv.rectangle(img, (100, 100), (250, 250), (0, 0, 0), -1)
    
    number_of_squares = rnd.randint(2,10)
    for i in range(number_of_squares):
        top, bottom = rnd.randint(360, 720), rnd.randint(360, 720)
        left, right = rnd.randint(0, 1280), rnd.randint(0, 1280)
        if bottom > top:
            bottom, top = top, bottom
        if right > left:
            left, right = right, left
        rand_color = (rnd.randint(0, 255), rnd.randint(0, 255), rnd.randint(0, 255))
        cv.rectangle(img, (left, top), (right, bottom), rand_color, -1)
    return img

if __name__=="__main__":
    images = []
    for i in range(100):
        images.append(create_img(_idx = i))
    img_sum = sum(images)
    img_avg = np.array(img_sum/100, dtype=np.uint8)
    img_heatmap = cv.applyColorMap(img_avg, cv.COLORMAP_JET)
    print(img_heatmap[100, 100])
    cv.imshow("test", img_heatmap)
    cv.waitKey(0)
