import cv2 as cv 
import numpy as np
import os

#TODO Blur and Morphology Kernel - why (21, 21)?
#TODO Heatmap steps - why +40 and -20?
#TODO heatmap_binary - why <150?

class Heatmap():
    def __init__(self, path, image_dimensions):
        #self.heatmap_time_series_path = os.path.join(path, "time_series")
        #self.heatmap_colored_path = os.path.join(path, "heatmap_colored.png")
        #self.heatmap_raw_path = os.path.join(path, "heatmap_raw.png")
        #self.heatmap_overlapped_path = os.path.join(path, "heatmap_overlapped.png")

        self.img_dim = image_dimensions
        self.heatmap_img = np.zeros((self.img_dim[1], self.img_dim[0]), dtype=np.int16) #Correct for numpy's row major matrix representation
        self.heatmap_img_colored = cv.applyColorMap(self.heatmap_img.astype(np.uint8), cv.COLORMAP_JET)
        #self.load()

    """
    def load(self):
        if os.path.exists(self.heatmap_raw_path):
            print("HEATMAP: Data found at", self.heatmap_raw_path)
            self.heatmap_img = cv.imread(self.heatmap_raw_path, cv.IMREAD_UNCHANGED)
            self.heatmap_img_colored = cv.applyColorMap(self.heatmap_img.astype(np.uint8), cv.COLORMAP_JET)
            #IF NOT THE SAME SHAPE, CRY ME A RIVER
        else:
            print("HEATMAP: heatmap_raw.png does not exist. Data not found, initializing empty variable")
            self.heatmap_img = np.zeros((self.img_dim[1], self.img_dim[0]), dtype=np.int16) #Correct for numpy's row major matrix representation
            self.heatmap_img_colored = cv.applyColorMap(self.heatmap_img.astype(np.uint8), cv.COLORMAP_JET)
    """

    def update(self, image):
        #print("HEATMAP: Computing a heatmap")
        
        #General processing
        image_resized = cv.resize(image, self.img_dim)
        image_gray = cv.cvtColor(image_resized, cv.COLOR_BGR2GRAY)

        #Blur the image
        image_blurred = cv.GaussianBlur(image_gray, (21, 21), 0) 
        #cv.imshow("blurred", blurred)
        
        #Threshold image
        heatmap_binary = np.zeros(image_blurred.shape)
        heatmap_binary[image_blurred < 150] = 1
        #cv.imshow("heatmap", heatmap)
        
        #Open and close morphology
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (21, 21))
        heatmap_opened = cv.morphologyEx(heatmap_binary, cv.MORPH_OPEN, kernel)
        heatmap_closed = cv.morphologyEx(heatmap_opened, cv.MORPH_CLOSE, kernel)

        #Compute heatmap
        self.heatmap_img[heatmap_closed == 1] += 40 #hard punish for not moving fish, i.e. if fish are not sufficiently shuffled in 6 consecutive images, we get the highest heat
        self.heatmap_img[heatmap_closed == 0] -= 20 #low reward for moving fish, i.e. fish must be moved to a lot of new positions before the heat settles  
        #Ensure no byte overflow
        self.heatmap_img[self.heatmap_img > 255] = 255 
        self.heatmap_img[self.heatmap_img < 0] = 0
        #Smoothed heatmaps are easier to read
        self.heatmap_img = cv.GaussianBlur(self.heatmap_img, (15, 15), 0) 
        self.heatmap_img_colored = cv.applyColorMap(self.heatmap_img.astype(np.uint8), cv.COLORMAP_JET)
        self.heatmap_img_overlapped = cv.addWeighted(image_resized, 0.5, self.heatmap_img_colored, 0.5, 0.0)

        #cv.waitKey(0)

    def save_all(self, filename):
        #print("HEATMAP: Saving heatmap data")

        if not os.path.exists (self.heatmap_raw_path):
            os.mkdir(self.heatmap_time_series_path)
        cv.imwrite(os.path.join(self.heatmap_time_series_path, filename+"_raw.png"), self.heatmap_img, [cv.IMWRITE_PNG_COMPRESSION, 0])
        cv.imwrite(os.path.join(self.heatmap_time_series_path, filename+"_colored.png"), self.heatmap_img_colored, [cv.IMWRITE_PNG_COMPRESSION, 0])
        cv.imwrite(os.path.join(self.heatmap_time_series_path, filename+"_overlapped.png"), self.heatmap_img_overlapped, [cv.IMWRITE_PNG_COMPRESSION, 0])
        
        #Raw heatmap
        cv.imwrite(self.heatmap_raw_path, self.heatmap_img, [cv.IMWRITE_PNG_COMPRESSION, 0])
        print("HEATMAP: HEATMAP_RAW saved ", self.heatmap_raw_path)
        #Colored heatmap
        cv.imwrite(self.heatmap_colored_path, self.heatmap_img_colored, [cv.IMWRITE_PNG_COMPRESSION, 0])
        print("HEATMAP: HEATMAP_COLORED saved ", self.heatmap_colored_path)
        #Overlapped heatmap
        cv.imwrite(self.heatmap_overlapped_path, self.heatmap_img_overlapped, [cv.IMWRITE_PNG_COMPRESSION, 0])
        print("HEATMAP: HEATMAP_OVERLAPPED saved ", self.heatmap_overlapped_path)

    def save(self, filepath):
        #if not os.path.exists (self.heatmap_raw_path):
        #    os.mkdir(self.heatmap_time_series_path)
        cv.imwrite(filepath, self.heatmap_img_overlapped, [cv.IMWRITE_PNG_COMPRESSION, 0])


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