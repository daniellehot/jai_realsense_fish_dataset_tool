import sys
sys.path.append("../")
import pyJaiGo as jai

import os
if os.path.exists("test.tiff"):
    print("Removing previous image tiff")
    os.remove("test.tiff")

camera = jai.JaiGo()
camera.LoadCustomCameraConfiguration = False
camera.CameraConfigurationPath = "/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/saveCameraConfiguration/RG10_5Hz_199Kexposure_notColorAdjusted.pvxml"
#camera.CameraConfigurationPath = "/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/saveCameraConfiguration/RG10_5Hz_199Kexposure.pvxml"

camera.FindAndConnect()
if camera.Connected:
    camera.StartStream()
    if camera.Streaming:
        camera.SaveImage("test.tiff")
    camera.CloseAndDisconnect()