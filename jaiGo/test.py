import pyJaiGo as jai
import numpy as np
import cv2
import time 

camera = jai.JaiGo()

durations = []
camera.FindAndConnect()
if camera.Connected:
    camera.StartStream()
    i = 0
    while camera.Streaming:
        start = time.time()
        i+=1
        
        if camera.GrabImage():
            img = camera.Img
            #print("Iteration ", i, " Image shape is ", np.shape(img))
            resized_img = cv2.resize(img, (1280, 720))
            cv2.imshow("test", resized_img)
            cv2.waitKey(1)
            stop = time.time()
            durations.append(stop-start)
            
        if i == 100:
            camera.Streaming = False
duration_avg = np.average(np.asarray(durations))
print("Average iteration duration", duration_avg)
camera.CloseAndDisconnect()


