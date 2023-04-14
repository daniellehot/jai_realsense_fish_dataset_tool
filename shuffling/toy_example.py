from pynput import keyboard
import cv2 as cv
import random as rnd
import numpy as np
import math 

IMG_HEIGHT = 720
IMG_WIDTH = 1280
IMG_CHANNELS = 3
IMG_DIM = (IMG_WIDTH, IMG_HEIGHT, IMG_CHANNELS)
COLOR = (0, 0, 255)

class Toy():
    def __init__(self):
        self.run = True

        self.cx = IMG_WIDTH/2
        self.cy = IMG_HEIGHT/2
        
        self.arrow_length = 40
        self.bbox_size_height = 50
        self.bbox_size_width = 75
        
        self.coords = [
            (300, 200),
            (600, 400),
            (900, 600),
        ]
        self.rotation = 2.0
        self.bboxes = self.generate_bounding_boxes()
        self.orientation_vectors = self.generate_orientation_vectors()

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()


    def generate_bounding_boxes(self):
        bounding_boxes = []
        for coord in self.coords:
            y_min = coord[1] - self.bbox_size_height
            y_max = coord[1] + self.bbox_size_height
            x_min = coord[0] - self.bbox_size_width
            x_max = coord[0] + self.bbox_size_width

            bbox = [
                self.rotate_point( (x_min, y_min), self.rotation, coord ),
                self.rotate_point( (x_min, y_max), self.rotation, coord ),
                self.rotate_point( (x_max, y_max), self.rotation, coord ),
                self.rotate_point( (x_max, y_min), self.rotation, coord )
                ]
            bounding_boxes.append(bbox)
        return bounding_boxes
    

    def generate_orientation_vectors(self):
        orientation_vectors = []
        for coord in self.coords:
            vector = (
                int( coord[0] + self.arrow_length*math.cos(self.rotation) ),
                int( coord[1] + self.arrow_length*math.sin(self.rotation) )
            )
            orientation_vectors.append(vector)
        return orientation_vectors
        

    def on_press(self, key):
        try:
            print('key {0} pressed'.format(key.char))
            if key.char == "q":
                self.run = False

            if key.char == "r":
                self.shuffle()

        except AttributeError:
            print('special key {0} pressed'.format(key))


    def show(self):
        self.image = np.ones((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS))*255
        self.draw()
        cv.imshow("image", self.image)


    def draw(self):
        print("coords", self.coords)
        print("bboxes", self.bboxes)
        print("orientaion", self.orientation_vectors)
        print("rotation", self.rotation)
        print("===========0")
        for (coord, orientation, bbox) in zip(self.coords, self.orientation_vectors, self.bboxes):
            #Annotation center
            cv.circle(self.image, coord, 20, COLOR, 2)
            #Annotation orientation
            cv.arrowedLine(self.image, coord, orientation, COLOR, 3)
            #Bounding box (must be draw as a set of lines in order to be rotatable)
            cv.line(self.image, bbox[0], bbox[1], COLOR, 3)
            cv.line(self.image, bbox[1], bbox[2], COLOR, 3)
            cv.line(self.image, bbox[2], bbox[3], COLOR, 3)
            cv.line(self.image, bbox[3], bbox[0], COLOR, 3)


    def shuffle(self):
        for i in range(len(self.coords)):
            self.coords[i] = (
                rnd.randint(0, IMG_WIDTH),
                rnd.randint(0, IMG_HEIGHT)
            )
            
            self.rotation = rnd.uniform(-math.pi, math.pi)
            print("********")
            print(self.rotation)
            print(math.cos(self.rotation))
            print(math.sin(self.rotation))
            print("********")

        self.orientation_vectors = self.generate_orientation_vectors()
        self.bboxes = self.generate_bounding_boxes()


    def rotate_point(self, point, rot, rot_point):
        #SOURCE https://www.euclideanspace.com/maths/geometry/affine/aroundPoint/matrix2d/ 

        point = np.asarray([
            point[0], 
            point[1], 
            1
        ]).reshape((3, 1))
        
        rot_point_to_origin = np.eye(3)
        rot_point_to_origin[0,2] = rot_point[0]
        rot_point_to_origin[1,2] = rot_point[1]

        rot_mat = np.array([
            [math.cos(rot), -math.sin(rot), 0],
            [math.sin(rot), math.cos(rot), 0],
            [0, 0, 1]
        ])

        origin_to_rot_point = np.eye(3)
        origin_to_rot_point[0,2] = -rot_point[0]
        origin_to_rot_point[1,2] = -rot_point[1]

        rot_mat_around_point = rot_point_to_origin @ rot_mat @ origin_to_rot_point
        print(rot_mat_around_point)
        rotated_point = (rot_mat_around_point @ point).astype(dtype=np.int32)
        rotated_point = rotated_point.T 
        return (rotated_point[0,0], rotated_point[0,1]) 



if __name__=="__main__":
    toy = Toy()

    while toy.run:
        toy.show()
        cv.waitKey(1)
