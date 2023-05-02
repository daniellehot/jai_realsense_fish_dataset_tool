import pyJaiGo as jai
import numpy as np
import time
import random as rnd

camera = jai.JaiGo()
camera.LoadCustomCameraConfiguration = True
idx = 0

camera.FindAndConnect()
if camera.Connected:
    camera.StartStream()
    while camera.Streaming:
        if camera.GrabImage():
            sleep_time = rnd.randint(30, 60)
            print("Image number", idx, "sleeping_time", sleep_time)
            time.sleep(sleep_time)
            path = "images/img_" + str(idx) + ".tiff"
            result = camera.SaveImage(path)
            print("Saved?", result)
            idx += 1
            if idx == 10:
                break
camera.CloseAndDisconnect()


