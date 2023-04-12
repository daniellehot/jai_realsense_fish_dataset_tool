import cv2 as cv 
import numpy as np
import os

#TODO Blur and Morphology Kernel - why (21, 21)?
#TODO Heatmap steps - why +40 and -20?

class Heatmap():
    def __init__(self, path, image_dimensions):
        self.heatmap_colored_path = os.path.join(path, "heatmap_colored.png")
        self.heatmap_raw_path = os.path.join(path, "heatmap_raw.png")
        self.heatmap_overlapped_path = os.path.join(path, "heatmap_overlapped.png")
        self.img_dim = image_dimensions
        self.load()

    def load(self):
        if os.path.exists(self.heatmap_raw_path):
            print("HEATMAP: Data found at", self.heatmap_raw_path)
            self.heatmap_img = cv.imread(self.heatmap_raw_path, cv.IMREAD_UNCHANGED)
        else:
            print("HEATMAP: Data not found, initializing empty variables")
            if not os.path.exists(self.heatmap_raw_path):
                print("HEATMAP: heatmap_raw.png does not exist")
            self.heatmap_img = None

    def update(self, image):
        #General processing
        image_resized = cv.resize(image, self.img_dim)
        image_gray = cv.cvtColor(image_resized, cv.COLOR_BGR2GRAY)

        #Blur the image
        blurred = cv.GaussianBlur(image_gray, (21, 21), 0) 
        #cv.imshow("blurred", blurred)
        
        #Threshold image
        heatmap_binary = np.zeros(image_resized.shape)
        heatmap_binary[blurred < 150] = 1
        #cv.imshow("heatmap", heatmap)
        
        #Dilate and erode image
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (21, 21))
        heatmap_opened = cv.morphologyEx(heatmap_binary, cv.MORPH_OPEN, kernel)
        heatmap_closed = cv.morphologyEx(heatmap_opened, cv.MORPH_CLOSE, kernel)

        #Compute heatmap
        if self.heatmap_img is None:
            self.heatmap_img = np.zeros(heatmap_binary.shape)
        self.heatmap_img[heatmap_closed == 1] += 40 #hard punish for not moving fish, i.e. if fish are not sufficiently in 6 consecutive images, we get the highest heat
        self.heatmap_img[heatmap_closed == 0] -= 20 #low reward for moving fish, i.e. fish must be moved to double new positions before the heat settles  
        #Ensure no byte overflow
        self.heatmap_img[self.heatmap_img > 255] = 255 
        self.heatmap_img[self.heatmap_img < 0] = 0
        #Smoothed heatmaps are easier to read
        self.heatmap_img = cv.GaussianBlur(self.heatmap_img, (15, 15), 0) 
        self.heatmap_img_colored = cv.applyColorMap(self.heatmap_img.astype(np.uint8), cv.COLORMAP_JET)
        self.heatmap_img_overlapped = cv.addWeighted(image_resized, 0.5, self.heatmap_img_colored, 0.5, 0.0)

        #cv.waitKey(0)

    def save(self):
        print("HEATMAP: Saving heatmap data")
        #Raw heatmap
        cv.imwrite(self.heatmap_raw_path, self.heatmap_img)
        #Colored heatmap
        cv.imwrite(self.heatmap_colored_path, self.heatmap_img_colored)
        #Overlapped heatmap
        cv.imwrite(self.heatmap_overlapped_path, self.heatmap_img_overlapped)


if __name__=="__main__":
    import shutil
    import random

    HEATMAP_PATH = "heatmap_data"
    if os.path.exists(HEATMAP_PATH):
        shutil.rmtree(HEATMAP_PATH)
        os.mkdir(HEATMAP_PATH)
        os.mkdir(os.path.join(HEATMAP_PATH, "time_data"))

    heatmap = Heatmap(HEATMAP_PATH, (1280, 720))

    DATA_PATH = "data/jai/rgb"
    image_paths = os.listdir(DATA_PATH)
    image_paths = random.choices(image_paths, k=random.randint(10, 40))
    
    idx = 1
    for image_path in image_paths:
        print("Iteration", idx)
        img = cv.imread(os.path.join(DATA_PATH, image_path))
        heatmap.update(image=img)
        cv.imwrite(
            os.path.join(HEATMAP_PATH, "time_data", str(idx)+".png"),
            heatmap.heatmap_img_overlapped
        )
        idx += 1 

    heatmap.save()