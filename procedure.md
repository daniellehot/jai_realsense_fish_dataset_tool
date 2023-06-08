# Procedure 
1. Prepare setup
2. Run *viewer/calibration.py*
3. Run *viewer/viewer.py*
4. Collect images 
5. Repeat from step 2 with every new group

## Prepare setup
* Place the conveyor belt on the work table such that the conveyor belt's sideguards and the upper right corner align with the work table. 
* Ensure that Jai Go lens is correctly configured - range ring is set to 1, aperture size is 11, which is the dot between 8 and 16.
* Place both cameras on the camera stand, clean camera lenses if necessary, move the stand on the work table, and align it with the marks on the side of the conveyor belt. Ensure the camera stand is firmly in place and its base is not wobbly. 
* Connect both cameras and the extra screen to the work laptop. 

## *calibration.py*
* This will launch the stream from both cameras. Jai's FOV should cover the entirety of the conveyor belt and a little of both side guards. RealSense's FOV should align with the outside sideguad of the conveyor belt.
* There is a counter of saved images in the upper right corner of the window. 20 to 30 images should be collected for each group to accurately estimate extrensic parameters between Jai Go and RealSense camera. 
* Images can be saved by pressing *s* key. The stream window is a composite image of both camera views, but images are saved separately. 
* A checkboard should be placed and oriented at various poses accross the image plane. 

## *viewer.py*
* This will launch the annotation software with the stream from both cameras. Jai's FOV should cover the entirety of the conveyor belt and a little of both side guards. RealSense's FOV should align with the outside sideguad of the conveyor belt. You can swich between streams by pressing *k* key. However, you can only annotate the Jai Go stream. 
* It is advisable to regularly check RealSense's FOV to ensure that the camera can still see everything required. 
* To annotate, click in the window, insert an annotation, and press OK. 
* There are three annotation modes, each identified with the color. When the annotations on the screen are red, you add annotations by clicking in the window. When yellow, you can move the already inserted annotations around. When blue, you can remove annotations. To change between modes, press *m* key. 
* You can visualise heatmaps of fish placement by pressing *h* key. This will overlap Jai Go stream with the heatmap, where the high heat represents the lack of motion in that area.  
* You can save by pressing *s* key. If you saved accidentaly, you can press *Z* key to remove the last saved image. 
* You can reset by pressing *R* key. This will remove all annotations. 
* To exit the software, press *Q* key. Exitting any other way will cause issues when relaunching the software.

## Collect images
* Each group has 66 images - 60 images with unlabelled fish and 6 images with labelled fish. An image with labelled fish should be taken whenever a new set of fish, or the same set placed on its other side, is put on the conveyor belt. 
* For every new image, all or majority of fish should be shuffled around. Use "yellow" annotation mode to move annotation around when shuffling fish. Heatmaps can help with visualising which fish have not been moved. However, the heatmaps are only updated after the image is saved. **IMPORTANT - FISH ARE NOT TO BE TURNED TO THEIR OTHER SIDE WHEN SHUFFLING.**
* When 66 images are collected, a new group of fish should be processed. Before you start with the new group, first, exit the annotation software by pressing *Q* key. Then, rename the current *data* folder to group number that was just processed. Finally. relaunch the annotation software, and start processing the new group of fish. If you forgot to rename the *data* folder, the annotation software will not start and instead it will exit with an error remainding you that the *data* folder already exists. Remember to regularly backup collected data. You can do so using the following command, or do it via GUI.

```
    # Move into the folder with the data folder
    cd /home/vap/jai_realsense_fish_dataset_tool/viewer

    # In case you have not yet renamed the data folder, rename it. group_1 is only a placeholder 
    mv data/ group_1

    # Copy the renamed data folder to the harddrive. 
    cp -r -v -n group_1 $HARDDRIVE
```

### Group preparation
Make sure all fish are somewhat thawn. Fish should be washed and made wet to better simulate an environment of a fishing vessel. Fish should be regularly sprayed with water to remain wet.  

A group is split into 2 parts, denoted as Half A and Half B. Fish are placed on the conveoyr belt with random side up, i.e. randly pick LEFT or RIGHT side. Fish should not all be placed with the same side up. One set of images consists of half + side. There are 6 sets:  
1. Half A, Side 1
2. Half B, Side 1
3. Half A+B, Side 1
4. Half A, Side 2
5. Half B, Side 2
6. Half A+B, Side 2
