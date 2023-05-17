import cv2 as cv 
import numpy as np
import os

class Heatmap():
    def __init__(self, path, image_dimensions):
        self.threshold = 110
        self.blur_size = (21, 21)
        self.kernel_size = (21, 21)

        self.img_dim = image_dimensions
        self.heatmap_img = np.zeros((self.img_dim[1], self.img_dim[0]), dtype=np.int16) #Correct for numpy's row major matrix representation
        self.heatmap_img_colored = cv.applyColorMap(self.heatmap_img.astype(np.uint8), cv.COLORMAP_JET)


    def adjust_gamma(self, image, gamma):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
        # apply gamma correction using the lookup table
        return cv.LUT(image, table)

    def update(self, image):
  
        #General processing
        image_resized = cv.resize(image, self.img_dim)
        #image_gamma_corrected = self.adjust_gamma(image_resized, gamma=0.9)
        image_gray = cv.cvtColor(image_resized, cv.COLOR_BGR2GRAY)

        #Blur the image
        image_blurred = cv.GaussianBlur(image_gray, self.blur_size, 0) 

        #Threshold image
        heatmap_binary = np.zeros(image_blurred.shape)
        heatmap_binary[image_gray < self.threshold] = 1
        #cv.imshow("heatmap", heatmap)
        
        #Open and close morphology
        kernel = cv.getStructuringElement(cv.MORPH_RECT, self.kernel_size)
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


def get_resized_dimension(scale_percent):
    width = int(2464 * scale_percent / 100)
    height = int(2056 * scale_percent / 100)
    return (width, height)


if __name__=="__main__":
    import shutil
    import random

    HEATMAP_PATH = "heatmap_data"
    if os.path.exists(HEATMAP_PATH):
        shutil.rmtree(HEATMAP_PATH)
        os.mkdir(HEATMAP_PATH)
        #os.mkdir(os.path.join(HEATMAP_PATH, "time_data"))

    DATA_PATH = "data/jai_tiff"
    image_paths = os.listdir(DATA_PATH)
    #image_paths = random.choices(image_paths, k=random.randint(10, 40))
    
    idx = 1
    thresholds = list(range(100, 150, 5))

    for threshold in thresholds:
        print("=============")
        print("Threshold", threshold)
        heatmap = Heatmap(HEATMAP_PATH, get_resized_dimension(50))
        heatmap.threshold = threshold
        os.mkdir( os.path.join(HEATMAP_PATH, "time_data_" + str(threshold)) )
        
        for image_path in image_paths:
            print("Iteration", idx)
            img = cv.imread(os.path.join(DATA_PATH, image_path))
            heatmap.update(image=img)
            cv.imwrite(
                os.path.join(HEATMAP_PATH, "time_data_" + str(threshold), str(idx)+".png"),
                heatmap.heatmap_img_overlapped
            )
            idx += 1 

    #heatmap.save()