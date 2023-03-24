import os

## PATH CONSTANTS ##
ROOT_PATH = "/media/daniel/4F468D1074109532/autofisk/data/"
ROOT_LOCAL = "data/"
ROOT_PATH = ROOT_LOCAL #ONLY USED FOR TESTING
RS_PATH = "rs/"
JAI_PATH = "jai/"
TEST_PATH = ROOT_PATH + "test"
RGB_PATH_RS = os.path.join(ROOT_PATH, RS_PATH, "rgb/")
RGB_PATH_JAI = os.path.join(ROOT_PATH, JAI_PATH, "rgb/")
PC_PATH = os.path.join(ROOT_PATH, RS_PATH, "pc/")
ANNOTATIONS_PATH_RS = os.path.join(ROOT_PATH, RS_PATH, "annotations/")
ANNOTATIONS_PATH_JAI = os.path.join(ROOT_PATH, JAI_PATH, "annotations/")
LOGS_PATH = os.path.join(ROOT_PATH, "logs/")

print(RGB_PATH_JAI)
print(RGB_PATH_RS)
print(PC_PATH)
print(ANNOTATIONS_PATH_JAI)
print(ANNOTATIONS_PATH_RS)
print(LOGS_PATH)


def create_folders():
    if not os.path.exists(ROOT_PATH):
        os.mkdir(ROOT_PATH)
        os.mkdir(os.path.join(ROOT_PATH, RS_PATH))
        os.mkdir(os.path.join(ROOT_PATH, JAI_PATH))
        os.mkdir(RGB_PATH_JAI)
        os.mkdir(RGB_PATH_RS)
        os.mkdir(PC_PATH)
        os.mkdir(ANNOTATIONS_PATH_JAI)
        os.mkdir(ANNOTATIONS_PATH_RS)
        os.mkdir(LOGS_PATH)

if __name__=="__main__":
    create_folders()