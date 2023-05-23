import numpy as np
import cv2
import argparse

from Camera import Camera

class CameraMapper():
    def __init__(self):
        self.mappings = {}
        self.cameras = {}


    def add_camera(self, cam, label):
        self.cameras[label] = cam

    def create_mapping(self, from_cam, to_cam):
        src_cam = self.cameras[from_cam]
        dst_cam = self.cameras[to_cam]

        # Prepare the undistorted image points
        src_pts_corr = src_cam.undistort_points(np.array(src_cam.img_pts[0]))
        dst_pts_corr = dst_cam.undistort_points(np.array(dst_cam.img_pts[0]))

        # Calculate homography
        homo, inliers = cv2.findHomography(src_pts_corr, dst_pts_corr)
        # NOTE: USING THE IMG PTS FROM THE ALL CHECKERBOARDS ARE MAYBE NOT THE BEST CHOICE
        # AS THEY ARE NOT ENTIRELY FLAT I.E. IN THE SAME PLANE!!
        # MAYBE JUST USE ONE CHECKERBOARD LAYING FLAT ON THE CONVYER?!?

        # Add homography to mapping dict
        if(from_cam not in self.mappings):
            self.mappings[from_cam] = {}
        self.mappings[from_cam][to_cam] = homo


    def map_points(self, pts, from_cam, to_cam):
        # Check if to / from camera exists
        for cam in [from_cam, to_cam]:
            if(cam not in self.cameras):
                print("Mapping points error - camera {0} not found!".format(cam))
                return

        # Check if mapping exists
        try:
            mapping = self.mappings[from_cam][to_cam]
        except:
            # Create mapping because it is missing
            print("Missing mapping: {0} --> {1}".format(from_cam, to_cam))
            print(" - creating it and trying again!")
            self.create_mapping(from_cam, to_cam)
            mapping = self.mappings[from_cam][to_cam]


        # Apply mapping
        pts_undist = self.cameras[from_cam].undistort_points(pts)
        pts_mapped = cv2.perspectiveTransform(pts_undist, mapping)
        pts_redist = self.cameras[to_cam].redistort_points(pts_mapped)
        return pts_redist



def draw_points(img_path, pts):
    if(pts.shape[0] == 1):
        pts = np.transpose(pts, axes=[1,0,2])

    img = cv2.imread(img_path)
    print("point to draw!")
    print(np.array(pts).shape)

    circle_radius = int((img.shape[0]/1000.0)*5.0)

    for p in pts:
        print(p)
        img = cv2.circle(img, (int(p[0][0]), int(p[0][1])), circle_radius, (0,255,0), -1)
    cv2.imwrite(img_path.replace(".png", "_points.png"), img)


if __name__ == "__main__": # Just for debugging purposes
    # Prepare cameras
    jai_cam = Camera()
    jai_cam.calibrate("test-sample/jai/checkerboards/", eval_error=True)

    rs_cam = Camera()
    rs_cam.calibrate("test-sample/rs/checkerboards/", eval_error=True)

    # Setup camera mapper
    cam_mapper = CameraMapper()
    cam_mapper.add_camera(jai_cam, "jai")
    cam_mapper.add_camera(rs_cam, "rs")


    # Test mapping jai --> rs
    # for image 17
    jai_pts = np.array([[[655.0, 1556.0], # fish eyes
                         [677.0, 944.0],
                         [817.0, 1107.0],
                         [1323.0, 583.0],
                         [1228.0, 1398.0],
                         [1782.0, 1122.0],
                         [2073.0, 1531.0]]])

    rs_pts = cam_mapper.map_points(jai_pts, "jai", "rs")
    draw_points("test-sample/jai/rgb/00017.png", jai_pts)
    draw_points("test-sample/rs/rgb/00017.png", rs_pts)
    print(rs_pts)



    # Test mapping rs --> jai
    # for image 21
    rs_pts = np.array([[[624.0, 372.0], # fish eyes
                        [805.0, 458.0],
                        [903.0, 230.0],
                        [1048.0, 295.0],
                        [1147.0, 482.0],
                        [1276.0, 514.0],
                        [1397.0, 590.0]]])

    jai_pts = cam_mapper.map_points(rs_pts, "rs", "jai")
    draw_points("test-sample/jai/rgb/00021.png", jai_pts)
    draw_points("test-sample/rs/rgb/00021.png", rs_pts)
    print(jai_pts)
