from  pycocotools.coco import COCO
import matplotlib.pyplot as plt
import numpy as np
import cv2
import open3d as o3d
import os
from pyemd import emd_with_flow, emd
import pandas as pd


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

FISH_COLOR_DICT = {"54haddock" : 'blue',
                   "23cod" : 'orange',  
                   "10saithe" : 'green',
                   "5cod" : 'red',
                   "2cod" : 'purple'
                }

PLOT_COLORS = ['blue', 'orange', 'green', 'red', 'purple', 'black', 'cyan', 'magenta', 'saddlebrown', 'olive']

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


def estimate_plane(_img):
    max_depth = 1200
    _img[_img > max_depth] = max_depth
    o3_depth_image = o3d.geometry.Image(_img)
    pcd = o3d.geometry.PointCloud.create_from_depth_image(o3_depth_image, RS_INTRINSICS)
    #plane_model, inliers = pcd.segment_plane(distance_threshold=0.01, ransac_n=10, num_iterations=1000)
    plane_model, inliers = pcd.segment_plane(distance_threshold=0.01, ransac_n=3, num_iterations=1000)
    #[a, b, c, d] = plane_model
    #print(f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")
    """
    plane_cloud = pcd.select_by_index(inliers)
    inlier_cloud.paint_uniform_color([1.0, 0, 0])
    outlier_cloud = pcd.select_by_index(inliers, invert=True)
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
                                    zoom=0.8,
                                    front=[-0.4999, -0.1659, -0.8499],
                                    lookat=[2.1813, 2.0619, 2.0999],
                                    up=[0.1204, -0.9852, 0.1215])
    """
    return plane_model


def calculate_distances(_plane, _fish):
    #print(_fish.shape)
    fish_points = np.c_[ _fish, np.ones(_fish.shape[0]) ]
    #print(fish_points)
    [a, b, c, d] = _plane
    #print("[a, b, c, d]")
    #print([a, b, c, d])
    plane = np.asarray([a, b, c, d])
    #print("plane")
    #print(plane)
    #print("np.abs(fish_points.dot(plane))")
    #print(np.abs(fish_points.dot(plane)))
    #print("np.linalg.norm(plane[:3])")
    #print(np.linalg.norm(plane[:3]))
    distances = np.abs(fish_points.dot(plane)) / np.linalg.norm(plane[:3])
    #print(distances)
    return distances


def generate_signatures(freq1, bins1, freq2, bins2, normalize):
    if normalize:
        freq1 = freq1/sum(freq1) * 100
        freq2 = freq2/sum(freq2) * 100
    all_bins = list(np.concatenate((bins1, bins2)))
    distribution1_sig = np.concatenate((freq1, np.zeros(len(bins2))))
    distribution2_sig = np.concatenate((np.zeros(len(bins1)), freq2))

    #print("============")
    #print(all_bins)
    #print(np.concatenate((freq1, freq2)))
    #print("============")
    #print(distribution1_sig)
    #print("============")
    #print(distribution2_sig)
    #print("============")
    return all_bins, distribution1_sig, distribution2_sig


def compute_dist_matrix(positions):
    dist_matrix = np.eye(len(positions))
    for i in range(len(positions)):
        for j in range(len(positions)):
            dist_matrix[i, j] = np.abs(positions[i]-positions[j])
    return dist_matrix


def calculate_emd(freq1, bins1, freq2, bins2, normalize):
    all_bins, signature_1, signature_2 = generate_signatures(freq1, bins1, freq2, bins2, normalize)

    distance_matrix = compute_dist_matrix(all_bins)
    #print(pd.DataFrame(distance_matrix.round(4), index=np.around(all_bins, 4), columns=np.around(all_bins, 4)))
    first_signature = np.array(signature_1, dtype=np.double)
    second_signature = np.array(signature_2, dtype=np.double)
    distances = np.array(distance_matrix, dtype=np.double)
    #emd_value, flow = emd_with_flow(first_signature, second_signature, distances)
    #flow = np.array(flow)
    if len(first_signature) != len(second_signature):
        print("Signature lengths dont match")
        exit(5)
        
    emd_value = emd(first_signature, second_signature, distances)
    return emd_value

class EMDData():
    def _init_(self, emd_value, freq1, bins1, freq2, bins2, fish, preset):
        self.emd_value = emd_value
        self.freq1, self.freq2 = freq1, freq2
        self.bins1, self.bins2 = bins1, bins2
        self.fish, self.preset = fish, preset


