# Standard modules
import cv2 as cv
import math
from pynput import keyboard
import csv
from datetime import datetime

import os
HOME_PATH = os.path.expanduser('~')

# Custom modules
import sys

#sys.path.append("/home/daniel/jai_realsense_fish_dataset_tool/realsense")
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/realsense"))
import rs_camera

#sys.path.append("/home/daniel/jai_realsense_fish_dataset_tool/tkinter")
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/tkinter"))
import tkinter_gui as gui

#sys.path.append("/home/daniel/jai_realsense_fish_dataset_tool/jaiGo/")
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/jaiGo"))
import pyJaiGo

sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/heatmap"))
import heatmap

## PATH CONSTANTS ##
ROOT_PATH = "/media/daniel/4F468D1074109532/autofisk/data/"
ROOT_LOCAL = os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/viewer/data/")
ROOT_PATH = ROOT_LOCAL #ONLY USED FOR TESTING

RS_PATH = "rs/"
JAI_PATH = "jai/"
RGB_PATH_RS = os.path.join(ROOT_PATH, RS_PATH, "rgb/")
RGB_PATH_JAI = os.path.join(ROOT_PATH, JAI_PATH, "rgb/")
DEPTH_PATH_RS = os.path.join(ROOT_PATH, RS_PATH, "depth/")
PC_PATH_RS = os.path.join(ROOT_PATH, RS_PATH, "pc/")
ANNOTATIONS_PATH_RS = os.path.join(ROOT_PATH, RS_PATH, "annotations/")
ANNOTATIONS_PATH_JAI = os.path.join(ROOT_PATH, JAI_PATH, "annotations/")
LOGS_PATH = os.path.join(ROOT_PATH, "logs/")
HEATMAPS_PATH = os.path.join(ROOT_PATH, "heatmaps/")

def create_folders():
    if not os.path.exists(ROOT_PATH):
        os.mkdir(ROOT_PATH)
        os.mkdir(os.path.join(ROOT_PATH, RS_PATH))
        os.mkdir(os.path.join(ROOT_PATH, JAI_PATH))
        os.mkdir(RGB_PATH_JAI)
        os.mkdir(RGB_PATH_RS)
        os.mkdir(DEPTH_PATH_RS)
        os.mkdir(PC_PATH_RS)
        os.mkdir(ANNOTATIONS_PATH_JAI)
        os.mkdir(ANNOTATIONS_PATH_RS)
        os.mkdir(LOGS_PATH)
        os.mkdir(HEATMAPS_PATH)


