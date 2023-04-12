from scipy import ndimage
import os
import cv2 as cv

DATA_PATH = "data/jai/rgb"
images_paths = os.listdir(DATA_PATH) 

idx = 43
for image_path in images_paths:
    img = cv.imread(os.path.join(DATA_PATH, image_path))
    rotated_img = ndimage.rotate(img, 180)
    filename = str(idx).zfill(5) + ".png"
    print(os.path.join(DATA_PATH, filename))
    cv.imwrite(os.path.join(DATA_PATH, filename), rotated_img, [cv.IMWRITE_PNG_COMPRESSION, 0])
    idx += 1