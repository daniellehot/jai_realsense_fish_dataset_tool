from  pycocotools.coco import COCO
import matplotlib.pyplot as plt
import numpy as np
import cv2
import open3d as o3d
import os

ANNOTATIONS = ["depth_analysis_data/img2-11.json",
               "depth_analysis_data/img12-21.json",
               "depth_analysis_data/img22-31.json",
               "depth_analysis_data/img32-41.json"
               ]

CONDITIONS_DICT = {"depth_analysis_data/img2-11.json" : "default_no_background",
               "depth_analysis_data/img12-21.json" : "default_background",
               "depth_analysis_data/img22-31.json" : "high_acc_background",
               "depth_analysis_data/img32-41.json" : "high_acc_no_background"
               }

FISH = ["54haddock",
        "23cod",
        "10saithe",
        "5cod",
        "2cod"
        ]

PLOT_COLORS = ['blue', 'orange', 'green', 'red', 'purple']

RS_INTRINSICS = o3d.camera.PinholeCameraIntrinsic( 1920, #width
                                                1080, #height
                                                1386.84, #fx
                                                1385.35, #fy
                                                928.33, #cx
                                                537.03 #cy
                                                ) 


if __name__=="__main__":
        for fish in FISH:
            for idx, path in enumerate(ANNOTATIONS):
                #print("Working on ", fish, CONDITIONS_DICT[path], path)
                coco = COCO(path)
                query_id = coco.getCatIds(fish)
                query_ann_ids = coco.getAnnIds(catIds=query_id)
                query_img_ids = coco.getImgIds(catIds=query_id)
                
                cats = coco.loadCats(query_id)   
                #print(cats[0]["name"])
                anns = coco.loadAnns(query_ann_ids)
                #print(len(anns))
                imgs = coco.loadImgs(query_img_ids)
               

                if len(anns)!=10 or len(imgs)!=10 :
                    print("============")
                    print(cats[0]["name"], CONDITIONS_DICT[path], path)
                    print("anns", len(anns))
                    print("imgs", len(imgs))
                    print("============")
                    exit(5)

                """
                query_anns = coco.loadAnns( coco.getAnnIds(catIds=query_id) )
                #print(query_anns)
                query_imgs = coco.loadImgs( coco.getImgIds(catIds=query_id) )
                #print(query_imgs)

                dot_products_all_imgs = []
                #for i in range(len(query_imgs)):
                for ann in query_anns:
                    #mask = coco.annToMask(query_anns[i])
                    mask = coco.annToMask(ann)
                    print(mask)
                """