class Viewer():
    def __init__(self):
        self.jai_cam = pyJaiGo.JaiGo()
        self.rs_cam = rs_camera.RS_Camera()

        self.coordinates = []
        self.species = []
        self.ids = []
        self.sides = []
        
        self.saving = False
        
        self.mode_color_dict = {"annotating" : (0, 0, 255),
                                "dragging" : (0, 255, 255), 
                                "correcting" : (255, 0, 0),
                                "saving" : (0, 255, 0)}                                 
        self.mode = "annotating"
        self.color = self.mode_color_dict[self.mode]
        self.dragging = False
        self.dragged_point_idx = None

        self.start_keylistener()
        self.create_session_log()
        self.get_resized_dimension(scale_percent=50)

        self.heatmapper = heatmap.Heatmap(HEATMAPS_PATH, self.resized_dim)
        self.show_heatmap = False

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
            if key.char == "s" and len(self.coordinates) != 0 and not self.saving:
                self.saving = True
                self.color = self.mode_color_dict["saving"]
                self.save_data()
                self.saving = False
                self.color = self.mode_color_dict[self.mode]
                
            if not self.saving:
                if key.char == "m":
                    if self.mode == "annotating":
                        self.mode = "dragging"
                        self.color = self.mode_color_dict[self.mode]

                    elif self.mode == "dragging":
                        self.dragging = False
                        self.mode = "correcting"
                        self.color = self.mode_color_dict[self.mode]

                    elif self.mode == "correcting":
                        self.mode = "annotating"
                        self.color = self.mode_color_dict[self.mode]
                
                if key.char == "h":
                    if self.show_heatmap:
                        self.show_heatmap = False
                    else:
                        self.show_heatmap = True
                
            if key.char == "Z":
                self.remove_last()

            if key.char == "R":
                self.coordinates.clear()
                self.species.clear()
                self.ids.clear()
                self.sides.clear()
                self.mode = "annotating"
                self.color = self.mode_color_dict[self.mode]

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
        self.log_entry = 0
        filename = self.get_filename(LOGS_PATH) + ".csv"
        self.path_to_session_log = os.path.join(LOGS_PATH, filename)
        with open(self.path_to_session_log, 'a') as f: 
            writer = csv.writer(f)
            header = ['species', 'id', 'side', 'width', 'height', 'entry'] 
            writer.writerow(header)
        
    def get_resized_dimension(self, scale_percent):
        width = int(2464 * scale_percent / 100)
        height = int(2056 * scale_percent / 100)
        self.resized_dim = (width, height)

    def retrieve_measures(self):
        if self.jai_cam.GrabImage():
            self.img_cv = self.jai_cam.Img
        
    def show(self):
        self.window_title = "jai"
        self.scaled_img = cv.resize(self.img_cv, self.resized_dim)
        if self.show_heatmap:
            self.scaled_img = cv.addWeighted(self.scaled_img, 0.5, self.heatmapper.heatmap_img_colored, 0.5, 0.0)
        self.draw_annotations()
        cv.namedWindow(self.window_title, cv.WINDOW_AUTOSIZE)
        if self.mode == "annotating": 
                cv.setMouseCallback(self.window_title, self.get)
        elif self.mode == "dragging":
            cv.setMouseCallback(self.window_title, self.drag)
        elif self.mode == "correcting": 
            cv.setMouseCallback(self.window_title, self.remove)

        cv.imshow(self.window_title, self.scaled_img)
        self.update_log()
        
    def draw_annotations(self):
        for (coordinate, species, id, side) in zip(self.coordinates, self.species, self.ids, self.sides):
            cv.circle(self.scaled_img, coordinate, 10, self.color, 2)
            annotation = id + side + "-" + species
            #Text border
            cv.putText(self.scaled_img, annotation, (coordinate[0]+15, coordinate[1]+10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 10, cv.LINE_AA, False)
            #Actual text
            cv.putText(self.scaled_img, annotation, (coordinate[0]+15, coordinate[1]+10), cv.FONT_HERSHEY_SIMPLEX, 1, self.color, 2, cv.LINE_AA, False)

    def get(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            coordinate = (x,y)
            id, species, side = self.get_annotation()
            if species != "cancel" and self.check_for_double_entry(_species = species, _id = id, _side = side):
                self.coordinates.append(coordinate)
                self.species.append(species)
                self.ids.append(id)
                self.sides.append(side)
                self.log_entry += 1

    def drag(self, event, x, y, flags, param):
        if self.dragging:
            self.coordinates[self.dragged_point_idx] = (x, y)

            if event == cv.EVENT_LBUTTONUP:
                #print("Stopped updating the point")
                self.dragging = False
                self.dragged_point_idx = None
        else:
            if event == cv.EVENT_LBUTTONDOWN:
                #print("Selecting point")
                for coordinate in self.coordinates:
                    dist = math.sqrt(math.pow(x-coordinate[0], 2) + math.pow(y-coordinate[1],2))
                    if dist < 10:
                        self.dragging = True
                        self.dragged_point_idx =self.coordinates.index(coordinate) 

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
                    self.log_entry += 1
                    break

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
            
    def check_for_double_entry(self, _species, _id, _side):
        current_annotation = str(_species) + str(_id) + str(_side) 
        for (species, id, side) in zip(self.species, self.ids, self.sides):
            if current_annotation == (str(species) + str(id) + str(side) ):
                print("Double annotation. Check annotation")
                return False
        return True

    def save_data(self):
        print("V: ========= Timestamp ", datetime.now())
        self.rs_cam.get_data()

        filename = self.get_filename(RGB_PATH_JAI)
        self.saved_files = []

        self.heatmapper.update(self.img_cv)
        self.heatmapper.save(filename)

        self.jai_cam.SaveImage(RGB_PATH_JAI + filename + ".tiff")
        self.saved_files.append(RGB_PATH_JAI + filename + ".tiff")
        print("V: RGB saved ", RGB_PATH_JAI + filename + ".tiff")
        
        self.rs_cam.save_image(RGB_PATH_RS + filename + ".png")
        self.saved_files.append(RGB_PATH_RS + filename + ".png")
        print("V: RGB saved ", RGB_PATH_RS + filename + ".png")

        self.rs_cam.save_depth_map(DEPTH_PATH_RS + filename + ".png")
        self.saved_files.append(DEPTH_PATH_RS + filename + ".png")
        print("V: DEPTH saved ", DEPTH_PATH_RS + filename + ".png")

        self.rs_cam.save_intrinsics(DEPTH_PATH_RS + filename + ".json")
        self.saved_files.append(DEPTH_PATH_RS + filename + ".json")
        print("V: INTRINSICS saved ", DEPTH_PATH_RS + filename + ".json")

        self.rs_cam.save_pointcloud(PC_PATH_RS + filename + ".ply")
        self.saved_files.append(PC_PATH_RS + filename + ".ply")
        print("V: POINTCLOUD saved", PC_PATH_RS + filename + ".ply")

        self.save_annotations(ANNOTATIONS_PATH_JAI + filename + ".csv")
        self.saved_files.append(ANNOTATIONS_PATH_JAI + filename + ".csv")
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
    
    def format_annotations(self, log_format = False):
        scale_width = self.img_cv.shape[1]/self.scaled_img.shape[1]
        scale_height = self.img_cv.shape[0]/self.scaled_img.shape[0]
        data_formated = []
        for (species, id, side, xy) in zip(self.species, self.ids, self.sides, self.coordinates):
            if (not log_format):
                data_formated.append([species, id, side, int(xy[0]*scale_width), int(xy[1]*scale_height) ])
            else:
                data_formated.append([species, id, side, int(xy[0]*scale_width), int(xy[1]*scale_height), self.log_entry ])
        return data_formated

    def remove_last(self):
        print("V: ========= Timestamp ", datetime.now())
        for file in self.saved_files:
            os.remove(file)
            print("V: Removed ", file)
        self.saved_files.clear() 

    def get_filename(self, path):
        number_of_files = len(os.listdir(path))
        number_of_files += 1
        number_of_files = str(number_of_files).zfill(5)
        return  number_of_files
    
    def update_log(self):
        data = self.format_annotations(log_format=True)
        if data != self.log_data:
            with open(self.path_to_session_log, 'a') as f: 
                writer = csv.writer(f)
                for annotation in data:
                    writer.writerow(annotation)
        self.log_data = data
       

if __name__=="__main__":
    create_folders()
    viewer = Viewer()
    try:
        viewer.start_stream()
        while viewer.jai_cam.Streaming and viewer.rs_cam.Streaming:
            if not viewer.saving:
                viewer.retrieve_measures()
            viewer.show()
            cv.waitKey(1)
        viewer.jai_cam.CloseAndDisconnect()
        viewer.rs_cam.close()

    except Exception as e:
        print("V: Error occurred, stopping streams and shutting down")
        print("   Streaming status Jai ", viewer.jai_cam.Streaming)
        print("   Streaming status RealSense ", viewer.rs_cam.Streaming)
        print("ERROR: ", e)
        if viewer.jai_cam.Streaming:
            viewer.jai_cam.CloseAndDisconnect()
        if viewer.rs_cam.Streaming:
            viewer.rs_cam.close()