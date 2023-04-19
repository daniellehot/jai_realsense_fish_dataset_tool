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
sys.path.append("../viewer/")
import viewer


def get_annotations(_path):
    #annotation_path = _path.replace(".png", ".csv")
    #annotation_path = annotation_path.replace("rgb", "annotations")
    #print("Reading annotation file", annotation_path)
    annotation_path = "/home/vap/jai_realsense_fish_dataset_tool/viewer/data/jai/annotations/00002.csv"
    _annotations = None
    with open(annotation_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter = ",")
        _annotations = list(csv_reader)
    return _annotations


def annotate_image(_img, _annotations):
    print("Annotating image")
    color = (0, 0, 255)
    for annotation in _annotations:
        coordinate = ( int(annotation["width"]), int(annotation["height"]) )
        cv.circle(_img, coordinate, 5, color, -1)
        annotation = annotation["id"] + annotation["side"] + "-" + annotation["species"]
        cv.putText(_img, annotation, (coordinate[0]+5, coordinate[1]+5), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv.LINE_AA, False)
    return _img


if __name__=="__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input", type=str, help="Path to the image")

    args = argParser.parse_args()
    #img = cv.imread(args.input)
    img = cv.imread("00002.png")
    
    annotations = get_annotations(args.input)
    annotate_image(img, annotations)
    cv.imwrite("annotated.png", img)
    print("Image saved")
