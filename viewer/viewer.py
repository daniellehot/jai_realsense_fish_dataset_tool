# Standard modules
import cv2 as cv
import os
import math
from pynput import keyboard
import numpy as np
from tkinter import messagebox
import csv
from datetime import datetime
import open3d as o3d
import time 

# Custom modules
import sys
sys.path.append("../realsense/")
import rs_camera
sys.path.append("../tkinter/")
import tkinter_gui as gui
sys.path.append("../jaiGo/")
import pyJaiGo

## PATH CONSTANTS ##
ROOT_PATH = "/media/daniel/4F468D1074109532/autofisk/data/"
ROOT_LOCAL = "data/"
ROOT_PATH = ROOT_LOCAL #ONLY USED FOR TESTING
RS_PATH = "rs/"
JAI_PATH = "jai/"
TEST_PATH = ROOT_PATH + "test"
RGB_PATH_RS = os.path.join(ROOT_PATH, RS_PATH, "rgb/")
RGB_PATH_JAI = os.path.join(ROOT_PATH, JAI_PATH, "rgb/")
PC_PATH = os.path.join(ROOT_PATH, RS_PATH, "pc/")
ANNOTATIONS_PATH_RS = os.path.join(ROOT_PATH, RS_PATH, "annotations/")
ANNOTATIONS_PATH_JAI = os.path.join(ROOT_PATH, JAI_PATH, "annotations/")
LOGS_PATH = os.path.join(ROOT_PATH, "logs/")

def create_folders():
    if not os.path.exists(ROOT_PATH):
        os.mkdir(ROOT_PATH)
        os.mkdir(os.path.join(ROOT_PATH, RS_PATH))
        os.mkdir(os.path.join(ROOT_PATH, JAI_PATH))
        os.mkdir(RGB_PATH_JAI)
        os.mkdir(RGB_PATH_RS)
        os.mkdir(PC_PATH)
        os.mkdir(ANNOTATIONS_PATH_JAI)
        os.mkdir(ANNOTATIONS_PATH_RS)
        os.mkdir(LOGS_PATH)

