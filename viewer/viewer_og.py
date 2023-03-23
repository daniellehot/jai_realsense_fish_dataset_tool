import cv2 as cv
import pyzed.sl as sl
import os
import math
from pynput import keyboard
import numpy as np
import tkinter_gui as gui
from tkinter import messagebox
import csv
from datetime import datetime


## PATH CONSTANTS ##
ROOT_PATH = "/media/daniel/4F468D1074109532/autofisk/data/"
ROOT_LOCAL = "/data/"
RGB_PATH = os.path.join(ROOT_PATH, "rgb/")
DEPTH_PATH = os.path.join(ROOT_PATH, "depth/")
CONF_PATH = os.path.join(ROOT_PATH, "confidence/")
#PC_PATH = "data/pointclouds/"
INTRINSICS_PATH = os.path.join(ROOT_PATH, "intrinsics/")
ANNOTATIONS_PATH = os.path.join(ROOT_PATH, "annotations/")
LOGS_PATH = os.path.join(ROOT_PATH, "logs/")

def create_folders():
    if not os.path.exists(ROOT_PATH):
        os.mkdir(ROOT_PATH)
        os.mkdir(RGB_PATH)
        os.mkdir(DEPTH_PATH)
        os.mkdir(CONF_PATH)
        #os.mkdir(PC_PATH)
        os.mkdir(INTRINSICS_PATH)
        os.mkdir(ANNOTATIONS_PATH)
        os.mkdir(LOGS_PATH)

