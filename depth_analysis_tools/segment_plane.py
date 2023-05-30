import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import cv2

# Camera params
img_w = 1920
img_h = 1080
fx = 1386.8350830078125 #fx
fy = 1385.3465576171875 #fy
cx = 928.3276977539062 #cx
cy = 537.0281982421875 #cy


def get_roi_mask():
    # Draw ROI mask
    corners = np.array([[640,21], #top left
                        [1830,20], #top right
                        [1845,1068], #bottom right
                        [655,1060]]) #bottom left

    mask = np.zeros((img_h,img_w), dtype='uint16')
    mask = cv2.fillPoly(mask, pts = [corners], color=(1))
    return mask

def depthmap2pointcloud(depth_map, apply_roi=True):
    # Apply mask if necessary
    mask = get_roi_mask()
    depth_map_masked = np.asarray(depth_map) * mask

    if(apply_roi):
        depth_map = depth_map_masked

    # Create pointcloud from masked depth map
    # NOTE: parsing the .json file would be better than hard-coded stuff...
    camera = o3d.camera.PinholeCameraIntrinsic(img_w, img_h, fx, fy, cx, cy)
    pcd = o3d.geometry.PointCloud.create_from_depth_image(o3d.geometry.Image(depth_map),
                                                          camera, np.identity(4),
                                                          depth_scale=1000.0,
                                                          depth_trunc=1000.0)

    return pcd

def remove_plane(_pcd, _dist_thres=0.015):
    # Downsample pointcloud
    downpcd = _pcd.voxel_down_sample(voxel_size=0.0025)


    # Fit plane
    plane_model, inliers = downpcd.segment_plane(distance_threshold=_dist_thres,
                                                 ransac_n=10,
                                                 num_iterations=1000)
    [a, b, c, d] = plane_model
    print(f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")

    # Select outliers / non-plane points
    outlier_cloud = downpcd.select_by_index(inliers, invert=True)
    #o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])
    return outlier_cloud

def cluster_points(_pcd, _eps=0.025, _points=100):
    # Cluster outliers
    labels = np.array(_pcd.cluster_dbscan(eps=_eps, min_points=_points))
    return labels

def cloud2pixels(_cloud):
    pts = np.array(_cloud.points)

    xs = pts[:,0]*1000
    ys = pts[:,1]*1000
    zs = pts[:,2]*1000

    u = ((xs) * (fx/zs)) + cx
    v = ((ys) * (fy/zs)) + cy
    return (u,v)

def update_mask(_mask, _pixels, _label):
    for i,_ in enumerate(_pixels[0]):
        curr_x = int(_pixels[0][i])
        curr_y = int(_pixels[1][i])
        _mask = cv2.circle(_mask, (curr_x, curr_y), 5, (int(_label)), -1)
    return _mask

def clusters2mask(_pcd, _labels, _num_clusters=-1):
    # Convert labels to list of pointclouds
    vals, counts = np.unique(_labels, return_counts=True)

    # Remove background label
    vals = vals[1:]
    counts = counts[1:]

    # Sort by biggest and limit to num_clusters
    biggest = np.argsort(counts)[::-1]
    biggest = biggest[:_num_clusters]

    # Loop through the biggest clusters
    mask = np.zeros((img_h,img_w))
    for i,b in enumerate(biggest):
        # Extract cluster from point cloud
        indices = np.argwhere(_labels == b).flatten()
        cluster_cloud = _pcd.select_by_index(indices)

        # Convert cloud to pixels
        us,vs = cloud2pixels(cluster_cloud)

        # Update depthmap
        label = i+1 # start counting from 1 as 0 = background
        mask = update_mask(mask, (us,vs), label)
    return mask


def process_img(_depth_map, _dist_thres):
    # Convert to pointcloud
    pcd = depthmap2pointcloud(_depth_map)

    # Remove plane
    pcd_non_plane = remove_plane(pcd, _dist_thres)

    # Try to cluster the non-plane points
    labels = cluster_points(pcd_non_plane)

    # Convert clusters to mask
    mask = clusters2mask(pcd_non_plane, labels, _num_clusters=10)

    print(np.unique(mask))

    # # Save mask
    # cv2.imwrite("mask.png", mask)

    # Save debug image
    #rgb_img = cv2.imread(_depth_path.replace("/depth/","/rgb/"))
    #plt.imshow(rgb_img)
    #plt.imshow(mask, alpha=0.3, cmap='gist_ncar')
    #plt.savefig("mask-overlaid.png")
    return mask

def process_img_from_path(_depth_path, _dist_thres):
    # Load depth map
    depth_map = o3d.io.read_image(_depth_path)

    return process_img(depth_map, _dist_thres)

if __name__ == "__main__":
    test_path = "../../data_depth_analysis/data/rs/depth/00002.png"

    #for i in np.arange(10):
    #    process_img(test_path, i)
