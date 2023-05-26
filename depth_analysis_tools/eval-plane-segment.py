import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import cv2

# Based on:
# https://www.kaggle.com/code/yerramvarun/understanding-dice-coefficient
def calc_dice_score(_mask1, _mask2):
    intersection = np.sum(_mask1*_mask2)
    dice = (2 * intersection) / (np.sum(_mask1) + np.sum(_mask2))
    return dice


if __name__ == "__main__":
    seg_path = "../../data_depth_analysis/data/rs/depth/00032.png"
    annotations_path =
