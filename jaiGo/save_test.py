import pyJaiGo as jai
import numpy as np
import cv2
import time 

camera = jai.JaiGo()
camera.FindAndConnect()
if camera.Connected:
    camera.StartStream()

for i in range(1):
    to_save = ["images/img_" + str(i) + ".bmp",
               "images/img_" + str(i) + ".raw",
               "images/img_" + str(i) + ".tiff"]
    if camera.GrabImage():
       camera.SaveImage(to_save[0])
       camera.SaveImage(to_save[1])
       camera.SaveImage(to_save[2])
camera.CloseAndDisconnect()


