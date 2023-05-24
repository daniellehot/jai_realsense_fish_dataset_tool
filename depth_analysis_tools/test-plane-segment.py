import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import cv2

#pcd = o3d.io.read_point_cloud("rs/pc/00033.ply")


# Draw ROI mask
corners = np.array([[640,21], #top left
                    [1830,20], #top right
                    [1845,1068], #bottom right
                    [655,1060]]) #bottom left

mask = np.zeros((1080,1920), dtype='uint16')
mask = cv2.fillPoly(mask, pts = [corners], color=(1))

# Load
depth_map = o3d.io.read_image("../../data_depth_analysis/data/rs/depth/00001.png")
depth_map_masked = np.array(depth_map) * mask
depth_map_masked = o3d.geometry.Image(depth_map_masked)
pcd = o3d.geometry.PointCloud.create_from_depth_image(depth_map_masked,
                                                      o3d.camera.PinholeCameraIntrinsic(1280, 720, 644.921570, 644.921570, 638.844421, 363.089111),
                                                      np.identity(4),
                                                      depth_scale=1000.0, depth_trunc=1000.0)
o3d.visualization.draw_geometries([pcd])

# Downsample pointcloud
downpcd = pcd.voxel_down_sample(voxel_size=0.005)


# Fit plane
plane_model, inliers = downpcd.segment_plane(distance_threshold=0.01,
                                         ransac_n=3,
                                         num_iterations=1000)
[a, b, c, d] = plane_model
print(f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")

# Select inliers/outliers
inlier_cloud = downpcd.select_by_index(inliers)
inlier_cloud.paint_uniform_color([1.0, 0, 0])
outlier_cloud = downpcd.select_by_index(inliers, invert=True)
o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])

# Cluster outliers
with o3d.utility.VerbosityContextManager(
        o3d.utility.VerbosityLevel.Debug) as cm:
    labels = np.array(outlier_cloud.cluster_dbscan(eps=0.05, min_points=200, print_progress=True))

vals, counts = np.unique(labels, return_counts=True)

vals = vals[1:]
counts = counts[1:]
highest = np.argsort(counts)[::-1]

print(counts)
print(highest[:6])


max_label = labels.max()
print(f"point cloud has {max_label + 1} clusters")
colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
colors[labels < 0] = 0
outlier_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])
o3d.visualization.draw_geometries([outlier_cloud])
