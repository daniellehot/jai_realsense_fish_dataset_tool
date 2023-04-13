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
        self.arrow_length = 40
        self.bbox_size_height = 50
        self.bbox_size_width = 75
        self.coords = [
            (300, 200),
            (600, 400),
            (900, 600),
        ]

        self.orientations = [
            (self.coords[0][0], self.coords[0][1]),
            (self.coords[1][0], self.coords[1][1]),
            (self.coords[2][0], self.coords[2][1]), 
        ]

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        
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
        image = np.ones((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS))*255
        for (coord, orientation) in zip(self.coords, self.orientations):
            cv.circle(image, coord, 20, COLOR, 2)
            cv.arrowedLine(image, coord, orientation, COLOR, 3)
            cv.rectangle(
                image,
                self.compute_top_left_corner(coord),
                self.compute_bottom_right_corner(coord),
                COLOR,
                3
            )
        cv.imshow("image", image)


    def compute_top_left_corner(self, center_point):
        top = center_point[1] - self.bbox_size_height
        left = center_point[0] - self.bbox_size_width
        return (left, top)

    def compute_bottom_right_corner(self, center_point):
        bottom = center_point[1] + self.bbox_size_height
        right = center_point[0] + self.bbox_size_width
        return (right, bottom)

    def shuffle(self):
        for i in range(len(self.coords)):
            self.coords[i] = (
                rnd.randint(0, IMG_WIDTH),
                rnd.randint(0, IMG_HEIGHT)
            )
            
            new_orientation = rnd.uniform(0, math.pi)
            self.orientations[i] = (
                int( self.coords[i][0] + self.arrow_length*math.cos(new_orientation) ),
                int( self.coords[i][1] + self.arrow_length*math.sin(new_orientation) )
            )
            

if __name__=="__main__":
    toy = Toy()

    while toy.run:
        toy.show()
        cv.waitKey(1)
