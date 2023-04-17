import random as rnd
import numpy as np
import math 

class Shuffler():
    def __init__(self, img_dimensions):
        self.bbox_size_height = 50
        self.bbox_size_width = 150
        self.arrow_length = self.bbox_size_width
        self.img_height = img_dimensions[1]
        self.img_width = img_dimensions[0]
        self.img_channels = 3

        self.bboxes = []
        self.orientation_vectors = []


    def generate_random_rotation(self):
        self.rotation = self.rotation = rnd.uniform(-math.pi, math.pi)


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


    def shuffle(self, coords, invalidated = None):
        if invalidated is None:
            for i in range(len(coords)):
                self.coords[i] = (
                    rnd.randint(0, self.img_width),
                    rnd.randint(0, self.img_height)
                )  
        else:
            for idx in invalidated:
                self.coords[idx] = (
                    rnd.randint(0, self.img_width),
                    rnd.randint(0, self.img_height)
                )
                self.rotation = rnd.uniform(-math.pi, math.pi)

        self.orientation_vectors = self.generate_orientation_vectors()
        self.bboxes = self.generate_bounding_boxes()

        self.validate_coordinates()



    def validate_coordinates(self):
        valid = True
        coords_to_fix = []
        for i in range(len(self.bboxes)):
            for corner in self.bboxes[i]:
                if corner[0] < 0 or corner[0] > self.img_width:
                    coords_to_fix.append(i)
                    valid = False
                    break

                if corner[1] < 0 or corner[1] > self.img_height:
                    coords_to_fix.append(i)
                    valid = False
                    break

        if not valid:
            self.shuffle(invalidated = coords_to_fix)


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