from argparse import ArgumentParser
import os 
import csv
import cv2 as cv
import logging

def createArgumentParser():
    parser = ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="full path to the folder with groups")
    parser.add_argument("-g", "--group", type=int, help="specify group number you want to correct, must be an intenger")
    parser.add_argument("-f", "--files", type=str, help="insert file numbers, without zeros and separated by a comma,  you want to correct")
    parser.add_argument("-q", "--querry_annotation", type=str, help="annotation to fix, format is ID-SIDE-SPECIES")
    parser.add_argument("-n", "--new_annotation", type=str, help="new annotation, format is ID-SIDE-SPECIES")
    return parser

def format_args(args):
    group = "group_{}".format(args.group)
    files = args.files.split(",")
    files = [file.zfill(5) for file in files]
    querry_annotation = args.querry_annotation.split("-")
    querry_annotation = querry_annotation[0] + querry_annotation[1] + "-" + querry_annotation[2]
    return args.path, group, files, querry_annotation, args.new_annotation.split("-")

if __name__=="__main__":
    logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

    args = createArgumentParser().parse_args()
    path, group, files, querry_annotation, new_annotation = format_args(args)

    #print(path)
    #print(group)
    #print(files)
    print(querry_annotation)
    print(new_annotation)
    print("====")

    for file in files:
        print(file)
        tiff_image_path = os.path.join(path, group, "jai", "rgb", file+".tiff")
        annotated_image_path = os.path.join(path, group, "jai", "annotated", file+".png")
        annotations_path = os.path.join(path, group, "jai", "annotations", file+".csv")
        #print(tiff_image_path)
        #print(annotated_image_path)
        #print(annotations_path)
        tiff_img = cv.imread(tiff_image_path)
        annotated_img = cv.imread(annotated_image_path)        
        with open(annotations_path, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter = ",")
            annotations = list(csv_reader)

            for annotation in annotations:
                saved_annotation = annotation["id"] + annotation["side"] + "-" + annotation["species"]
                if saved_annotation == querry_annotation:
                    log_str = " {}, {}, {}".format(annotations_path, saved_annotation, new_annotation)
                    logging.info(log_str)
                    print(saved_annotation)
                    print(querry_annotation) 

        #print(tiff_img.shape)
        #print(annotated_img.shape)