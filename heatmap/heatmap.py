import cv2 as cv 
import numpy as np
import os

class Heatmap():
    def __init__(self, path):
        self.heatmap_file = os.path.join(path,"heatmap.png")
        self.sum_file = os.path.join(path,"sum.npy")
        self.load()

    def load(self):
        if os.path.exists(self.heatmap_file) and os.path.exists(self.sum_file):
            print("HEATMAP: Data found at", self.heatmap_file, "and", self.sum_file)
            self.heatmap_img = cv.imread(self.heatmap_file, cv.IMREAD_UNCHANGED)
            self.sum_img = np.load(self.sum_file)
        else:
            print("HEATMAP: Data not found, initializing empty variables")
            if not os.path.exists(self.heatmap_file):
                print("HEATMAP: heatmap.png does not exist")
            if not os.path.exists(self.sum_file):
                print("HEATMAP: sum.npy does not exist")
            self.heatmap_img, self.sum_img = None, None

    def update(self, image, number_of_files):
        print("HEATMAP: Updating heatmap")
        if self.heatmap_img is None:
            self.sum_img = np.asarray(image, dtype=np.uint64)
            avg_img = np.asarray(
                self.sum_img,
                dtype=np.uint8
            )
            self.heatmap_img = cv.applyColorMap(avg_img, cv.COLORMAP_JET)
            self.save()
        else:
            if self.heatmap_img.shape == image.shape:
                self.sum_img += np.asarray(image, dtype=np.uint64)
                avg_img = np.asarray(
                    self.sum_img/number_of_files,
                    dtype=np.uint8
                )
                self.heatmap_img = cv.applyColorMap(avg_img, cv.COLORMAP_JET)
                self.save()
            else:
                print("HEATMAP: Heatmap and input image have different shapes. Exiting...")
                exit()

    def save(self):
        print("HEATMAP: Saving heatmap data")
        cv.imwrite(self.heatmap_file, self.heatmap_img)
        np.save(self.sum_file, self.sum_img)


if __name__=="__main__":
    HEATMAP_PATH = "heatmap_data"
    heatmap = Heatmap(HEATMAP_PATH)

    DATA_PATH = "data/jai/rgb"
    images_paths = os.listdir(DATA_PATH)
    
    idx = 1
    for image_path in images_paths:
        print("Iteration", idx)
        img = cv.imread(os.path.join(DATA_PATH, image_path))
        heatmap.update(image=img, number_of_files=idx)
        idx += 1 
        if idx == 11:
            break