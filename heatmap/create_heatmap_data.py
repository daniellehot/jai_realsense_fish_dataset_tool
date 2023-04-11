import cv2 as cv 
import numpy as np
import random as rnd
import os

DATA_PATH = "data/jai/rgb"

if __name__=="__main__":
  
    images_paths = os.listdir(DATA_PATH)
    print(images_paths)
    print("len(images_paths)", len(images_paths))
    images = []
    
    for image in images_paths:
        img = cv.imread(os.path.join(DATA_PATH, image))
        img = np.asanyarray(img, dtype=np.uint64)
        images.append(img)
        #scale_percent = 30 # percent of original size
        #width = int(img.shape[1] * scale_percent / 100)
        #height = int(img.shape[0] * scale_percent / 100)
        #dim = (width, height)
        #img_resized = cv.resize(img, dim)
        #temp_sum += img_resized[100, 200]
        #images.append(img_resized)
    
    """
    for i in range(100):
        img = cv.imread(os.path.join(DATA_PATH, images_paths[5]))
        scale_percent = 30 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        img_resized = cv.resize(img, dim)
        images.append(img_resized)
    """    
    #sanity check
    #cv.imshow("sanity_check", images[5])
    #cv.waitKey(0)
    img_sum = np.asarray(sum(images), dtype = np.uint64)
    print("img_sum[100, 200, 0]", img_sum[100, 200])
    print("temp_sum", temp_sum)
    #print("img_sum shape", np.shape(img_sum))
    #print("img_sum shape", img_sum)
    img_avg = np.array(img_sum/len(images_paths), dtype=np.uint8)
    img_heatmap = cv.applyColorMap(img_avg, cv.COLORMAP_JET)
    cv.imshow("test", img_heatmap)
    cv.waitKey(0)
