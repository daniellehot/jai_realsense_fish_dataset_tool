import numpy as np
import cv2 as cv
import math

SIDES = ["R", "L", "R"]
COORDS = [(100, 100), (300, 250), (500, 400)]

def toggle(event, x, y, flags, param):
    global SIDES, COORDS
    if event == cv.EVENT_LBUTTONDOWN:
        print("Toggle")
        for coordinate in COORDS:
                dist = math.sqrt(math.pow(x-coordinate[0], 2) + math.pow(y-coordinate[1],2))
                if dist < 10:
                    idx = COORDS.index(coordinate)
                    print(idx)
                    if SIDES[idx] == "L":  
                        SIDES[idx] = "R"
                    elif SIDES[idx] == "R":  
                        SIDES[idx] = "L"
                    break
        print(SIDES)

if __name__=="__main__":
    color = (255, 205, 155)
    window_name = "stream"
    cv.namedWindow(window_name, cv.WINDOW_AUTOSIZE)

    cv.setMouseCallback(window_name, toggle)
    while True:
        img = np.zeros((500, 750, 3)).astype(np.uint8)
        for (coordinate, side) in zip(COORDS, SIDES):
            cv.putText(img, side, (coordinate[0]+15, coordinate[1]+10), cv.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv.LINE_AA, False)
            cv.circle(img, coordinate, 10, color, 2)

        cv.imshow(window_name, img)
        k = cv.waitKey(1)
        if k == 27: #ESC
            break