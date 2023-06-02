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
    plane_model, inliers = pcd.segment_plane(distance_threshold=0.01, ransac_n=10, num_iterations=1000)
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


def generate_signatures(freq1, bins1, freq2, bins2):
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

    # Calculate bin centers
    bins1 = 0.5 * (bins1[1:] + bins1[:-1])
    bins2 = 0.5 * (bins2[1:] + bins2[:-1])
    # Normalize data if true
    if normalize:
        freq1 = freq1/sum(freq1) * 100
        freq2 = freq2/sum(freq2) * 100

    # Generate signatures
    all_bins, signature_1, signature_2 = generate_signatures(freq1, bins1, freq2, bins2)
    
    # Compute distance matrix for all bins
    distance_matrix = compute_dist_matrix(all_bins)
    #print(pd.DataFrame(distance_matrix.round(4), index=np.around(all_bins, 4), columns=np.around(all_bins, 4)))
    
    # Cast all data to double (required by pyemd)
    first_signature = np.array(signature_1, dtype=np.double)
    second_signature = np.array(signature_2, dtype=np.double)
    distances = np.array(distance_matrix, dtype=np.double)
    
    # Sanity check before emd computation
    if len(first_signature) != len(second_signature):
        print("Signature lengths dont match")
        exit(5)
        
    emd_value = emd(first_signature, second_signature, distances)
    #emd_value, flow = emd_with_flow(first_signature, second_signature, distances)
    #flow = np.array(flow)
    return emd_value


class EMDData():
    def __init__(self, emd_value, freq1, bins1, image1, freq2, bins2, image2, fish, preset):
        self.emd_value = emd_value
        self.freq1, self.freq2 = freq1, freq2
        self.bins1, self.bins2 = bins1, bins2
        self.img1, self.img2 = image1, image2
        self.fish, self.preset = fish, preset


def compute_average_plane(imgs, preset):
    print("Computing average plane")
    plane_models = []
    for img in imgs:
        depth_img = cv2.imread( os.path.join("depth_analysis_data/data/rs/depth", img["file_name"]), cv2.IMREAD_UNCHANGED)
        for i in range(3):
            print("Preset {} Img {} Iteration {} ".format(preset, img["file_name"], i))
            plane_models.append(estimate_plane(depth_img))
    plane_models = np.asarray(plane_models)
    avg_plane_model = np.mean(plane_models, axis=0)
    angles_to_plot = compute_angles_between_planes(plane_models)
    return avg_plane_model, angles_to_plot

def compute_angles_between_planes(plane_models):
    angles = []
    for i in range(plane_models.shape[0]):
        plane1 = plane_models[i, :3]
        for j in range(i, plane_models.shape[0]):
            plane2 = plane_models[j, :3]
            if i != j:
                dot_product_between_planes = np.abs(plane1.dot(plane2))
                plane1_norm = np.linalg.norm(plane1)
                plane2_norm = np.linalg.norm(plane2)
                angle_betweeen_planes = np.arccos(dot_product_between_planes/(plane1_norm*plane2_norm))
                angles.append(angle_betweeen_planes)
    return angles