class Viewer():
    def __init__(self):
        self.start_stream()
        self.start_keylistener()
        self.create_session_log()

        self.coordinates = []
        self.species = []
        self.ids = []
        self.sides = []
        self.saved = 0

        self.color = (0, 0, 255) #BGR
        self.mode = "annotating"

    def start_stream(self):
        init_params = sl.InitParameters()
        init_params.depth_mode = sl.DEPTH_MODE.QUALITY  # https://www.stereolabs.com/docs/api/python/classpyzed_1_1sl_1_1DEPTH__MODE.html
        init_params.coordinate_units = sl.UNIT.METER  # Use meter units (for depth measurements)
        init_params.depth_minimum_distance = 0.4
        init_params.depth_maximum_distance = 1.0
        init_params.camera_resolution = sl.RESOLUTION.HD2K
        init_params.enable_image_enhancement = False

        self.zed = sl.Camera()
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print(err)
            exit(-1)
        
        self.set_camera_settings()

        self.runtime_parameters = sl.RuntimeParameters() # Create and set RuntimeParameters after opening the camera
        self.runtime_parameters.sensing_mode = sl.SENSING_MODE.FILL # STANDARD 50 CONFIDENCE THRESHOLD, FILL 100 CONFIDENCE THRESHOLD

        self.image = sl.Mat()
        self.depth = sl.Mat()
        self.confidence = sl.Mat()
        #self.point_cloud = sl.Mat()
        self.calibration_params = None

    def set_camera_settings(self):
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS, 4)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.CONTRAST, 4)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.HUE, 0)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.SATURATION, 4)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.SHARPNESS, 4)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.GAMMA,  5)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.EXPOSURE,  30)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.GAIN, 10)
        self.zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_TEMPERATURE, 3600)
        #self.zed.set_camera_settings(sl.VIDEO_SETTINGS.WHITEBALANCE_AUTO, 1)
    
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
                self.RGB_saved = 0
                self.mode = "annotating"
                self.color = (0, 0, 255)

            if key.char == "q":
                self.zed.close()
                cv.destroyAllWindows()
        except AttributeError:
            print('special key {0} pressed'.format(key))

    def start_keylistener(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        keyboard_listener.start()

    def create_session_log(self):
        self.log_data = None
        filename = self.get_filename(LOGS_PATH) + ".csv"
        self.path_to_session_log = os.path.join(LOGS_PATH, filename)
        
    def retrieve_measures(self):
        # Retrieve left image
        self.zed.retrieve_image(self.image, sl.VIEW.LEFT)
        self.img_cv = (self.image.get_data()) # Return RGB image + extra channel for memory type (I guess?)
        self.zed.retrieve_measure(self.depth, sl.MEASURE.DEPTH)
        self.depth_map = np.array(self.depth.get_data())
        self.zed.retrieve_measure(self.confidence, sl.MEASURE.CONFIDENCE)
        self.confidence_map = np.array(self.confidence.get_data())
        #self.zed.retrieve_measure(self.point_cloud, sl.MEASURE.XYZRGBA)
        self.calibration_params = self.zed.get_camera_information().camera_configuration.calibration_parameters.left_cam
        self.intrinsics = np.array([self.calibration_params.fx, self.calibration_params.fy, self.calibration_params.cx, self.calibration_params.cy], dtype=np.float32)

    def retrieve_only_RGB(self):
        if self.RGB_saved:
            self.zed.retrieve_image(self.image, sl.VIEW.LEFT)
        
    def show(self):
        #window_title = "zed " + self.mode
        self.window_title = "zed"
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
            print("Remove fish and reset by pressing 'r' key.")
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
        filename = self.get_filename(RGB_PATH)
        self.image.write(RGB_PATH + filename + ".png", compression_level = 0)
        print("RGB saved ", RGB_PATH + filename + ".png")
        self.RGB_saved = True

        np.savetxt(DEPTH_PATH + filename + ".csv", self.depth_map, delimiter=",")
        print("DEPTH MAP saved ", DEPTH_PATH + filename + ".csv")
        np.savetxt(CONF_PATH + filename + ".csv", self.confidence_map, delimiter=",")
        print("CONFIDENCE MAP saved ", CONF_PATH + filename + ".csv")
        #self.point_cloud.write(PC_PATH + filename + ".ply", compression_level = 0)
        #print("POINT CLOUD saved", PC_PATH + filename + ".ply")
        np.savetxt(INTRINSICS_PATH + filename + ".csv", self.intrinsics, delimiter=",", header="fx, fy, cx, cy")
        print("INTRINSICS saved ", INTRINSICS_PATH + filename + ".csv")
        self.save_annotations(ANNOTATIONS_PATH + filename + ".csv")
        print("ANNOTATIONS saved ", ANNOTATIONS_PATH + filename + ".csv")

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
        file_to_remove = int(self.get_filename(RGB_PATH)) - 1
        file_to_remove = str(file_to_remove).zfill(5)
        os.remove(os.path.join(RGB_PATH, file_to_remove + ".png"))
        print("Removed ", os.path.join(RGB_PATH, file_to_remove + ".png"))
        os.remove(os.path.join(DEPTH_PATH, file_to_remove + ".csv"))
        print("Removed ", os.path.join(DEPTH_PATH, file_to_remove + ".csv"))
        os.remove(os.path.join(CONF_PATH, file_to_remove + ".csv"))
        print("Removed ", os.path.join(CONF_PATH, file_to_remove + ".csv"))
        #os.remove(os.path.join(PC_PATH, file_to_remove + ".ply"))
        #print("Removed ", os.path.join(PC_PATH, file_to_remove + ".ply"))
        os.remove(os.path.join(INTRINSICS_PATH, file_to_remove + ".csv"))
        print("Removed ", os.path.join(INTRINSICS_PATH, file_to_remove + ".csv"))
        os.remove(os.path.join(ANNOTATIONS_PATH, file_to_remove + ".csv"))
        print("Removed ", os.path.join(ANNOTATIONS_PATH, file_to_remove + ".csv"))

    def get_filename(self, path):
        number_of_files = len(os.listdir(path))
        #print(number_of_files)
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
    while True:
        if viewer.zed.grab(viewer.runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            if not viewer.saved:
                viewer.retrieve_measures()
            else:
                viewer.retrieve_only_RGB()
            viewer.show()
            cv.waitKey(1)
        else:   
            break