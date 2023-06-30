import os
HOME_PATH = os.path.expanduser('~')
import sys
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/viewer"))
from viewer import RGB_PATH_RS, RGB_PATH_JAI, ANNOTATED_PATH_JAI, DEPTH_PATH_RS, PC_PATH_RS, ANNOTATIONS_PATH_RS, ANNOTATIONS_PATH_JAI
sys.path.append(os.path.join(HOME_PATH, "jai_realsense_fish_dataset_tool/calibration"))
from calibration import CALIBRATION_PATH_RS, CALIBRATION_PATH_JAI

def fix_path(path, group_str):
    path = path.replace("/jai_realsense_fish_dataset_tool/viewer/", "/{}/".format("groups"))
    path = path.replace("/data/", "/{}/".format(group_str))
    return path


if __name__=="__main__":
    #groups = os.listdir("/home/vap/groups/")
    groups = os.listdir("/home/vap/OneDrive/autofish_groups/")
    groups = [group for group in groups if "group_" in group]
    groups.sort()
    print("GROUPS: {}".format(groups))
    print("================================")
    print("LEGEND")
    print("group [rgb_rs, rgb_jai, rgb_annotated_jai, depth_rs, pc_rs, annotations_rs, annotations_jai] number_of_files_together CALIBRATION [calibration_rs, calibration_jai]")
    print("================================")
    for group in groups:
        rgb_rs = len(os.listdir(fix_path(RGB_PATH_RS, group))) 
        rgb_jai = len(os.listdir(fix_path(RGB_PATH_JAI, group)))
        rgb_annotated_jai = len(os.listdir(fix_path(ANNOTATED_PATH_JAI, group)))
        depth_rs = len(os.listdir(fix_path(DEPTH_PATH_RS, group)))
        pc_rs = len(os.listdir(fix_path(PC_PATH_RS, group)))
        annotations_rs = len(os.listdir(fix_path(ANNOTATIONS_PATH_RS, group)))
        annotations_jai = len(os.listdir(fix_path(ANNOTATIONS_PATH_JAI, group)))
        number_of_files = rgb_rs + rgb_jai + rgb_annotated_jai + depth_rs + pc_rs + annotations_rs + annotations_jai

        calibration_rs = len(os.listdir(fix_path(CALIBRATION_PATH_RS, group)))
        calibration_jai = len(os.listdir(fix_path(CALIBRATION_PATH_JAI, group)))
        
        if (len(group) != 8):
            group += " "
        print("{} [{}, {}, {}, {}, {}, {}, {}] {} CALIBRATION [{}, {}]"
              .format(group, rgb_rs, rgb_jai, rgb_annotated_jai, depth_rs, pc_rs, annotations_rs, annotations_jai, number_of_files, calibration_rs, calibration_jai))

    """
    print(RGB_PATH_RS)
    print(RGB_PATH_JAI)
    print(ANNOTATED_PATH_JAI)
    print(DEPTH_PATH_RS)
    print(PC_PATH_RS)
    print(ANNOTATIONS_PATH_RS)
    print(ANNOTATIONS_PATH_JAI)
    print(CALIBRATION_PATH_RS)
    print(CALIBRATION_PATH_JAI)
    """