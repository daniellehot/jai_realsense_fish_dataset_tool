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

FISH = ["54haddock",
        "23cod",
        "10saithe",
        "5cod",
        "2cod"
        ]

RS_INTRINSICS = o3d.camera.PinholeCameraIntrinsic(1920, #width
                                                        1080, #height
                                                        1386.84, #fx
                                                        1385.35, #fy
                                                        928.33, #cx
                                                        537.03 #cy
                                                        ) 

def depth_map_to_masked_pc(_img, _mask):
    # Apply max depth threshold
    max_depth = 1200
    _img[_img > max_depth] = max_depth

    # Mask image and convert to open3d image
    masked_depth = _img * _mask
    o3_image = o3d.geometry.Image(masked_depth)

    # Convert image to pointcloud
    pcd = o3d.geometry.PointCloud.create_from_depth_image(o3_image, RS_INTRINSICS)
    return pcd


def calculate_dot_product_of_normals(_pc):
    # Calculate surface normals
    o3d.geometry.PointCloud.estimate_normals(_pc, search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.01, max_nn=30))
    o3d.geometry.PointCloud.orient_normals_to_align_with_direction(_pc, orientation_reference=np.array([0.0,0.0,-1.0]))
    pcd_tree = o3d.geometry.KDTreeFlann(_pc)

    dot_products = []
    for p_idx in range(len(downpcd.points)):
        [k, idx, _] = pcd_tree.search_radius_vector_3d(_pc.points[p_idx], 0.01)
        inlier_cloud = _pc.select_by_index(idx)
        #inlier_cloud.paint_uniform_color([0.0, 1.0, 0.0])
        plane_n = np.asarray(_pc.normals[p_idx])
        normals_np = np.asarray(inlier_cloud.normals)
        dot_plane = normals_np.dot(plane_n)
        dot_plane = np.abs(dot_plane) # crap fix! shouldn't be needed!!
        dot_products.append(np.min(dot_plane))
    print(np.any((np.asarray(dot_products)<0)))
    return dot_products

if __name__=="__main__":
    coco = COCO("depth_analysis_data/img2-11.json")
    query_id = coco.getCatIds("54haddock")
    query_anns = coco.loadAnns( coco.getAnnIds(catIds=query_id) )
    query_imgs = coco.loadImgs( coco.getImgIds(catIds=query_id) )

    for i in range(len(query_imgs)):
        mask = coco.annToMask(query_anns[i])
        depth_img = cv2.imread(
            os.path.join("depth_analysis_data/data/rs/depth", query_imgs[i]["file_name"]),
            cv2.IMREAD_UNCHANGED)
        pcd = depth_map_to_masked_pc(_img=depth_img, _mask=mask)
        # Downsample pointcloud
        downpcd = o3d.geometry.PointCloud.voxel_down_sample(pcd, voxel_size=0.0025)
        dot_product = calculate_dot_product_of_normals(_pc=downpcd)
        print("iteration", i, dot_product[10:30])
        #o3d.visualization.draw_geometries([downpcd])


        


    #imgIds = coco.getImgIds()
    #catIds = coco.getCatIds()
    #annIds = coco.getAnnIds()

    #imgs = coco.loadImgs(imgIds)
    #cats = coco.loadCats(catIds)
    #anns = coco.loadAnns(annIds)


    #goal_fish = "54haddock"
    #querry_id = coco.getCatIds(goal_fish)
    #print(querry_id)
    #query_annotations = coco.getAnnIds(catIds=querry_id)
    #query_img_ids = coco.getImgIds(catIds=querry_id)
    #print(query_annotations)
    #print(len(query_annotations))
    #anns = coco.loadAnns(query_annotations)
    #imgs = coco.loadImgs(query_img_ids)
    #print(imgs[2])
    #print(anns[2])
    #print("=========")
    #print(imgs[5])
    #print(anns[5])

    #exit(5)

    #annotations_for_cat = an

    #for img in imgs:
        #print(img)

        #get image annotations
        #ann = anns[img["id"]]
        #print(ann)


    #annIds = coco.getAnnIds()

    #print("annIds", annIds, "\n================")
    #anns = coco.loadAnns(annIds)
    #print(anns)
    ##mask = coco.annToMask(anns[i]