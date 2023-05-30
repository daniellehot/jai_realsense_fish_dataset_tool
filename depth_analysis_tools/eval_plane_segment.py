import open3d as o3d
import numpy as np
from  pycocotools.coco import COCO
import matplotlib.pyplot as plt
import cv2

from segment_plane import process_img_from_path

glob_path = "../../data_depth_analysis/data/rs/depth/*.png"

ANNOTATIONS = ["annotations/img2-11.json",
               "annotations/img12-21.json",
               "annotations/img22-31.json",
               "annotations/img32-41.json"
               ]

CONDITIONS_DICT = {"annotations/img2-11.json" : "def_no_bg",
               "annotations/img12-21.json" : "def_bg",
               "annotations/img22-31.json" : "acc_bg",
               "annotations/img32-41.json" : "acc_no_bg"
               }

FISH = ["54haddock",
        "23cod",
        "10saithe",
        "5cod",
        "2cod"
        ]

# Based on:
# https://www.kaggle.com/code/yerramvarun/understanding-dice-coefficient
def calc_dice_score(_mask1, _mask2):
    intersection = np.sum(_mask1*_mask2)
    dice = (2 * intersection) / (np.sum(_mask1) + np.sum(_mask2))
    return dice

def img2masks(_img):
    # Get unique valies
    vals = np.unique(_img)

    # Remove background label
    vals = vals[1:]

    masks = []
    for v in vals:
        curr_mask = np.zeros_like(_img).astype(np.float32)
        curr_mask[_img == v] = 1.0
        if(len(curr_mask.shape) == 3):
            curr_mask = curr_mask[:,:,0]
        masks.append(curr_mask)
    return masks

def load_masks_from_path(_path):
    seg_img = cv2.imread(seg_path)
    seg_masks = img2masks(seg_img)
    return seg_masks

def process_mask_pairs(_coco_masks, _seg_masks, _visualize=False):

    all_scores = []
    all_indices = []
    fn = 0
    for i1,m1 in enumerate(_coco_masks): # loop through annotations
        highest_score = 0
        highest_index = -1
        for i2,m2 in enumerate(_seg_masks): # loop through masks from segmentation
            dice_score = calc_dice_score(m1, m2)

            if(dice_score > highest_score): # update highest score
                highest_score = dice_score
                highest_index = i2

        # Check for false negatives / missing masks
        if(highest_score == 0.0 or highest_index in all_indices):
            fn += 1
        # Update list of scores
        all_scores.append(highest_score)
        all_indices.append(highest_index)
    avg_dice = np.mean(all_scores)

    if(_visualize):
        merged_coco_masks = np.clip(np.sum(np.stack(_coco_masks), axis=0),0,1)
        best_seg_masks = [_seg_masks[b] for b in all_indices]
        merged_seg_masks = np.clip(np.sum(np.stack(best_seg_masks), axis=0),0,1)
        plt.imshow(merged_coco_masks, cmap='jet')
        plt.imshow(merged_seg_masks, alpha=0.5, cmap='bwr')
        plt.title("Dice: {0} - FN: {1}".format(round(avg_dice,3), fn))
        plt.show()
    return fn, all_scores, avg_dice

if __name__ == "__main__":
    dist_thres = 0.020

    all_fns = {}
    all_dice_scores = {}
    for idx, path in enumerate(ANNOTATIONS): #[ANNOTATIONS[0]]):
        coco = COCO(path)
        coco_img_ids = coco.getImgIds()
        print("img ids: ", coco_img_ids)

        for img_id in coco_img_ids:
            # Load coco image info
            curr_img = coco.loadImgs(img_id)[0]
            img_name = curr_img["file_name"]

            # Convert fish names to category ids
            coco_cat_ids = [coco.getCatIds(f)[0] for f in FISH]

            # Extract masks from coco annotations
            coco_anns = [coco.loadAnns(coco.getAnnIds(imgIds=img_id,catIds=coco_cat_id))[0] for coco_cat_id in coco_cat_ids]
            coco_masks = [coco.annToMask(ann) for ann in coco_anns]

            # Extract masks from segmented image
            seg_path = glob_path.replace("*.png",img_name)
            #print(seg_path)
            #seg_masks = load_masks_from_path(seg_path)
            test = process_img_from_path(seg_path, _dist_thres=dist_thres)
            seg_masks = img2masks(test)

            # Compare masks
            fn, dice_scores, avg_dice = process_mask_pairs(coco_masks, seg_masks) #, _visualize=True)

            if(path not in all_fns.keys()):
                all_fns[path] = []
                all_dice_scores[path] = []

            all_fns[path].append(fn)
            all_dice_scores[path]+= dice_scores
            break

        print("---------------")
        print(path)
        print("fns: ", np.sum(np.array(all_fns[path]).flatten()))
        print(np.mean(np.array(all_dice_scores[path], dtype=np.float32).flatten()))
        print("---------------")

    # Create nice plots...
    dice_avgs = [np.mean(np.array(all_dice_scores[path], dtype=np.float32).flatten()) for path in ANNOTATIONS]
    fns = [np.sum(np.array(all_fns[path]).flatten()) for path in ANNOTATIONS]
    labels = [CONDITIONS_DICT[p] for p in ANNOTATIONS]


    fig = plt.figure(figsize=(16.0,12.0))
    plt.subplot(2,1,1)
    plt.ylim(0.0, 1.0)
    plt.bar(labels, dice_avgs)
    plt.title("DICE score (higher is better)")
    plt.grid(b=True, which='major', color='k', linestyle='-')
    plt.grid(b=True, which='minor', color='r', linestyle='-', alpha=0.2)
    plt.minorticks_on()
    plt.subplot(2,1,2)
    plt.bar(labels, fns)
    plt.grid(b=True, which='major', color='k', linestyle='-')
    plt.grid(b=True, which='minor', color='r', linestyle='-', alpha=0.2)
    plt.minorticks_on()
    plt.title("False Negatives (lower is better)")
    plt.savefig("eval-plane-seg_{0}.png".format(dist_thres), dpi=300)
