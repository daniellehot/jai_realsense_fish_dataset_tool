import cv2 as cv 
import numpy as np
import os
import time 


class Heatmap():
    def __init__(self, path):
        self.heatmap_file = os.path.join(path,"heatmap.png")
        self.sum_file = os.path.join(path,"sum.npy")
        self.read_latest()

    def read_latest(self):
        if os.path.exists(self.heatmap_file):
            self.heatmap = cv.imread(os.path.join(self.heatmap_path, self.heatmap_file), cv.IMREAD_UNCHANGED)
            self.img_sum = np.load(os.path.join(self.heatmap_path, self.sum_file))
        else:
            self.heatmap, self.img_sum = None, None

    def update_heatmap(self, image, number_of_files):
        if self.heatmap.shape == image.shape:
            if self.img_sum == None:
                self.img_sum = image
            else:
                self.img_sum += image
                
            img_avg = np.asarray(
                self.img_sum/number_of_files,
                dtype=np.uint8
            )
            self.heatmap = cv.applyColorMap(img_avg, cv.COLORMAP_JET)
            self.save()
        else:
            print("Heatmap and input image have different shapes. Exiting...")
            exit()

    def save(self):
        cv.imwrite(self.heatmap_file, os.path.join(self.heatmap_path, self.heatmap_file))
        np.save(os.path.join(self.heatmap_path, self.sum_file), self.img_sum)


if __name__=="__main__":
    DATA_PATH = "data/jai/rgb"
