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
               "depth_analysis_data/img12-21.json" : "defaul_backgroud",
               "depth_analysis_data/img22-31.json" : "high_acc_backgroud",
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
    o3d.geometry.PointCloud.orient_normals_to_align_with_direction(_pc, orientation_reference=np.array([0.0,0.0, -1.0]))
    pcd_tree = o3d.geometry.KDTreeFlann(_pc)

    dot_products = []
    for p_idx in range(len(downpcd.points)):
        [k, idx, _] = pcd_tree.search_radius_vector_3d(_pc.points[p_idx], 0.01)
        inlier_cloud = _pc.select_by_index(idx)
        plane_n = np.asarray(_pc.normals[p_idx])
        normals_np = np.asarray(inlier_cloud.normals)
        dot_plane = normals_np.dot(plane_n)
        dot_products.append(np.min(dot_plane))
    return dot_products

if __name__=="__main__":
        for fish in FISH:
            fig, ax = plt.subplots(4)
            ax[0].set_title(fish)

            dot_products_all_categories = []
            for idx, path in enumerate(ANNOTATIONS):
                print("Working on ", fish, CONDITIONS_DICT[path])
                coco = COCO(path)
                query_id = coco.getCatIds(fish)
                query_anns = coco.loadAnns( coco.getAnnIds(catIds=query_id) )
                query_imgs = coco.loadImgs( coco.getImgIds(catIds=query_id) )

                dot_products_all_imgs = []
                for i in range(len(query_imgs)):
                    mask = coco.annToMask(query_anns[i])
                    if query_anns[i]["image_id"] != query_imgs[i]["id"]:
                        print("============")
                        print(query_anns[i]["image_id"])
                        print(query_imgs[i]["id"])
                        print("============")
                    depth_img = cv2.imread(
                        os.path.join("depth_analysis_data/data/rs/depth", query_imgs[i]["file_name"]),
                        cv2.IMREAD_UNCHANGED
                        )
                    pcd = depth_map_to_masked_pc(_img=depth_img, _mask=mask)
                    # Downsample pointcloud
                    downpcd = o3d.geometry.PointCloud.voxel_down_sample(pcd, voxel_size=0.0025)
                    dot_products_all_imgs += calculate_dot_product_of_normals(_pc=downpcd)

                dot_products_all_categories.append(dot_products_all_imgs)
                ax[idx].hist(dot_products_all_imgs, bins=20, alpha=0.5, density=False, color = PLOT_COLORS[idx], label=CONDITIONS_DICT[path])

            fig.legend(ncols=2, prop={'size': 5})
            fig.tight_layout()
            fig.savefig(os.path.join("data", fish+".pdf" ))
        
            fig_combined, ax_combined = plt.subplots()
            ax_combined.set_title(fish)
            for idx, dot_products_cat in enumerate(dot_products_all_categories):
                ax_combined.hist(dot_products_cat, bins=20, alpha=0.5,  histtype='step', density=False, color = PLOT_COLORS[idx], label=CONDITIONS_DICT[path])
            fig_combined.legend(ncols=2, prop={'size': 5})
            fig_combined.tight_layout()
            fig_combined.savefig(os.path.join("data", fish+"_combined.pdf" ))
    
    