if __name__=="__main__":
        #calculate_distances(_plane = [2, -2, 5, 8], _fish = np.array([[4, -4, 3], [4, 4, 3]])) 
        #exit(5)

        VOXEL_SIZE = 0.0025
        VOXEL_SIZE = 0.1
        OUTPUT_FOLDER = "height_analysis"
        if not os.path.exists(OUTPUT_FOLDER):
            os.mkdir(OUTPUT_FOLDER)

        #fig, ax = plt.subplots(4)
        #fig_avg, ax_avg = plt.subplots()
        #fig_emd, ax_emd = plt.subplots(4)
        
        box_plot_data = []
        fig, (ax_box, ax_scatter) = plt.subplots(1, 2)
        for idx, path in enumerate(ANNOTATIONS):
            #cat_emd_values = []    
            emd_values = []
            emd_pairs = []
            emd_freqs = []
            emd_bins = []
            emd_height_data = []
            
            for fish in FISH:    
                print("Working on ", fish, CONDITIONS_DICT[path], path)
                coco = COCO(path)
                query_cat_id = coco.getCatIds(fish)
                query_anns = coco.loadAnns( coco.getAnnIds(catIds=query_cat_id) )
                query_imgs = coco.loadImgs( coco.getImgIds(catIds=query_cat_id) )
                
                freqs, bins = [], []
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
                    fish_pcd = depth_map_to_masked_pc(_img=depth_img, _mask=mask)
                    fish_pcd = o3d.geometry.PointCloud.voxel_down_sample(fish_pcd, voxel_size=VOXEL_SIZE) 
                    plane_model = estimate_plane(_img = depth_img)
                    height_profile = calculate_distances(plane_model, np.asarray(fish_pcd.points))
                    
                    height_freqs, height_bins = np.histogram(height_profile, bins=50, density=False)
                    height_bins_centers = 0.5 * (height_bins[1:] + height_bins[:-1])
                    freqs.append(height_freqs)
                    bins.append(height_bins_centers)
                    # Save to later plot histograms
                    emd_freqs.append(height_freqs)
                    emd_bins.append(height_bins)
                    emd_height_data.append(height_profile)
                

                for i in range(len(freqs)):
                    for j in range(i, len(freqs)):
                        if i != j:
                            emd_values.append(calculate_emd(freqs[i], bins[i], freqs[j], bins[j], normalize = True))
                            emd_pairs.append((i, j))
            
            fig, (ax_median, ax_max) = plt.subplots(2)

            median_emd = np.median(emd_values)
            median_idx = emd_values.index(median_emd)
            querry_i = emd_pairs[median_idx][0] 
            querry_j = emd_pairs[median_idx][1]
            #ax_median.bar(emd_bins[querry_i], freqs[querry_i]/sum(freqs[querry_i]), align="center", alpha=0.5, width=np.abs(bins[querry_i][1] - bins[querry_i][0]))
            #ax_median.bar(emd_bins[querry_j], freqs[querry_j]/sum(freqs[querry_j]), align="center", alpha=0.5, width=np.abs(bins[querry_j][1] - bins[querry_j][0]))
            ax_median.set_title("emd=" + str(np.around(median_emd, 4)))
            ax_median.stairs(emd_freqs[querry_i]/sum(emd_freqs[querry_i]), emd_bins[querry_i], fill=True, alpha=0.5)
            ax_median.stairs(emd_freqs[querry_j]/sum(emd_freqs[querry_j]), emd_bins[querry_j], fill=True, alpha=0.5)

            max_emd = max(emd_values)
            max_idx = emd_values.index(max_emd)
            querry_i = emd_pairs[max_idx][0]
            querry_j = emd_pairs[max_idx][1]
            #ax_max.bar(emd_bins[querry_i], freqs[querry_i]/sum(freqs[querry_i]), align="center", alpha=0.5, width=np.abs(bins[querry_i][1] - bins[querry_i][0]))
            #ax_max.bar(emd_bins[querry_j], freqs[querry_j]/sum(freqs[querry_j]), align="center", alpha=0.5, width=np.abs(bins[querry_j][1] - bins[querry_j][0]))
            ax_max.set_title("emd=" + str(np.around(max_emd, 4)))
            ax_max.stairs(emd_freqs[querry_i]/sum(emd_freqs[querry_i]), emd_bins[querry_i], fill=True, alpha=0.5)
            ax_max.stairs(emd_freqs[querry_j]/sum(emd_freqs[querry_j]), emd_bins[querry_j], fill=True, alpha=0.5)

            fig.supylabel(CONDITIONS_DICT[path])
            fig.tight_layout()
            fig.savefig(os.path.join(OUTPUT_FOLDER, os.path.join(CONDITIONS_DICT[path])))


            

        """

            ax_scatter.scatter([CONDITIONS_DICT[path]]*len(emd_values), emd_values, alpha = 0.25, c=emd_colors)
            box_plot_data.append(emd_values)

        ax_box.boxplot(box_plot_data)
        ax_box.set_xticks([1, 2, 3, 4], list(CONDITIONS_DICT.values()))
        ax_box.tick_params(axis="x", labelsize = 3, labelrotation = 30)        
        ax_scatter.tick_params(axis="x", labelsize = 3, labelrotation = 30)
        
        handlelist = [ax_scatter.plot([], marker="o", ls="", color=color)[0] for color in list(FISH_COLOR_DICT.values())]
        ax_scatter.legend(handlelist,list(FISH_COLOR_DICT.keys()), bbox_to_anchor=(1.1, 1), fontsize =5)

        fig.tight_layout()
        fig.savefig(os.path.join(OUTPUT_FOLDER, os.path.join("box_scatter_all_fish.pdf" )))
        """

        #https://safjan.com/metrics-to-compare-histograms/
#https://theailearner.com/2019/08/13/earth-movers-distance-emd/ 
#https://stats.stackexchange.com/questions/157468/how-to-determine-similarity-between-histograms-which-metric-to-use
#https://stats.stackexchange.com/questions/157468/how-to-determine-similarity-between-histograms-which-metric-to-use