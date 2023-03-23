import cv2 as cv 
import os 
import pyrealsense2 as rs
import numpy as np
import open3d as o3d

class RS_Camera():
    def __init__(self):
        self.color_width = 1920 #1920
        self.color_height = 1080 #1080
        self.color_format = rs.format.bgr8 #REMEMBER TO SWITCH COLUMNS OF THE COLOR IMAGE BEFORE ADDING COLOR TO A POINT CLOUD 
        self.depth_width = 1280
        self.depth_height = 720
        self.depth_format = rs.format.z16
        self.fps = 15

        #self.decimation_f = rs.decimation_filter()
        self.depth_min = 0.5
        self.depth_max = 8.0
        self.threshold_f = rs.threshold_filter(self.depth_min, self.depth_max)
        self.spatial_f = rs.spatial_filter()
        self.temporal_f = rs.temporal_filter()
        self.depth_to_disparity = rs.disparity_transform(True)
        self.disparity_to_depth = rs.disparity_transform(False)

    def start_stream(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, self.color_width, self.color_height, self.color_format, self.fps)
        config.enable_stream(rs.stream.depth, self.depth_width, self.depth_height, self.depth_format, self.fps)
        self.profile = self.pipeline.start(config)
        self.set_sensor_settings()
        self.align = rs.align(rs.stream.color)

        for i in range(15):
            if i==0:
                print("Waiting for auto-exposure to settle")
            self.pipeline.wait_for_frames()
    
    def set_sensor_settings(self):
        sensors = self.profile.get_device().query_sensors()
        for sensor in sensors:
            if sensor.is_depth_sensor():
                sensor.set_option(rs.option.enable_auto_exposure, True) 
                sensor.set_option(rs.option.laser_power, 360.0)
                sensor.set_option(rs.option.emitter_enabled, 1)
            if sensor.is_color_sensor():
                sensor.set_option(rs.option.exposure, 3000.0)
                sensor.set_option(rs.option.gain, 0.0)
                sensor.set_option(rs.option.brightness, 0.0)
                sensor.set_option(rs.option.contrast, 50.0)
                sensor.set_option(rs.option.gamma, 300.0)
                sensor.set_option(rs.option.hue, 0.0)
                sensor.set_option(rs.option.saturation, 50.0)
                sensor.set_option(rs.option.sharpness, 100.0)
                sensor.set_option(rs.option.white_balance, 4200.0)

    def get_data(self):
        ''' In case we want to use temporal filtering
        frames = []
        for i in range(10):
            aligned_frameset = self.align.process(self.pipeline.wait_for_frames())
            frames.append(aligned_frameset)
        
        for x in range(10):
            frame = frames[x]
            frame = self.depth_to_disparity.process(frame)
            frame = self.spatial.process(frame)
            frame = self.temporal.process(frame)
            frame = self.disparity_to_depth.process(frame)
        '''

        aligned_frames = self.align.process(self.pipeline.wait_for_frames())
        self.color_frame = aligned_frames.get_color_frame()
        self.img = np.asanyarray(self.color_frame.get_data())     

        self.depth_frame = aligned_frames.get_depth_frame()
        self.depth_frame = self.threshold_f.process(self.depth_frame)
        self.depth_frame = self.depth_to_disparity.process(self.depth_frame)
        self.depth_frame = self.spatial_f.process(self.depth_frame)
        self.depth_frame = self.disparity_to_depth.process(self.depth_frame)
        self.pointcloud = self.get_colored_pointcloud()
    
    def get_colored_pointcloud(self):
        pc = rs.pointcloud()
        pc.map_to(self.color_frame)
        points = rs.points()
        points = pc.calculate(self.depth_frame)

        v = points.get_vertices()
        verts = np.asarray(v).view(np.float32).reshape((-1, 3))

        t = points.get_texture_coordinates()
        tex_coords = np.asarray(t).view(np.float32).reshape((-1, 2))

        u = (tex_coords[:, 0] * self.color_width + 0.5).astype(np.uint32)
        np.clip(u, 0, self.color_width-1, out=u)
        v = (tex_coords[:, 1] * self.color_height + 0.5).astype(np.uint32)
        np.clip(v, 0, self.color_height-1, out=v)
        
        color_img_normalized = self.normalize(self.img)
        pc_colors = color_img_normalized[v, u]

        pc_colored = o3d.geometry.PointCloud()
        pc_colored.points = o3d.utility.Vector3dVector(verts)
        pc_colored.colors = o3d.utility.Vector3dVector(pc_colors)
        return pc_colored
        
    def normalize(self, x):
        return x.astype(float)/255
    
    def save_data(self):
        #cv.imwrite("test.bmp", self.img)
        cv.imwrite("test.png", self.img, [cv.IMWRITE_PNG_COMPRESSION, 0])
        o3d.io.write_point_cloud("pc.ply", self.pointcloud)        


if __name__=="__main__":
    import time 
    realsense = RS_Camera()
    realsense.start_stream()

    print("Sleeping for 5 seconds")
    time.sleep(5)

    realsense.get_data()
    print("Saving data")
    realsense.save_data()
    
        

