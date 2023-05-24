import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import cv2

def depthmap2pointcloud(depth_map, apply_roi=True):
    h,w = np.asarray(depth_map).shape

    # Draw ROI mask
    corners = np.array([[640,21], #top left
                        [1830,20], #top right
                        [1845,1068], #bottom right
                        [655,1060]]) #bottom left

    mask = np.zeros((h,w), dtype='uint16')
    mask = cv2.fillPoly(mask, pts = [corners], color=(1))

    # Apply mask if necessary
    depth_map_masked = np.asarray(depth_map) * mask

    if(apply_roi):
        depth_map = depth_map_masked

    # Create pointcloud from masked depth map
    # NOTE: parsing the .json file would be better than hard-coded stuff...
    camera = o3d.camera.PinholeCameraIntrinsic(w, h,
                                               1386.8350830078125, #fx
                                               1385.3465576171875, #fy
                                               928.3276977539062, #cx
                                               537.0281982421875) #cy

    pcd = o3d.geometry.PointCloud.create_from_depth_image(o3d.geometry.Image(depth_map), camera, np.identity(4),
                                                         depth_scale=1000.0, depth_trunc=1000.0)

    return pcd

def fit_plane(pcd):
    # Downsample pointcloud
    downpcd = pcd.voxel_down_sample(voxel_size=0.005)

    # Fit plane
    plane_model, inliers = downpcd.segment_plane(distance_threshold=0.01,
                                                 ransac_n=3,
                                                 num_iterations=1000)
    [a, b, c, d] = plane_model
    print(f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")
    return plane_model, inliers


def eval_plane(plane, inliers):
    # Select inliers/outliers
    inlier_cloud = downpcd.select_by_index(inliers)
    inlier_cloud.paint_uniform_color([1.0, 0, 0])
    outlier_cloud = downpcd.select_by_index(inliers, invert=True)
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])

# # Cluster outliers
# with o3d.utility.VerbosityContextManager(
#         o3d.utility.VerbosityLevel.Debug) as cm:
#     labels = np.array(outlier_cloud.cluster_dbscan(eps=0.05, min_points=200, print_progress=True))

# vals, counts = np.unique(labels, return_counts=True)

# vals = vals[1:]
# counts = counts[1:]
# highest = np.argsort(counts)[::-1]

# print(counts)
# print(highest[:6])


# max_label = labels.max()
# print(f"point cloud has {max_label + 1} clusters")
# colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
# colors[labels < 0] = 0
# outlier_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])
# o3d.visualization.draw_geometries([outlier_cloud])

if __name__ == "__main__":
    presets = {"default":(2,11),
               "default-back":(12,21),
               "acc-back":(22,31),
               "acc":(32,41)}

    fig = plt.figure(figsize=(12,8))
    for i,k in enumerate(presets.keys()):
        preset_name = k
        img_range = presets[k]

        indices = np.arange(img_range[0], img_range[1]+1)
        paths = ["../../data_depth_analysis/data/rs/depth/{:05d}.png".format(i) for i in indices]

        print("Preset: ", k)
        print(paths)

        xs = []
        ys = []
        zs = []
        ds = []
        for f_path in paths:
            depth = o3d.io.read_image(f_path)
            pcd = depthmap2pointcloud(depth)
            #o3d.visualization.draw_geometries([pcd])

            plane, inliers = fit_plane(pcd)
            [a, b, c, d] = plane
            xs.append(a)
            ys.append(b)
            zs.append(c)
            ds.append(d)


        plt.subplot(4, 1, 1)
        plt.scatter([i]*len(xs), xs, label=preset_name)

        plt.subplot(4, 1, 2)
        plt.scatter([i]*len(ys), ys, label=preset_name)

        plt.subplot(4, 1, 3)
        plt.scatter([i]*len(zs), zs, label=preset_name)

        plt.subplot(4, 1, 4)
        plt.scatter([i]*len(ds), ds, label=preset_name)
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.tight_layout()
    plt.show()
#        fig1, ax1 = plt.subplots()
#        ax1.set_title('Basic Plot')
#        ax1.boxplot(xs)
#        plt.show()

        #plt.hist(xs)
        #plt.show()