class Viewer():
    def __init__(self):
        self.jai_cam = pyJaiGo.JaiGo()
        self.rs_cam = rs_camera.RS_Camera()

        self.coordinates = []
        self.species = []
        self.ids = []
        self.sides = []
        self.saved = 0
        self.RGB_saved = False

        self.color = (0, 0, 255) #BGR
        self.mode = "annotating"

        #self.start_stream()
        self.start_keylistener()
        self.create_session_log()

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
            #print('alphanumeric key {0} pressed'.format(key.char))
            if key.char == "s" and len(self.coordinates) != 0 and not self.saved:
                self.saved = 1
                self.color = (0, 255, 0)
                self.save_data()
                
            if not self.saved:
                if key.char == "m":
                    if self.mode == "annotating":
                        self.mode = "correcting"
                        self.color = (255, 0, 0)
                    else:
                        self.mode = "annotating"
                        self.color = (0, 0, 255)
                
            if key.char == "z" and self.saved:
                self.remove_last()
                self.saved = 0
                self.color = (0, 0, 255)

            if key.char == "r":
                self.coordinates.clear()
                self.species.clear()
                self.ids.clear()
                self.sides.clear()
                self.saved = 0
                self.RGB_saved = False
                self.mode = "annotating"
                self.color = (0, 0, 255)

            if key.char == "q":
                self.stop_stream()
                cv.destroyAllWindows()
        except AttributeError:
            print('V: special key {0} pressed'.format(key))

    def start_keylistener(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        keyboard_listener.start()

    def create_session_log(self):
        self.log_data = None
        filename = self.get_filename(LOGS_PATH) + ".csv"
        self.path_to_session_log = os.path.join(LOGS_PATH, filename)
        
    def retrieve_measures(self):
        if self.jai_cam.GrabImage():
            self.img_cv = self.jai_cam.Img

    def retrieve_only_RGB(self):
        if self.RGB_saved and self.jai_cam.GrabImage():
            self.img_cv = self.jai_cam.Img
        
    def show(self):
        #window_title = "zed " + self.mode
        self.window_title = "jai"
        self.scaled_img = cv.resize(self.img_cv, (1280, 720))
        self.draw_annotations()
        cv.namedWindow(self.window_title, cv.WINDOW_AUTOSIZE)
        if self.saved:
            cv.setMouseCallback(self.window_title, self.popup)
        else:
            if self.mode == "annotating": 
                cv.setMouseCallback(self.window_title, self.get)
            if self.mode == "correcting":
                cv.setMouseCallback(self.window_title, self.remove)  
        cv.imshow(self.window_title, self.scaled_img)
        self.update_log()
        
    def draw_annotations(self):
        for (coordinate, species, id, side) in zip(self.coordinates, self.species, self.ids, self.sides):
            cv.circle(self.scaled_img, coordinate, 5, self.color, -1)
            annotation = id + side + "-" + species
            cv.putText(self.scaled_img, annotation, (coordinate[0]+5, coordinate[1]+5), cv.FONT_HERSHEY_SIMPLEX, 1, self.color, 2, cv.LINE_AA, False)

    def get(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            coordinate = (x,y)
            id, species, side = self.get_annotation()
            if species != "cancel":
                self.coordinates.append(coordinate)
                self.species.append(species)
                self.ids.append(id)
                self.sides.append(side)

    def remove(self, event, x, y, flags, param):    
        if event == cv.EVENT_LBUTTONDOWN:
            for coordinate in self.coordinates:
                dist = math.sqrt(math.pow(x-coordinate[0], 2) + math.pow(y-coordinate[1],2))
                if dist < 10:
                    idx =self.coordinates.index(coordinate)
                    self.coordinates.pop(idx)
                    self.species.pop(idx)
                    self.ids.pop(idx)
                    self.sides.pop(idx)
                    break
    
    def popup(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            print("V: Remove fish and reset by pressing 'r' key.")
            #messagebox.showerror("Error", "Remove fish and reset by pressing 'r' key.")

    def get_annotation(self):
        self.guiInstance = gui.AnnotationApp()
        while True:
            self.guiInstance.master.update()
            if self.guiInstance.cancelled:
                #print("Annotation cancelled")
                self.guiInstance.master.destroy()
                self.guiInstance = None
                return  str(-1), "cancel", "none"
            if self.guiInstance.id != -1 and self.guiInstance.species != None:
                #print("Annotation acquired")
                id = self.guiInstance.id
                species = self.guiInstance.species
                side = self.guiInstance.side
                self.guiInstance.master.destroy()
                self.guiInstance = None
                return id, species, side

    def save_data(self):
        self.rs_cam.get_data()
        filename = self.get_filename(RGB_PATH_JAI)
        cv.imwrite(RGB_PATH_JAI + filename + ".png", self.jai_cam.Img, [cv.IMWRITE_PNG_COMPRESSION, 0])
        cv.imwrite(RGB_PATH_RS + filename + ".png", self.rs_cam.img, [cv.IMWRITE_PNG_COMPRESSION, 0])
        print("V: RGB saved ", RGB_PATH_JAI + filename + ".png")
        print("V: RGB saved ", RGB_PATH_RS + filename + ".png")
        self.RGB_saved = True

        o3d.io.write_point_cloud(PC_PATH + filename + ".ply", self.rs_cam.pointcloud)  
        print("V: POINTCLOUD saved", PC_PATH + filename + ".ply")

        self.save_annotations(ANNOTATIONS_PATH_JAI + filename + ".csv")
        print("V: ANNOTATIONS saved ", ANNOTATIONS_PATH_JAI + filename + ".csv")

    def save_annotations(self, path):
        data = self.format_annotations()
        #print("annotations formatted")
        with open(path, 'a') as f: 
            writer = csv.writer(f)
            header = ['species', 'id', 'side', 'width', 'height'] 
            writer.writerow(header)
            for annotation in data:
                writer.writerow(annotation)
    
    def format_annotations(self):
        scale_width = self.img_cv.shape[1]/self.scaled_img.shape[1]
        scale_height = self.img_cv.shape[0]/self.scaled_img.shape[0]
        data_formated = []
        for (species, id, side, xy) in zip(self.species, self.ids, self.sides, self.coordinates):
            data_formated.append([species, id, side, int(xy[0]*scale_width), int(xy[1]*scale_height) ])
        return data_formated

    def remove_last(self):
        file_to_remove = int(self.get_filename(RGB_PATH_JAI)) - 1
        file_to_remove = str(file_to_remove).zfill(5)
        os.remove(os.path.join(RGB_PATH_JAI, file_to_remove + ".png"))
        print("V: Removed ", os.path.join(RGB_PATH_JAI, file_to_remove + ".png"))
        os.remove(os.path.join(RGB_PATH_RS, file_to_remove + ".png"))
        print("V: Removed ", os.path.join(RGB_PATH_RS, file_to_remove + ".png"))
        os.remove(os.path.join(PC_PATH, file_to_remove + ".ply"))
        print("V: Removed ", os.path.join(PC_PATH, file_to_remove + ".ply"))
        os.remove(os.path.join(ANNOTATIONS_PATH_JAI, file_to_remove + ".csv"))
        print("V: Removed ", os.path.join(ANNOTATIONS_PATH_JAI, file_to_remove + ".csv"))

    def get_filename(self, path):
        number_of_files = len(os.listdir(path))
        number_of_files += 1
        number_of_files = str(number_of_files).zfill(5)
        return  number_of_files
    
    def update_log(self):
        data = self.format_annotations()
        if data != self.log_data:
            with open(self.path_to_session_log, 'a') as f: 
                writer = csv.writer(f)
                f.write(str(datetime.now()) + "\n")
                header = ['species', 'id', 'side', 'width', 'height'] 
                writer.writerow(header)
                for annotation in data:
                    writer.writerow(annotation)
        self.log_data = data


if __name__=="__main__":
    create_folders()
    viewer = Viewer()
    try:
        viewer.start_stream()
        while viewer.jai_cam.Streaming and viewer.rs_cam.Streaming:
            #print("V: Jai GO FPS: %.2f" % viewer.jai_cam.FrameRate, " Bandwidth: %.2f" % viewer.jai_cam.BandWidth, " Mb/s", end='\r', flush=True)
            if not viewer.saved:
                viewer.retrieve_measures()
            else:
                viewer.retrieve_only_RGB()
            viewer.show()
            cv.waitKey(1)
        viewer.jai_cam.CloseAndDisconnect()
        viewer.rs_cam.close()

    except Exception as e:
        print("V: Error occured, stopping streams and shutting down")
        print("V: One of the cameras is not streaming.")
        print("   Streaming status Jai ", viewer.jai_cam.Streaming)
        print("   Streaming status RealSense ", viewer.rs_cam.Streaming)
        print("V: ", e)
        if viewer.jai_cam.Streaming:
            viewer.jai_cam.CloseAndDisconnect()
        if viewer.rs_cam.Streaming:
            viewer.rs_cam.close()