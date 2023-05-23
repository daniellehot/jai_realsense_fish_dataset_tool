from  pycocotools.coco import COCO
import matplotlib.pyplot as plt
import numpy as np
import cv2
import open3d as o3d
import os

ANNOTATIONS = ["annotations/img2-11.json",
               "annotations/img12-21.json",
               "annotations/img22-31.json",
               "annotations/img32-41.json"
               ]

CONDITIONS_DICT = {"annotations/img2-11.json" : "default_no_background",
               "annotations/img12-21.json" : "default_background",
               "annotations/img22-31.json" : "high_acc_background",
               "annotations/img32-41.json" : "high_acc_no_background"
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


def calculate_dot_product_of_normals(_pc, _mode):
    # Calculate surface normals
    o3d.geometry.PointCloud.estimate_normals(_pc, search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.01, max_nn=30))
    o3d.geometry.PointCloud.orient_normals_to_align_with_direction(_pc, orientation_reference=np.array([0.0,0.0, -1.0]))
    pcd_tree = o3d.geometry.KDTreeFlann(_pc)

    dot_products = []
    for p_idx in range(len(downpcd.points)):
        [k, idx, _] = pcd_tree.search_radius_vector_3d(_pc.points[p_idx], 0.01)
        #Remove the source point from the neighbourhood, otherwise we have at least one normal guaranteed to equal 1
        idx.remove(p_idx)
        
        if len(idx) != 0:
            inlier_cloud = _pc.select_by_index(idx)
            plane_n = np.asarray(_pc.normals[p_idx])
            normals_np = np.asarray(inlier_cloud.normals)
            dot_plane = normals_np.dot(plane_n)
            
            if _mode == 'min':
                dot_products.append(np.min(dot_plane))

            if _mode == "avg":
                dot_products.append(np.mean(dot_plane))
                
            if _mode == "all":
                dot_products += list(dot_plane)

    return dot_products


if __name__=="__main__":
        OUTPUT_FOLDER = "output_avg_all_fish"
        if not os.path.exists(OUTPUT_FOLDER):
            os.mkdir(OUTPUT_FOLDER)

        fig_combined, ax_combined = plt.subplots()
        fig_avg, ax_avg = plt.subplots()
        fig_individual, ax_individual = plt.subplots(4)

        for idx, path in enumerate(ANNOTATIONS):
            dot_products_cat =[] 
            no_of_points = []

            for fish in FISH:
                print("Working on ", fish, CONDITIONS_DICT[path], path)
                coco = COCO(path)
                query_cat_id = coco.getCatIds(fish)
                query_anns = coco.loadAnns( coco.getAnnIds(catIds=query_cat_id) )
                query_imgs = coco.loadImgs( coco.getImgIds(catIds=query_cat_id) )

                #dot_products_all_imgs_per_fish = []
                for i in range(len(query_imgs)):
                    # Sanity check for the annotation-image pair
                    if query_anns[i]["image_id"] != query_imgs[i]["id"]:
                        print("============")
                        print(query_anns[i]["image_id"])
                        print(query_imgs[i]["id"], query_imgs[i]["file_name"])
                        print("============")
                        exit(5)

                    mask = coco.annToMask(query_anns[i])
                    depth_img = cv2.imread(
                        os.path.join("depth_analysis_data/data/rs/depth", query_imgs[i]["file_name"]),
                        cv2.IMREAD_UNCHANGED
                        )
                    pcd = depth_map_to_masked_pc(_img=depth_img, _mask=mask)
                    no_of_points.append(len(np.asarray(pcd.points)))
                    downpcd = o3d.geometry.PointCloud.voxel_down_sample(pcd, voxel_size=0.0025)
                    #dot_products_all_imgs_per_fish += calculate_dot_product_of_normals(_pc=downpcd, _mode="avg")
                    #dot_products_cat += calculate_dot_product_of_normals(_pc=downpcd, _mode="avg")
                    dot_products_cat += calculate_dot_product_of_normals(_pc=downpcd, _mode="avg")
            ax_avg.bar(CONDITIONS_DICT[path], np.mean(np.asarray(no_of_points)), alpha=0.5, color = PLOT_COLORS[idx], label=CONDITIONS_DICT[path])
            ax_avg.set_xticks([])
            ax_individual[idx].hist(dot_products_cat, bins=20, alpha=0.5,  histtype='step', density=True, color = PLOT_COLORS[idx], label=CONDITIONS_DICT[path])
            ax_combined.hist(dot_products_cat, bins=20, alpha=0.5,  histtype='step', density=True, color = PLOT_COLORS[idx], label=CONDITIONS_DICT[path])
            
        fig_combined.legend(ncols=4, prop={'size': 5})
        fig_combined.tight_layout()
        fig_combined.savefig(os.path.join(OUTPUT_FOLDER, "avg_normal_distribution_per_category_combined.pdf" ))

        fig_individual.legend(ncols=4, prop={'size': 5})
        fig_individual.tight_layout()
        fig_individual.savefig(os.path.join(OUTPUT_FOLDER, os.path.join("avg_normal_distribution_per_category_individual.pdf" )))

        fig_avg.legend(ncols=4, prop={'size': 5})
        fig_avg.tight_layout()
        fig_avg.savefig(os.path.join(OUTPUT_FOLDER, os.path.join("avg_no_of_points.pdf" )))