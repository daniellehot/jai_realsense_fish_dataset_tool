from  pycocotools.coco import COCO
import matplotlib.pyplot as plt
import numpy as np
import cv2
import open3d as o3d

fp = "test-sample/saite-img27-img37.json"

depth_paths = ["test-sample/rs/depth/00027.png",
               "test-sample/rs/depth/00037.png"]


realsense_intrinsic = o3d.camera.PinholeCameraIntrinsic(1920, #width
                                                        1080, #height
                                                        1386.84, #fx
                                                        1385.35, #fy
                                                        928.33, #cx
                                                        537.03) #cy

for i,p in enumerate(depth_paths):
    # Load COCO annotations and prepare mask
    coco = COCO(fp)
    annIds = coco.getAnnIds()
    anns = coco.loadAnns(annIds)
    mask = coco.annToMask(anns[i])

    # Load depth image
    depth_img = cv2.imread(p, cv2.IMREAD_UNCHANGED)

    # Apply max depth threshold
    max_depth = 1200
    depth_img[depth_img > max_depth] = max_depth

    # Mask image and convert to open3d image
    masked_depth = depth_img * mask
    o3_image = o3d.geometry.Image(masked_depth)

    # Convert image to pointcloud
    pcd = o3d.geometry.PointCloud.create_from_depth_image(o3_image, realsense_intrinsic)

    # Downsample pointcloud
    downpcd = o3d.geometry.PointCloud.voxel_down_sample(pcd, voxel_size=0.0025)

    # Calculate surface normals
    o3d.geometry.PointCloud.estimate_normals(
        downpcd,
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.01, max_nn=30))


    o3d.geometry.PointCloud.orient_normals_to_align_with_direction(downpcd,
                                                                   orientation_reference=np.array([0.0,0.0,-1.0]))


    # Convert normals to np array
    normals_np = np.asarray(downpcd.normals)
    print(normals_np[:10,:])
    print(normals_np[:,0])

    # Calc dot product between plane normal and surface normals
    plane_n = np.array([0.0, 0.0, -1.0])
    dot_plane = normals_np.dot(plane_n)
    print(dot_plane[:10])

    # Try using nearest neighbour stuff
    pcd_tree = o3d.geometry.KDTreeFlann(downpcd)

    # idx 100 = tail
    # idx 1000 = on the fish
    test_idx = 100

    dot_products = []
    for p_idx in np.arange(len(downpcd.points)):
        test_idx = p_idx
        [k, idx, _] = pcd_tree.search_radius_vector_3d(downpcd.points[test_idx], 0.01)

        inlier_cloud = downpcd.select_by_index(idx)
        inlier_cloud.paint_uniform_color([0.0, 1.0, 0.0])

        plane_n = np.asarray(downpcd.normals[test_idx])
        normals_np = np.asarray(inlier_cloud.normals)
        dot_plane = normals_np.dot(plane_n)
        dot_plane = np.abs(dot_plane) # crap fix! shouldn't be needed!!
        dot_products.append(np.min(dot_plane))

    # Note: press 'n' to display surface normals
    o3d.visualization.draw_geometries([downpcd, inlier_cloud])


    # Show histogram of calculated dot product
    #all_dot_products = np.concatenate(dot_products).ravel()
    #all_dot_products = np.array(dot_products)
    print(dot_products)
    all_dot_products = dot_products
    plt.hist(all_dot_products, bins=36, alpha=0.6, density=True, label='{0}'.format(p))


plt.legend()
plt.show()