if __name__=="__main__":
        #calculate_distances(_plane = [2, -2, 5, 8], _fish = np.array([[4, -4, 3], [4, 4, 3]])) 
        #exit(5)

        VOXEL_SIZE = 0.0025
        #VOXEL_SIZE = 0.1
        OUTPUT_FOLDER = "height_analysis"
        if not os.path.exists(OUTPUT_FOLDER):
            os.mkdir(OUTPUT_FOLDER)

        fig_all, (ax_box, ax_scatter) = plt.subplots(1, 2)
        ax_scatter.tick_params(axis="x", labelsize = 3, labelrotation = 30)
        fig_angles, ax_angles = plt.subplots()
        ax_angles.tick_params(axis="x", labelsize = 3, labelrotation = 30)  
        ax_angles.set_ylabel("degrees")

        box_plot_data = []
        for idx, path in enumerate(ANNOTATIONS):    
            emd_values = []
            emd_data = []
            emd_colors = []
            bins_to_use = np.arange(0, 0.06+0.0025, 0.0025)
            
            coco = COCO(path)
            imgs = coco.loadImgs( coco.getImgIds() )
            plane_model, angles = compute_average_plane(imgs, CONDITIONS_DICT[path])
            ax_angles.scatter([CONDITIONS_DICT[path]]*len(angles), angles, alpha = 0.25, c=PLOT_COLORS[idx])
            
            for fish in FISH:    
                print("Working on ", fish, CONDITIONS_DICT[path], path)
                query_cat_id = coco.getCatIds(fish)
                query_anns = coco.loadAnns( coco.getAnnIds(catIds=query_cat_id) )
                query_imgs = coco.loadImgs( coco.getImgIds(catIds=query_cat_id) )
                
                
                freqs, bins, images = [], [], []
                for i in range(len(query_imgs)):        
        
                    # Sanity check for the annotation-image pair
                    if query_anns[i]["image_id"] != query_imgs[i]["id"]:
                        print("============")
                        print(query_anns[i]["image_id"])
                        print(query_imgs[i]["id"], query_imgs[i]["file_name"])
                        print("============")
                        exit(5)
                    
                    # Get mask
                    mask = coco.annToMask(query_anns[i])
                    
                    # Construct masked rgb image
                    rgb_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
                    rgb_mask[:,:,0] = rgb_mask[:,:, 0]*255 
                    rgb_image = cv2.imread( os.path.join("depth_analysis_data/data/rs/rgb", query_imgs[i]["file_name"]))
                    cv2.addWeighted(rgb_image, 0.65, rgb_mask, 0.35, 0, rgb_image)
                    
                    # Construct masked depth image
                    depth_img = cv2.imread(
                        os.path.join("depth_analysis_data/data/rs/depth", query_imgs[i]["file_name"]),
                        cv2.IMREAD_UNCHANGED
                        )
                    fish_pcd = depth_map_to_masked_pc(_img=depth_img, _mask=mask)
                    
                    fish_pcd = o3d.geometry.PointCloud.voxel_down_sample(fish_pcd, voxel_size=VOXEL_SIZE) 
                    #plane_model = estimate_plane(_img = depth_img)
                    height_profile = calculate_distances(plane_model, np.asarray(fish_pcd.points))
                    height_freqs, height_bins = np.histogram(height_profile, bins=bins_to_use, density=False)

                    freqs.append(height_freqs)
                    bins.append(height_bins)
                    images.append(rgb_image)

                for i in range(len(freqs)):
                    for j in range(i, len(freqs)):
                        if i != j:
                            emd_value = calculate_emd(freqs[i], bins[i], freqs[j], bins[j], normalize = True)
                            emd_values.append(emd_value)
                            emd_colors.append(FISH_COLOR_DICT[fish])
                                                    #(self, emd_value, freq1, bins1, freq2, bins2, fish, preset):
                            emd_data.append(EMDData(emd_value, freqs[i], bins[i], images[i], freqs[j], bins[j], images[j], fish, CONDITIONS_DICT[path]))
            
            # Build scatter plot for the preset
            ax_scatter.scatter([CONDITIONS_DICT[path]]*len(emd_values), emd_values, alpha = 0.25, c=emd_colors)
            # Preserve data for the box plot later
            box_plot_data.append(emd_values)

            # Image figure
            fig_img, (ax_img1, ax_img2) = plt.subplots(2)
            ax_img1.axis('off')
            ax_img2.axis('off')

            # Histogram figure
            fig, (ax_median, ax_max, ax_min) = plt.subplots(3)
            
            ax_median.set_xticks(bins_to_use)
            ax_median.tick_params(axis="x", labelsize = 3, labelrotation = 30)  

            ax_max.set_xticks(bins_to_use)
            ax_max.tick_params(axis="x", labelsize = 3, labelrotation = 30)  
            
            ax_min.set_xticks(bins_to_use)
            ax_min.tick_params(axis="x", labelsize = 3, labelrotation = 30)  
            
            # Median emd histogram
            query_emd = np.median(emd_values)
            query_idx = emd_values.index(query_emd)
            ax_median.set_title(emd_data[query_idx].fish + " emd=" + str(np.around(query_emd, 4)))
            ax_median.stairs(emd_data[query_idx].freq1/sum(emd_data[query_idx].freq1), 
                             emd_data[query_idx].bins1, 
                             fill=True, 
                             alpha=0.5)
            
            ax_median.stairs(emd_data[query_idx].freq2/sum(emd_data[query_idx].freq2), 
                             emd_data[query_idx].bins2, 
                             fill=True, 
                             alpha=0.5)

            # Max emd histogram
            query_emd = max(emd_values)
            query_idx = emd_values.index(query_emd)
            ax_max.set_title(emd_data[query_idx].fish + " emd=" + str(np.around(query_emd, 4)))
            ax_max.stairs(emd_data[query_idx].freq1/sum(emd_data[query_idx].freq1), 
                          emd_data[query_idx].bins1, 
                          fill=True, 
                          alpha=0.5)
            
            ax_max.stairs(emd_data[query_idx].freq2/sum(emd_data[query_idx].freq2),
                          emd_data[query_idx].bins2,
                          fill=True,
                          alpha=0.5)
            
            
            ax_img1.imshow(emd_data[query_idx].img1, interpolation='nearest')
            ax_img2.imshow(emd_data[query_idx].img2, interpolation='nearest')
            fig_img.supylabel(CONDITIONS_DICT[path]+"_max")
            fig_img.tight_layout()
            fig_img.savefig(os.path.join(OUTPUT_FOLDER, os.path.join(CONDITIONS_DICT[path])+"_max.png"))


            # Min emd histogram
            query_emd = min(emd_values)
            query_idx = emd_values.index(query_emd)
            ax_min.set_title(emd_data[query_idx].fish + " emd=" + str(np.around(query_emd, 4)))
            ax_min.stairs(emd_data[query_idx].freq1/sum(emd_data[query_idx].freq1), 
                          emd_data[query_idx].bins1, 
                          fill=True, 
                          alpha=0.5)
            
            ax_min.stairs(emd_data[query_idx].freq2/sum(emd_data[query_idx].freq2),
                          emd_data[query_idx].bins2,
                          fill=True,
                          alpha=0.5)
            
            ax_img1.imshow(emd_data[query_idx].img1, interpolation='nearest')
            ax_img2.imshow(emd_data[query_idx].img2, interpolation='nearest')
            fig_img.supylabel(CONDITIONS_DICT[path]+"_min")
            fig_img.tight_layout()
            fig_img.savefig(os.path.join(OUTPUT_FOLDER, os.path.join(CONDITIONS_DICT[path])+"_min.png"))

            # Save histogram figure
            fig.supylabel(CONDITIONS_DICT[path])
            fig.tight_layout()
            fig.savefig(os.path.join(OUTPUT_FOLDER, os.path.join(CONDITIONS_DICT[path])+".pdf"))
        
        #Build box plot
        ax_box.boxplot(box_plot_data)
        ax_box.set_xticks([1, 2, 3, 4], list(CONDITIONS_DICT.values()))
        ax_box.tick_params(axis="x", labelsize = 3, labelrotation = 30)        
        
        # Add legend to the scatter plot
        handlelist = [ax_scatter.plot([], marker="o", ls="", color=color)[0] for color in list(FISH_COLOR_DICT.values())]
        ax_scatter.legend(handlelist,list(FISH_COLOR_DICT.keys()), bbox_to_anchor=(1.1, 1), fontsize =5)
        
        # Save box and scatter plot figure
        fig_all.tight_layout()
        fig_all.savefig(os.path.join(OUTPUT_FOLDER, os.path.join("box_scatter_all_fish.pdf" )))

        # Save angles plot
        fig_angles.tight_layout()
        fig_angles.savefig(os.path.join(OUTPUT_FOLDER, os.path.join("angles_plot.pdf" )))


            

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