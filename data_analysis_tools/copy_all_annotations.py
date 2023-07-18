import os
import shutil
src_dir = "/home/daniel/autofish_dataset_mini"
dst_dir = "/home/daniel/jai_realsense_fish_dataset_tool/data_analysis_tools/csv"
for root, dirs, files in os.walk(src_dir):
    for file in files:
        if "annotations" in root and file.endswith('.csv'):
            os.makedirs(os.path.join(root, file).replace(src_dir, dst_dir))
            shutil.copy(os.path.join(root, file), os.path.join(root, file).replace(src_dir, dst_dir) )