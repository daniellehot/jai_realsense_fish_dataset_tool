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


def calculate_angles_between_vectors(dot_product, a, b):
    dot_product = np.around(dot_product, 4)
    norm_a = np.around(np.linalg.norm(a), 4)
    norm_b = np.around(np.linalg.norm(b, axis=1), 4)
    if (np.any(dot_product < -1) or np.any(dot_product > 1)):
        print(dot_product)
        exit(5)
    angles = np.arccos(dot_product/(norm_a*norm_b))
    return angles
    #return np.arccos(a.dot(b)/(np.linalg.norm(a)*np.linalg.norm(b)))
    

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


def calculate_angles(_pc, _mode):
    # Calculate surface normals
    o3d.geometry.PointCloud.estimate_normals(_pc, search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.01, max_nn=30))
    o3d.geometry.PointCloud.orient_normals_to_align_with_direction(_pc, orientation_reference=np.array([0.0,0.0, -1.0]))
    pcd_tree = o3d.geometry.KDTreeFlann(_pc)

    angles = []
    for p_idx in range(len(downpcd.points)):
        [k, idx, _] = pcd_tree.search_radius_vector_3d(_pc.points[p_idx], 0.01)
        #Remove the source point from the neighbourhood, otherwise we have at least one dot guaranteed to equal 1
        idx.remove(p_idx)
        
        if len(idx) != 0:
            base_normal = np.asarray(_pc.normals[p_idx])
            inlier_cloud = _pc.select_by_index(idx)    
            neighbourhood_normals = np.asarray(inlier_cloud.normals)
            #print("neighbourhood_normals", neighbourhood_normals)
            dot_products = neighbourhood_normals.dot(base_normal)
            #print(dot_products)
            all_angles = np.degrees(calculate_angles_between_vectors(dot_products, base_normal, neighbourhood_normals))
            
            #arccos returns nan when dot product equals 1 because norm_a*norm_b doesnt add up to 1 but to 0.99999999, meaning arccos = (1/0.99) = 1.01 
            #all_angles[dot_products >= 1] = 0
            #all_angles[dot_products <= -1] = 180
            #print("dot_products nan")
            #print(dot_products[np.isnan(all_angles)])
            
            if _mode == 'min':
                angles.append(np.min(all_angles))

            if _mode == "avg":
                angles.append(np.mean(all_angles))
                
            if _mode == "all":
                angles += list(all_angles)

    return angles


def sort_angles(angles):

    angles_np = np.asarray(angles)
    #angles_np = angles_np[~np.isnan(angles_np)]
    #Sanity check, arccos should return the smaller angle between two vectors, meaning it cant be a negative value
    
    #angles_np_negative = angles_np[angles_np < 0].nonzero()
    #if (np.isangles_np_negative):
    #    print(angles_np_negative)
    #    print("negative angle between vectors")
    #   exit(5)
    
    # Angles under 15 degrees, good match 
    angles_under_15 = np.where(angles_np <= 15, angles_np, -1)
    angles_under_15 = angles_under_15[angles_under_15 != -1]

    # Angles under 15 degrees, medium match 
    angles_under_30 = np.where(angles_np <= 30, angles_np, -1)
    angles_under_30 = np.where(angles_under_30 > 15, angles_under_30, -1)
    angles_under_30 = angles_under_30[angles_under_30 != -1]

    ## Angles over 30 degrees, poor match 
    angles_over_30 = np.where(angles_np > 30, angles_np, -1)
    angles_over_30 = angles_over_30[angles_over_30 != -1]

    disributions = [0, 0, 0] #under 15, under 30, over 30
    disributions[0] = angles_under_15.size/angles_np.size * 100
    disributions[1] = angles_under_30.size/angles_np.size * 100
    disributions[2] = angles_over_30.size/angles_np.size * 100
    disributions = np.around(disributions, 2)

    #print(angles_np.size - angles_under_15.size - angles_under_30.size - angles_over_30.size)
    #print(disributions)
    #print("sum distributions", sum(disributions))
    
    return disributions

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
        VOXEL_SIZE = 0.0025
        #VOXEL_SIZE = 0.0100

        OUTPUT_FOLDER = "angle_avg_all_fish"
        if not os.path.exists(OUTPUT_FOLDER):
            os.mkdir(OUTPUT_FOLDER)

        fig_combined, ax_combined = plt.subplots()
        fig_avg, ax_avg = plt.subplots()
        fig_individual, ax_individual = plt.subplots(4)
        
        distributions_per_cat = []
        for idx, path in enumerate(ANNOTATIONS):
            dot_products_cat =[] 
            no_of_points = []

            angles_per_cat = []
            for fish in FISH:
                print("Working on ", fish, CONDITIONS_DICT[path], path)
                coco = COCO(path)
                query_cat_id = coco.getCatIds(fish)
                query_anns = coco.loadAnns( coco.getAnnIds(catIds=query_cat_id) )
                query_imgs = coco.loadImgs( coco.getImgIds(catIds=query_cat_id) )

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
                    downpcd = o3d.geometry.PointCloud.voxel_down_sample(pcd, voxel_size=VOXEL_SIZE)
                    angles_per_cat += calculate_angles(_pc = downpcd, _mode="avg")
            

                    #angles_per_cat.append( calculate_angles(_pc = downpcd, _mode="avg") )
            
            distributions_per_cat.append(sort_angles(angles_per_cat))
        
            ax_individual[idx].hist(angles_per_cat, bins=12, alpha=0.5,  histtype='step', density=True, color = PLOT_COLORS[idx], label=CONDITIONS_DICT[path])
            ax_combined.hist(angles_per_cat, bins=12, alpha=0.5,  histtype='step', density=True, color = PLOT_COLORS[idx], label=CONDITIONS_DICT[path])
            ax_individual[idx].set_xticks(np.arange(0, 180, 15))
            ax_combined.set_xticks(np.arange(0, 180, 15))
        

        fig_bar, ax_bar = plt.subplots()
        bar_x_axis_ticks = ["<15", "<15, 30>", ">30"]
        x = np.arange(len(bar_x_axis_ticks))  # the label locations
        width = 0.1  # the width of the bars
        multiplier = 0

        for idx, distribution in enumerate(distributions_per_cat):
            offset = width * multiplier
            rects = ax_bar.bar(x + offset, distribution, width, alpha = 0.5, color = PLOT_COLORS[idx], label=list(CONDITIONS_DICT.values())[idx])
            ax_bar.bar_label(rects, padding=3, fontsize = 5)
            multiplier += 1
        ax_bar.set_xticks(x + width, bar_x_axis_ticks)

        fig_bar.legend(ncols=2, prop={'size': 5})
        fig_bar.tight_layout()
        fig_bar.savefig(os.path.join(OUTPUT_FOLDER, "bar.pdf" ))

        fig_combined.legend(ncols=4, prop={'size': 5})
        fig_combined.tight_layout()
        fig_combined.savefig(os.path.join(OUTPUT_FOLDER, "avg_normal_distribution_per_category_combined.pdf" ))

        fig_individual.legend(ncols=4, prop={'size': 5})
        fig_individual.tight_layout()
        fig_individual.savefig(os.path.join(OUTPUT_FOLDER, os.path.join("avg_normal_distribution_per_category_individual.pdf" )))

        #fig_avg.legend(ncols=4, prop={'size': 5})
        #fig_avg.tight_layout()
        #fig_avg.savefig(os.path.join(OUTPUT_FOLDER, os.path.join("avg_no_of_points.pdf" )))
        