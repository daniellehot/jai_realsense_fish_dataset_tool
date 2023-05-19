# Standard modules
import cv2 as cv
import csv
import os
import random as rnd
import numpy as np


def get_annotations(_path):
    annotation_path = None
    if ".png" in _path:
        annotation_path = _path.replace(".png", ".csv")
    if ".tiff" in _path:
        annotation_path = _path.replace(".tiff", ".csv")    
    annotation_path = annotation_path.replace("rgb", "annotations")
    print("Reading annotation file", annotation_path)
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
        cv.circle(_img, coordinate, 10, color, 2)
        annotation = annotation["id"] + annotation["side"] + "-" + annotation["species"]
        #Text border
        cv.putText(_img, annotation, (coordinate[0]+15, coordinate[1]+10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 10, cv.LINE_AA, False)
        #Actual text
        cv.putText(_img, annotation, (coordinate[0]+15, coordinate[1]+10), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv.LINE_AA, False)
        #cv.putText(_img, annotation, (coordinate[0]+15, coordinate[1]+5), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv.LINE_AA, False)
    return _img

def combine_images(tiff, png):
    """
    # PADDING 
    height_delta = tiff.shape[0] - png.shape[0]
    width_delta = tiff.shape[1] - png.shape[1]
    padded_png = cv.copyMakeBorder(png, 
                                   int(height_delta/2), 
                                   int(height_delta/2),
                                   int(width_delta/2),
                                   int(width_delta/2),
                                   cv.BORDER_CONSTANT,
                                   value=(0, 0, 0)
                                   )
    cv.imshow("padded_png", padded_png)
    cv.waitKey(0)
    """
    resized_tiff = cv.resize(tiff, (png.shape[1], png.shape[0]))
    stacked_img = np.hstack((resized_tiff, png))
    return stacked_img
    #cv.imshow("stacked", stacked_img)
    #cv.waitKey(0)
    #exit(5)



if __name__=="__main__":
    TIFFS = "/home/vap/jai_realsense_fish_dataset_tool/viewer/data/jai/rgb"
    GT = "/home/vap/jai_realsense_fish_dataset_tool/viewer/data/jai/annotated"
    ANNOTATIONS = "/home/vap/jai_realsense_fish_dataset_tool/viewer/data/jai/annotations"
    IMAGES_TO_COMPARE = 10

    images = os.listdir(TIFFS)
    for i in range(IMAGES_TO_COMPARE):
        rnd_img = rnd.choice(images)
        img = cv.imread(os.path.join(TIFFS, rnd_img))
        #print(img)
        annotations = get_annotations(os.path.join(TIFFS, rnd_img))
        #print(annotations)
        annotated_image = annotate_image(_img = img, _annotations=annotations)
        print(annotated_image.shape)
        gt_image = cv.imread(os.path.join(GT, rnd_img.replace(".tiff", ".png")))
        print(gt_image.shape)
        combined_images = combine_images(annotated_image, gt_image)
        cv.imwrite(
            os.path.join("data", rnd_img.replace(".tiff", ".png")), 
            combined_images
            )
    

    
    exit(4)
    img = cv.imread(args.input)
    annotations = get_annotations(args.input)
    annotate_image(img, annotations)
    cv.imwrite("annotated.png", img)
    print("Image saved")
