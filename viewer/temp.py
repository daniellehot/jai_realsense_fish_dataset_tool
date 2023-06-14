list1 = [(5, 10), (8, 20), (7, 30), (9, 40)]
list2 = [(5, 10), (10, 20), (7, 30), (25, 40)]

if len(set(list1) & set(list2)) != 0:
    print("have not moved all")
    print(set(list1) & set(list2))


import numpy as np
import cv2 as cv

info_img = np.zeros((250, 600, 3)).astype(np.uint8)
#system_info = "{}/{} images mode:{}".format(str(20), str(30), "annotating")
cv.putText(info_img, "Number of images: 20/30", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (25, 40, 155), 1, cv.LINE_AA, False) #(25, 140, 255)
cv.putText(info_img, "Viewer mode: annotating", (50, 100), cv.FONT_HERSHEY_SIMPLEX, 1, (25, 40, 155), 1, cv.LINE_AA, False) #(25, 140, 255)
cv.putText(info_img, "Number of annotations: 15", (50, 150), cv.FONT_HERSHEY_SIMPLEX, 1, (25, 40, 155), 1, cv.LINE_AA, False) #(25, 140, 255)
cv.putText(info_img, "Status: !!!CHANGE FISH!!!", (50, 200), cv.FONT_HERSHEY_SIMPLEX, 1, (25, 40, 155), 1, cv.LINE_AA, False)
#cv.putText(info_img, "Change fish every 11th image [11, 22, 33, 44, 55, 66]", (30, 100 ), cv.FONT_HERSHEY_SIMPLEX, 0.6, (25, 40, 155), 1, cv.LINE_AA, False)
cv.imshow("info", info_img)
cv.waitKey(0)