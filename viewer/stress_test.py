#what are testing for
    #create annotations X
    #move annotation X
    #remove annotation X
    #save X
    #remove previous save X
    #reset X

#keep track of simulated actions

import viewer
import cv2 as cv
import random as rnd
import numpy as np
import time
import schedule

MIN_ITERATIONS = 100
MAX_ITERATIONS = 500

def generate_annotations(viewer_inst):
    number_of_annotations = rnd.randint(10, 20)
    for i in range(number_of_annotations):
        coordinate = (
            np.random.randint(0, viewer_inst.resized_dim[0]), 
            np.random.randint(0, viewer_inst.resized_dim[1]), 
        )
        viewer_inst.coordinates.append( coordinate )
        viewer_inst.species.append( rnd.choice(["cod", "haddock", "hake", "whiting", "saithe"]) )
        viewer_inst.ids.append( str(rnd.randint(0, 100)) )
        viewer_inst.sides.append( rnd.choice(["L", "R"]) )

def move_annotation(viewer_inst):
    #rnd.choice(viewer_inst.coordinates)[0] += rnd.randint(-20, 20)
    #rnd.choice(viewer_inst.coordinates)[1] += rnd.randint(-20, 20)
    idx = rnd.randint(0, len(viewer_inst.coordinates)-1)
    viewer_inst.coordinates[idx] = (
        np.random.randint(0, viewer_inst.resized_dim[0]), 
        np.random.randint(0, viewer_inst.resized_dim[1]), 
    )

def remove_annotation(viewer_inst):
    idx_to_remove = np.random.randint(0, len(viewer_inst.coordinates))
    viewer_inst.coordinates.pop(idx_to_remove)
    viewer_inst.species.pop(idx_to_remove)
    viewer_inst.ids.pop(idx_to_remove)
    viewer_inst.sides.pop(idx_to_remove)


def save(viewer_inst):
    viewer_inst.saving = True
    viewer_inst.color = viewer_inst.mode_color_dict["saving"]
    viewer_inst.heatmapper.update(viewer_inst.img_cv)
    viewer_inst.save_data()
    viewer_inst.saving = False
    viewer_inst.color = viewer_inst.mode_color_dict[viewer_inst.mode]

def reset(viewer_inst):
    viewer_inst.coordinates.clear()
    viewer_inst.species.clear()
    viewer_inst.ids.clear()
    viewer_inst.sides.clear()

if __name__=="__main__":
    viewer.create_folders()
    viewer_stress = viewer.Viewer()
    
    # Test stats
    iteration = 0
    goal_iteration = rnd.randint(MIN_ITERATIONS, MAX_ITERATIONS)
    number_of_annotations = len(viewer_stress.coordinates)
    action = None
    events = [0, 0, 0, 0, 0, 0] #annotations_generated, move_annotation, remove_annotation, save_data, reset, remove_last
    generate_annotations(viewer_inst=viewer_stress)
    events[0] += 1

    try:
        viewer_stress.start_stream()
        while viewer_stress.jai_cam.Streaming and viewer_stress.rs_cam.Streaming:
            if not viewer_stress.saving:
                viewer_stress.retrieve_measures()

            if iteration < goal_iteration:
                if iteration % 100 == 0 and iteration != 0:
                    remove_annotation(viewer_inst=viewer_stress)
                    action = "remove_annotation"
                    events[2] += 1
                else:
                    move_annotation(viewer_inst=viewer_stress)
                    action = "move_annotation"
                    events[1] += 1

            if iteration == goal_iteration:
                save(viewer_inst=viewer_stress)
                action = "save_data"
                events[3] += 1
                
                reset(viewer_inst=viewer_stress)
                events[4] += 1

                if rnd.uniform(0, 1) > 0.75:
                    viewer_stress.remove_last()
                    action = "remove_last"
                    events[5] += 1
                
                generate_annotations(viewer_inst=viewer_stress)
                events[0] += 1
                number_of_annotations = len(viewer_stress.coordinates)
                iteration = 0
                goal_iteration = rnd.randint(MIN_ITERATIONS, MAX_ITERATIONS)
            
            print( "Iteration", iteration, "/", goal_iteration, "| Action", action, "| Number of annotations", number_of_annotations, "/", len(viewer_stress.coordinates))
            print("Annotations generated", events[0], 
                  "| Annotations moved", events[1], 
                  "| Annotations removed", events[2], 
                  "| Data saved", events[3],
                  "| Reset", events[4],
                  "| Data removed", events[5]
                  )

            viewer_stress.show()
            cv.waitKey(1)
            iteration += 1

        viewer_stress.jai_cam.CloseAndDisconnect()
        viewer_stress.rs_cam.close()

    except Exception as e:
        print("STRESS TEST: Error occurred, stopping streams and shutting down")
        print("   Streaming status Jai ", viewer_stress.jai_cam.Streaming)
        print("   Streaming status RealSense ", viewer_stress.rs_cam.Streaming)
        print("STRESS TEST: ", e)
        if viewer_stress.jai_cam.Streaming:
            viewer_stress.jai_cam.CloseAndDisconnect()
        if viewer_stress.rs_cam.Streaming:
            viewer_stress.rs_cam.close()