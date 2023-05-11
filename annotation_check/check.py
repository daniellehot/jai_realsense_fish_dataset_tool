# Standard modules
import cv2 as cv
import csv
import argparse

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
        cv.circle(_img, coordinate, 5, color, -1)
        annotation = annotation["id"] + annotation["side"] + "-" + annotation["species"]
        cv.putText(_img, annotation, (coordinate[0]+5, coordinate[1]+5), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv.LINE_AA, False)
    return _img


if __name__=="__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input", type=str, help="Path to the image")

    args = argParser.parse_args()
    img = cv.imread(args.input)
    annotations = get_annotations(args.input)
    annotate_image(img, annotations)
    cv.imwrite("annotated.png", img)
    print("Image saved")
