import cv2 as cv

import sys
sys.path.append("../")
import pyJaiGo as jai

camera = jai.JaiGo()
camera.LoadCustomCameraConfiguration = True
camera.CameraConfigurationPath = "/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/cameraConfigurations/RG10_Ideal.pvxml"
idx = 0
try:
    camera.FindAndConnect()
    if camera.Connected:
        camera.StartStream()
        while camera.Streaming:
            if camera.GrabImage():
                #cv.imshow("stream", camera.Img)
                if (idx % 10 == 0):
                    camera.SaveImage("temp/image_" + str(idx) + ".tiff")
                idx += 1
                k = cv.waitKey(1)
                if k==27:    # Esc key to stop
                    break
finally:
    camera.CloseAndDisconnect()
