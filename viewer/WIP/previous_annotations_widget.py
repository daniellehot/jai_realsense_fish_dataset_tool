import numpy as np
import cv2 as cv
import csv
import os 

def read_previous_annotations():
    #info_img = np.zeros((1200, 1200, 3)).astype(np.uint8)
    csv_to_read = ["00001.csv", "00012.csv", "00034.csv", "00045.csv"]
    annotations = []

    for file in csv_to_read:
        path = os.path.join("/home/vap/jai_realsense_fish_dataset_tool/viewer/group_3/jai/annotations", file)
        if os.path.exists(path):
            with open(path, mode='r') as csv_file:
                for item in csv.DictReader(csv_file, delimiter = ","):
                    annotation = item["id"] + item["side"] + "-" + item["species"]
                    annotations.append(annotation)
            annotations.append("========")
        """
            no_of_annotations = len(list(annnotations))
            img_width = 300
            img_height = no_of_annotations * 50
            img = np.zeros((img_height, img_width)).astype(np.uint8)

            for item in annnotations:
                annotation = item["id"] + item["side"] + "-" + item["species"]
                
                cv.putText(info_img, annotation, (50, 50), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1, cv.LINE_AA, False) 
        #_annotations = list(csv_reader)
        """
    return annotations

def create_annotation_image(annotations):
    if len(annotations) % 2 != 0:
        annotations.pop(-1)
    no_of_annotations = len(annotations) 

    text_positions = []
    for idx, annotation in enumerate(annotations):
        text_width = 50
        text_height = 50 * (idx + 1)
        if text_height > 900:
            text_width = 350
        print("{} {}".format(idx, (text_width, text_height)))
        text_positions.append( (text_width, text_height) ) 
    img_width = 600
    img_height = int(no_of_annotations) * 50
    img = np.zeros((img_height, img_width)).astype(np.uint8)
    print(img.shape)
    for annotation, position in zip(annotations, text_positions):
        cv.putText(img, annotation, position, cv.FONT_HERSHEY_SIMPLEX, 0.75, 255, 1, cv.LINE_AA, False )
    cv.imshow("annotations", img)
    cv.waitKey(0)




annotations = read_previous_annotations()
print(annotations)
create_annotation_image(annotations)