import sys
sys.path.append("../")
import pyJaiGo as jai
import os
import random

folder_path = "/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/images" 

camera = jai.JaiGo()
camera.LoadCustomCameraConfiguration = True
camera.AdjustColors = False
camera.GainB = 1.8
camera.GainR = 1.4
camera.GainG = 1.0

camera.CameraConfigurationPath = "RG8.pvxml"
camera.FindAndConnect()
if camera.Connected:
    camera.StartStream()
    if camera.Streaming:
        camera.SaveImage("deviceGains_8bit.tiff")
camera.CloseAndDisconnect()

camera.CameraConfigurationPath = "RG10.pvxml"
camera.FindAndConnect()
if camera.Connected:
    camera.StartStream()
    if camera.Streaming:
        camera.SaveImage("deviceGains_10bit.tiff")
camera.CloseAndDisconnect()
