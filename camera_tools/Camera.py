import numpy as np
import cv2
import glob
import argparse

class Camera():
# Based on:
# https://docs.opencv.org/4.5.5/dc/dbb/tutorial_py_calibration.html

    def __init__(self):
        self.square_size_mm = 40.0
        self.checker_size = (9,6)
        self.term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.cam_mat = None
        self.dist = None
        self.cam_mat_optim = None
        self.roi = None
        self.obj_pts = None
        self.img_pts = None

    def setup_obj_points(self):
        # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....
        obj_pts = np.zeros((self.checker_size[0]*self.checker_size[1],3), np.float32)
        obj_pts[:,:2] = np.mgrid[0:self.checker_size[0],0:self.checker_size[1]].T.reshape(-1,2)
        obj_pts *= self.square_size_mm
        return obj_pts

    def calc_reproj_error(self, obj_pts, img_pts, cam_mat, dist, Rs, ts):
        all_errors = []

        for i in np.arange(len(obj_pts)):
            img_pts_proj, _ = cv2.projectPoints(obj_pts[i], Rs[i], ts[i], cam_mat, dist)
            error = cv2.norm(img_pts[i], img_pts_proj, cv2.NORM_L2)/len(img_pts_proj)
            all_errors.append(error)
        return np.mean(np.array(all_errors))

    def undistort_img(self, img):
        # Undistort image
        img_undist = cv2.undistort(img, self.cam_mat, self.dist, None, self.cam_mat_optim)

        # Crop and return image
        x, y, w, h = self.roi
        return img_undist[y:y+h, x:x+w]


    def undistort_points(self, points):
        undist_pts = cv2.undistortPoints(points, self.cam_mat, self.dist, P=self.cam_mat_optim)

        # Correct for ROI after optimized camera matrix
        for i in np.arange(len(undist_pts)):
            undist_pts[i][0][0] -= self.roi[0]
            undist_pts[i][0][1] -= self.roi[1]

        return undist_pts

    # Based on:
    # https://answers.opencv.org/question/148670/re-distorting-a-set-of-points-after-camera-calibration/
    def redistort_points(self, points):
        pts = points.copy() # make sure not to overwrite original points

        # Undo ROI correction
        for i in np.arange(len(pts)):
            pts[i][0][0] += self.roi[0]
            pts[i][0][1] += self.roi[1]

        # Re-distort points
        pts_normalized = cv2.undistortPoints(pts, self.cam_mat_optim, None)
        pts_homo = cv2.convertPointsToHomogeneous(pts_normalized)
        rtemp = ttemp = np.array([0,0,0], dtype='float32')
        pts_dist, _ = cv2.projectPoints(pts_homo, rtemp, ttemp, self.cam_mat, self.dist)
        return pts_dist

    def calibrate(self, img_path, eval_error=False):
        # Prepare object points
        obj_pts = self.setup_obj_points()

        # Process all calibration images
        images = glob.glob(img_path + "*.png")

        all_obj_pts = []
        all_img_pts = []
        for p in images:
            print("Calibration - processing:")
            print(p)
            img = cv2.imread(p)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (self.checker_size[0],
                                                            self.checker_size[1]), None)

            # If found, add object points and image points (after refining them)
            if(ret):
                all_obj_pts.append(obj_pts)
                corners_sub = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), self.term_crit)
                all_img_pts.append(corners_sub)

        # Run the camera calibration
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(all_obj_pts, all_img_pts,
                                                           gray.shape[::-1], None, None)

        if(ret):
            self.cam_mat = mtx
            self.dist = dist
            #self.Rs = rvecs
            #self.ts = tvecs
            self.obj_pts = all_obj_pts
            self.img_pts = all_img_pts

            # Optimize (?) camera matrix
            h, w = img.shape[:2]
            self.cam_mat_optim, self.roi = cv2.getOptimalNewCameraMatrix(self.cam_mat,
                                                                         self.dist,
                                                                         (w,h), 1, (w,h))
            # Calc re-projection error if specified
            error = self.calc_reproj_error(all_obj_pts, all_img_pts, mtx, dist, rvecs, tvecs)
            print("Re-projection avg error: {0} pixels".format(error))

        return



if __name__ == "__main__": # Just for debugging purposes
    cal_images_path = "test-sample/jai/checkerboards/"

    # Test calibration
    cam = Camera()
    cam.calibrate(cal_images_path, eval_error=True)

    # Test undistort image
    img_path = "test-sample/jai/rgb/00017.png"
    img = cv2.imread(img_path)
    img_undist = cam.undistort_img(img)

    cv2.imwrite(img_path.replace(".png","_undist.png"), img_undist)

    # Test undistort / re-distort points
    img_path = "test-sample/jai/rgb/00017.png"
    img = cv2.imread(img_path)
    #pts = np.array([[[654.0, 1559.0]]]) # fish eye
    pts = np.array([[[1945.0, 28.0], # ruler eye
                     [654.0, 1559.0]]]) # fish eye
    pts_undist = cam.undistort_points(pts)
    print("org: ", pts)
    print("undistorted: ", pts_undist)
    print("re-distorted: ", cam.redistort_points(pts_undist))
