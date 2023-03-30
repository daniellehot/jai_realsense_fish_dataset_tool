import cv2 as cv
import numpy as np
import math

class PointDragger():
    def __init__(self):
        self.img_height = 720
        self.img_width = 1280
        self.window_title = "test"
        self.coordinates = [(300, 200),
                            (600, 400),
                            (900, 600)]
        cv.namedWindow(self.window_title, cv.WINDOW_AUTOSIZE)
        cv.setMouseCallback(self.window_title, self.drag)
        
        self.dragging = False
        self.dragged_point_idx = None

    def show(self):
        self.img = np.ones((self.img_height, self.img_width, 3))*255
        #print("self.coordinates", self.coordinates)
        for coordinate in self.coordinates:
            cv.circle(self.img, coordinate, 10, (0, 255, 0), -1)
        cv.imshow(self.window_title, self.img)
    
    def drag(self, event, x, y, flags, param):
        #print("self.dragging", self.dragging)
        if self.dragging:
            print("Updating the point")
            self.coordinates[self.dragged_point_idx] = (x, y)
            print(self.coordinates[self.dragged_point_idx])

            if event == cv.EVENT_LBUTTONUP:
                print("Stopped updating the point")
                self.dragging = False
                self.dragged_point_idx = None
        else:
            if event == cv.EVENT_LBUTTONDOWN:
                print("Selecting point")
                for coordinate in self.coordinates:
                    dist = math.sqrt(math.pow(x-coordinate[0], 2) + math.pow(y-coordinate[1],2))
                    if dist < 20:
                        self.dragging = True
                        self.dragged_point_idx =self.coordinates.index(coordinate) 

    
    

if __name__=="__main__":
    dragger = PointDragger()

    while True:
        dragger.show()
        cv.waitKey(1)
