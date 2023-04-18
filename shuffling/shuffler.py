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

        self.coordinates = []
        self.bboxes = []
        self.orientation_vectors = []


    def generate_random_rotation(self):
        self.rotation = rnd.uniform(-math.pi, math.pi)


    def generate_bounding_boxes(self):
        bounding_boxes = []
        for coord in self.coordinates:
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
        self.bboxes = bounding_boxes
        #return bounding_boxes
    

    def generate_orientation_vectors(self):
        orientation_vectors = []
        for coord in self.coordinates:
            vector = (
                int( coord[0] + self.arrow_length*math.cos(self.rotation) ),
                int( coord[1] + self.arrow_length*math.sin(self.rotation) )
            )
            orientation_vectors.append(vector)
        self.orientation_vectors = orientation_vectors
        #return orientation_vectors


    def shuffle(self, invalidated = None):
        if invalidated is None:
            self.generate_random_rotation()
            for i in range(len(self.coordinates)):
                self.coordinates[i] = (
                    rnd.randint(0, self.img_width),
                    rnd.randint(0, self.img_height)
                )  
        else:
            for idx in invalidated:
                self.coordinates[idx] = (
                    rnd.randint(0, self.img_width),
                    rnd.randint(0, self.img_height)
                )

        #self.orientation_vectors = self.generate_orientation_vectors()
        #self.bboxes = self.generate_bounding_boxes()
        self.generate_orientation_vectors()
        self.generate_bounding_boxes()
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
            #print("Not valid, reshuffling for", coords_to_fix)
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
    
    def clear(self):
        self.coordinates.clear()
        self.bboxes.clear()
        self.orientation_vectors.clear()


if __name__=="__main__":
    coordinates = [
        (400, 200),
        (800, 400),
        (1200, 600),
        (1600, 800),
    ]
    
    shuffler = Shuffler( img_dimensions=( 1920, 1080 ) )
    shuffler.coordinates = coordinates

    for i in range(10):
        print("Iteration", i)
        shuffler.shuffle()
        print("Shuffler.coordinates", shuffler.coordinates)
        print("Shuffler.bboxes", shuffler.bboxes)
        print("Shuffler.orientation_vectors", shuffler.orientation_vectors)
    print("Done")
