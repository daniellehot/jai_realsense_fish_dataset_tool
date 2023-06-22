# Standard modules
import cv2 as cv
import csv
import os
import random as rnd
import numpy as np

TIFFS = "/home/vap/jai_realsense_fish_dataset_tool/viewer/data/jai/rgb"
ANNOTATED = "/home/vap/jai_realsense_fish_dataset_tool/viewer/data/jai/annotated"
ANNOTATIONS = "/home/vap/jai_realsense_fish_dataset_tool/viewer/data/jai/annotations"

def fix_path(path, group_str):
    path = path.replace("/jai_realsense_fish_dataset_tool/viewer/", "/{}/".format("groups"))
    path = path.replace("/data/", "/{}/".format(group_str))
    return path


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
    iterations_to_compare = 30
    groups = os.listdir("/home/vap/groups/")

    for iteration in range(iterations_to_compare):
        print("Iteration ", iteration)
        group = rnd.choice(groups)
        tiff_path = fix_path(TIFFS, group)
        annotated_path = fix_path(ANNOTATED, group)
        annotations_path = fix_path(ANNOTATIONS, group)
        print("{}\n{}\n{}".format(tiff_path, annotated_path, annotations_path))

        images = os.listdir(tiff_path)
        rnd_img = rnd.choice(images)
        print(rnd_img)
        img = cv.imread(os.path.join(tiff_path, rnd_img))
        print("tiff img shape", img.shape)
        annotations = get_annotations(os.path.join(tiff_path, rnd_img))
        #print(annotations)
        annotated_image = annotate_image(_img = img, _annotations=annotations)

        gt_image = cv.imread(os.path.join(annotated_path, rnd_img.replace(".tiff", ".png")))
        print("annotated img shape", gt_image.shape)

        combined_images = combine_images(annotated_image, gt_image)
        cv.imwrite(
            os.path.join("data", rnd_img.replace(".tiff", ".png")), 
            combined_images
        )