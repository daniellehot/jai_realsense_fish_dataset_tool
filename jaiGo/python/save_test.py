import pyJaiGo as jai
import numpy as np
import cv2
import time 

pixel_formats = ["BayerRG8", "BayerRG10", "BayerRG10p", "BayerRG12", "BayerRG12p"]
image_formats = [".tiff", ".bmp"]

for pixel_format in pixel_formats:
    camera = jai.JaiGo()
    camera.FindAndConnect()
    if camera.Connected:
        camera.SetPixelFormat(pixel_format)
        camera.StartStream()
        while camera.Streaming:
            if camera.GrabImage():
                print("Saving images")
                path = "images/img_" + pixel_format
                camera.SaveImage(path + ".tiff")
                #camera.SaveImage(path + ".bmp")
                break
    camera.CloseAndDisconnect()
    print("Sleeping for 5 seconds")
    time.sleep(5)


