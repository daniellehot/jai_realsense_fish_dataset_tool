# Standard modules
import cv2 as cv
from pynput import keyboard
from datetime import datetime
import numpy as np

import os
HOME_PATH = os.path.expanduser('~')

# Custom modules
import sys

#sys.path.append("/home/daniel/jai_realsense_fish_dataset_tool/realsense")
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/realsense"))
import rs_camera

#sys.path.append("/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/")
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/jaiGo"))
import pyJaiGo

from viewer import create_folders, CALIBRATION_PATH_JAI, CALIBRATION_PATH_RS

class Calibration():
    def __init__(self):
        self.image_number = 0
        self.color = (0, 0, 255)
        self.start_keylistener()

        self.jai_cam = pyJaiGo.JaiGo()
        self.jai_cam.LoadCustomCameraConfiguration = True
        self.jai_cam.CameraConfigurationPath = os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/jaiGo/cameraConfigurations/RG10_Ideal_short.pvxml")
        self.jai_cam.AdjustColors = False
        self.jai_cam.GainB = 2.84
        self.jai_cam.GainG = 1.0
        self.jai_cam.GainR = 1.39
        self.rs_cam = rs_camera.RS_Camera()

    def start_stream(self):
        self.jai_cam.FindAndConnect()
        if self.jai_cam.Connected:
            self.jai_cam.StartStream()
        self.rs_cam.start_stream()

    def stop_stream(self):
        self.jai_cam.StopStream()
        self.rs_cam.stop_stream()

    def on_press(self, key):
        try:
            if key.char == "s":
                self.color = (0, 255, 0)
                self.save()
                self.image_number += 1
                self.color = (0, 0, 255)

            if key.char == "Q":
                self.stop_stream()
                cv.destroyAllWindows()
        except AttributeError:
            pass
            
    def start_keylistener(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        keyboard_listener.start()
    
    def retrieve_measures(self):
        if self.jai_cam.GrabImage():
            self.jai_img = self.jai_cam.Img
        self.rs_img = self.rs_cam.get_color_img()

        #Combine 
        padding = (self.jai_img.shape[0]-self.rs_img.shape[0], self.jai_img.shape[1]-self.rs_img.shape[1])
        padding = (int(padding[0]/2), int(padding[1]/2))
        rs_img_padded = np.pad(self.rs_img, ( (padding[0],padding[0]), (0, 0), (0, 0) ), mode='constant') 
        self.combined_img = np.concatenate((self.jai_img, rs_img_padded), axis=1)
        
    def get_resized_dimensions(self, img_shape, scale_percent):
            width = int(img_shape[1] * scale_percent / 100)
            height = int(img_shape[0] * scale_percent / 100)
            return (width, height)
    
    def show(self):
        self.window_title = 'calibration'
        resized_shape = self.get_resized_dimensions(self.combined_img.shape, 40)
        resized_img = cv.resize(self.combined_img, resized_shape)
        cv.putText(resized_img, str(self.image_number), (resized_img.shape[1]-75, 75), cv.FONT_HERSHEY_SIMPLEX, 1, self.color, 5, cv.LINE_AA, False)
        cv.imshow(self.window_title, resized_img) 
    
    def save(self):
        filename = str(self.image_number).zfill(5) + ".png"
        cv.imwrite(os.path.join(CALIBRATION_PATH_JAI, filename), self.jai_img, [cv.IMWRITE_PNG_COMPRESSION, 0])
        print("C: {} CALIBRATION saved".format(datetime.now(), os.path.join(CALIBRATION_PATH_JAI, filename)))
        cv.imwrite(os.path.join(CALIBRATION_PATH_RS, filename), self.rs_img, [cv.IMWRITE_PNG_COMPRESSION, 0])
        print("C: {} CALIBRATION saved".format(datetime.now(), os.path.join(CALIBRATION_PATH_JAI, filename)))


if __name__=="__main__":
    create_folders()
    calibration = Calibration()

    try:
        calibration.start_stream()
        while calibration.jai_cam.Streaming and calibration.rs_cam.Streaming:
            calibration.retrieve_measures()
            calibration.show()
            cv.waitKey(1)
        calibration.jai_cam.CloseAndDisconnect()
        calibration.rs_cam.close()

    except Exception as e:
        print("C: Error occurred, stopping streams and shutting down")
        print("   Streaming status Jai ", calibration.jai_cam.Streaming)
        print("   Streaming status RealSense ", calibration.rs_cam.Streaming)
        print("C ERROR: ", e)
        if calibration.jai_cam.Streaming:
            calibration.jai_cam.CloseAndDisconnect()
        if calibration.rs_cam.Streaming:
            calibration.rs_cam.close()