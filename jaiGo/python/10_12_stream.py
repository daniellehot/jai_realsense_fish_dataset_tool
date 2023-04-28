import sys
sys.path.append("../")
import pyJaiGo as jai
import os
import random

folder_path = "/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/images" 

camera = jai.JaiGo()
camera.LoadCustomCameraConfiguration = True
camera.CameraConfigurationPath = "/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/saveCameraConfiguration/RG12_5Hz_199Kexposure.pvxml"
camera.AdjustColors = True
camera.GainB = 2.4
camera.GainR = 1.2
camera.GainG = 1.0


#camera.CameraConfigurationPath = "/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/saveCameraConfiguration/RG10_5Hz_199Kexposure.pvxml"

camera.FindAndConnect()
if camera.Connected:
    camera.StartStream()
    if camera.Streaming:
        for i in range(10):
            filename = "image_" + str(i) + ".tiff"
            filepath = os.path.join(folder_path, filename)
            camera.SaveImage(filepath)
            camera.GainB = random.uniform(1.0, 5.0)
            camera.GainG = random.uniform(1.0, 5.0)
            camera.GainR = random.uniform(1.0, 5.0)
            
    camera.CloseAndDisconnect()