# Standard modules
import cv2 as cv
import math
from pynput import keyboard
import csv
from datetime import datetime

import os
HOME_PATH = os.path.expanduser('~')

# Custom modules
import sys

#sys.path.append("/home/daniel/jai_realsense_fish_dataset_tool/realsense")
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/realsense"))
import rs_camera

#sys.path.append("/home/daniel/jai_realsense_fish_dataset_tool/tkinter")
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/tkinter"))
import tkinter_gui as gui

#sys.path.append("/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/")
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/jaiGo"))
import pyJaiGo

sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/heatmap"))
import heatmap
