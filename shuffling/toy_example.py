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
        
        
        self.bbox_size_height = 50
        self.bbox_size_width = 150
        self.arrow_length = self.bbox_size_width

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
        cv.waitKey(1)
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


    def shuffle(self, invalidated = None):
        if invalidated is None:
            for i in range(len(self.coords)):
                self.coords[i] = (
                    rnd.randint(0, IMG_WIDTH),
                    rnd.randint(0, IMG_HEIGHT)
                )
                
                self.rotation = rnd.uniform(-math.pi, math.pi)

        else:
            for idx in invalidated:
                self.coords[idx] = (
                    rnd.randint(0, IMG_WIDTH),
                    rnd.randint(0, IMG_HEIGHT)
                )
                self.rotation = rnd.uniform(-math.pi, math.pi)

        self.orientation_vectors = self.generate_orientation_vectors()
        self.bboxes = self.generate_bounding_boxes()

        self.validate_coordinates()
        #print("Valid:", valid, idx)



    def validate_coordinates(self):
        valid = True
        coords_to_fix = []
        for i in range(len(self.bboxes)):
            for corner in self.bboxes[i]:
                if corner[0] < 0 or corner[0] > IMG_WIDTH:
                    coords_to_fix.append(i)
                    valid = False
                    break

                if corner[1] < 0 or corner[1] > IMG_HEIGHT:
                    coords_to_fix.append(i)
                    valid = False
                    break
                
        for i in range( len(self.bboxes) ):
            for j in range( i, len(self.bboxes) ):
                if self.bboxes[i] == self.bboxes[j]:
                    continue
                elif i or j in coords_to_fix:
                    continue
                else:
                    continue
                    #TODO Computing intersection of non-axis aligned bounding boxes is fairly difficult (see computing polygon intersections) 

        
        print("Valid", valid)
        if not valid:
            self.shuffle(invalidated = coords_to_fix)
        #return valid, coords_to_fix


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

        rotated_point = (rot_mat_around_point @ point).astype(dtype=np.int32)
        rotated_point = rotated_point.T 
        return (rotated_point[0,0], rotated_point[0,1]) 
    

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


if __name__=="__main__":
    toy = Toy()

    while toy.run:
        toy.show()
        