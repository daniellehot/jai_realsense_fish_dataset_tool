# Standard modules
import cv2 as cv
import os
import numpy as np
import csv
import argparse

# Custom modules
import sys
sys.path.append("../jaiGo/")
import pyJaiGo as jai
import viewer


def get_the_last_log_entry(_log_path):
    log = os.path.join(_log_path)    
    print("Opening", log)

    log_data = []
    with open(log, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter = ",")
        log_data = list(csv_reader)

    last_log_entry = log_data[-1]["entry"]
    _annotations = []
    for annotation in log_data:
        if annotation["entry"] == last_log_entry:
            _annotations.append(annotation)
    return _annotations


def grab_image():
    camera = jai.JaiGo()
    _received_image = False

    camera.FindAndConnect()
    if camera.Connected:
        camera.StartStream()
        if camera.Streaming:
            if camera.GrabImage():
                _received_image = True
                _img = camera.Img

    camera.CloseAndDisconnect()
    return _received_image, _img


def annotate_image(_img, _annotations):
    color = (0, 0, 255)
    for annotation in _annotations:
        coordinate = ( int(annotation["width"]), int(annotation["height"]) )
        cv.circle(_img, coordinate, 5, color, -1)
        annotation = annotation["id"] + annotation["side"] + "-" + annotation["species"]
        cv.putText(_img, annotation, (coordinate[0]+5, coordinate[1]+5), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv.LINE_AA, False)
    return _img


if __name__=="__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input", type=str, help="Path to the log file")

    args = argParser.parse_args()
    annotations = get_the_last_log_entry(args.input)
    received_image, img = grab_image()
    if received_image:
        annotate_image(img, annotations)
        cv.imwrite("recovered.png", img)
        print("Annotations recovered")
    else:
        print("Could not grab an image")