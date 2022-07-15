# In case you only want to use the functionalities of the convolutional neural network and the segmentation,
# but not the full GUI, you only need the files in the same folder :
# `unet/model.py`,
# as well as the weights for the neural network which

# You can create predictions using the `prediction` function in `neural_network.py`
# (note that before making predictions, you have to use the function `equalize_adapthist` from `skimage.exposure` on the image).
# The segmentations can be obtained with the `segment` function in `segment.py`,
# and tracking between two frames is done using the `correspondence` function in `hungarian.py`.

# Python libraries import
# general
# import os
# import sys, time
from os import path, listdir

# images and data
# from PIL import Image, ImageSequence
import numpy
from numpy import asarray
from skimage import exposure, filters
import matplotlib.pyplot as plt

# UI
# from tkinter import filedialog
import PySimpleGUI as GUI

# bioformats for hyperstack management, requires javabridge
import javabridge as JB
import bioformats

# import of YeaZ modules (must be in the same folder as this script)
from neural_network import *
from segment import *
# from hungarian import *

################################################
# FUNCTIONS
def checkpath(directory, default):
    if os.path.exists(directory):
        print("Folder defined:", directory)
        return 1
    elif directory == default:
        print("Please select a folder.")
        return 0
    else:
        print("Path does not exist")
        return 0

def checkUnet(unet):
    if os.path.exists(unet):
        (filename, extension) = os.path.splitext(unet)
        if extension == ".hdf5":
            print("unet defined:", unet)
            return 1
        else:
            print("Unet path and file exists, but is not .Hdf5")
    else:
        print("unet does not exist")
        return 0

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def checkInt(text):
    if text.isdigit():
        print("is integer")
        return 1
    else:
        print("is not integer")
        return 0
################################################

# VARIABLE DEFINITION--> IDEALLY THROUGH USE INPUT THROUGH A SIMPLE GUI
Dir = Dir0 = "/no folder"
ch_BF = 1  # Default Bright-field channel index
z_BF = 1  # default Z slice where Bright-field is present (starts at 0)
frame_start = 1
frame_end = "last"
suffix = "seg"
TH_modifier = 1
# unet_weights = filedialog.askopenfilename()    # (for development purpose) turn this line into comment and define default location with the line below
# unet_weights = unet_weights_0 = r"C:\Users\vzuffer1\OneDrive - Université de Lausanne\PhD VZ (OneDrive)\0-MANIPS\0-IMAGING\0_python_scripts\Batch YeaZ segmenter\unet_weights_fission_BF_multilab_basic_SJR_0_1_batchsize_10_Nepochs_500.hdf5"

## Working folder definition single pop up (leave as comment, FOR DEBUG)
# Dir = filedialog.askDirectory()                              # request for a folder to work in
# if not len(Dir):                                             # check a Directory was entered
#         print("No file selected. interrupting script")
#         exit()
## Working folder definition single pop up (leave as comment, FOR DEBUG)

### PysimpleGUI ###
GUI.theme('DarkBlue')
layout = [
    [GUI.Text("Select folder with .tif files to segment and a .hdf5 file with neural-Network parameters (unet)",
              font="bold")],
    [GUI.FolderBrowse("Folder", key='Folder', enable_events=True)],
    [GUI.FileBrowse("Neural network parameters", key='NN', enable_events=True)],
    [GUI.Text("\nSpecify Bright-field z-slice and channel number (starts with 1):", font="bold")],
    [GUI.Text("Channel"), GUI.Input(key="channel", default_text=ch_BF, size=[5, 3], enable_events=True),
     GUI.Text("slice"), GUI.Input(key="slice", default_text=z_BF, size=[5, 3], enable_events=True)],
    [GUI.Text("\nFrames to segment (starts with 1):", font="bold")],
    [GUI.Text("From"), GUI.Input(key="frame_start", default_text=frame_start, size=[5, 3], enable_events=True),
     GUI.Text("to "), GUI.Input(key="frame_end", default_text=frame_end, size=[5, 3], enable_events=True)],
    [GUI.Text("\nOtsu thresholding modifier (default = 1)", font="bold")], [GUI.Input(key="mod", default_text=TH_modifier, size=[5, 3], enable_events=True)],
    [GUI.Text("\nOutput filename suffix (modifier, start and end frame are automatically added to output) ", font="bold")],
    [GUI.Input(key="suffix", default_text=suffix, size=[20, 3], enable_events=True)],
    [GUI.Text("\n")],
    [GUI.Button("OK"), GUI.Button("Cancel")]
]
window = GUI.Window("Batch YeaZ", layout, size=(660, 490))

# GUI events definition
while True:
    event, values = window.read()

    if event == GUI.WIN_CLOSED or event == 'Cancel':
        print("Program closed")
        exit()

    if event == 'Folder':
        Dir = values['Folder']
        if checkpath(Dir, Dir0):
            files = listdir(Dir)

    if event == 'NN':
        unet_weights = values['NN']
        checkUnet(unet_weights)

    if event == 'channel':
        if checkInt(values['channel']):
            ch_BF = values['channel']
            print("Bright-field set to channel #", ch_BF)
        else:
            print("specified channel is not a number")

    if event == 'slice':
        if checkInt(values['slice']):
            z_BF = values['slice']
            print("Bright-field set to slice #", z_BF)
        else:
            print("specified slice is not a number")

    if event == 'frame_end' or event == 'frame_start':
        frame_start = values['frame_start']
        frame_end = values['frame_end']
        #
        if frame_start.isdigit():
            frame_start = int(float(frame_start))
            if frame_end.isdigit():  # START and END are DIGITS
                frame_end = int(float(frame_end))
                if frame_end < frame_start:  # correct end if smaller than start
                    frame_end = frame_start
                    print("frame_end cannot be smaller than frame_start.\nSegmentation will only be applied on frame",
                          frame_start)
                print("Segmentation from frame", frame_start, "to frame", frame_end)
            else:  # only START is DIGITS
                print("Segmentation from frame", frame_start, "to last frame")
        else:  # START is string
            frame_start = int(1)
            if frame_end.isdigit():  # START IS STRING; ENF IS DIGIT
                frame_end = int(float(frame_end))
                print("Segmentation from first frame to frame", frame_end)
            else:  # ALL STRINGS
                print("Segmentation on all frames")

    if event == 'mod':
        if isfloat(values['mod']):
            TH_modifier = float(values['mod'])
            print("Thresholing modifier set to", TH_modifier)
        else:
            print("Threshold modifier is not a number")

    if event == 'suffix':
        suffix = values['suffix']
        print("suffix defined as", suffix)

    if event == 'OK':
        print("Parameters defined")
        if checkpath(Dir, Dir0):
            window.close()
            break

DirOut = str(Dir + "/seg")  # make output Directory
if not os.path.exists(DirOut):
    os.makedirs(DirOut)

# post initialisation variable summary
print("Loaded neural network: ", unet_weights)
print("Bright-field slice # : ", z_BF)
print("Bright-field channel #: ", ch_BF)

# initialisations for 1. Java virtual machine
JB.start_vm(class_path=bioformats.JARS)

# this code comes from https://forum.image.sc/t/python-bioformats-and-javabridge-debug-messages/12578/12, and is used to remove log message during execution
myloglevel = "ERROR"  # user string argument for logLevel.
rootLoggerName = JB.get_static_field("org/slf4j/Logger", "ROOT_LOGGER_NAME", "Ljava/lang/String;")
rootLogger = JB.static_call("org/slf4j/LoggerFactory", "getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;",rootLoggerName)
logLevel = JB.get_static_field("ch/qos/logback/classic/Level", myloglevel, "Lch/qos/logback/classic/Level;")
JB.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)

#initialisation for the image reader from python-bioformats (python-bioformats 1.5.2), used to obtain metadata of images
image_reader = bioformats.formatreader.make_image_reader_class()()  # https://downloads.openmicroscopy.org/bio-formats/5.1.5/api/loci/formats/ImageReader.html

# initialisations for image displays
fig = plt.figure(1, figsize=(8, 8))  # figure definition (1x4 layout)
subplot1 = fig.add_subplot(2, 2, 1)
subplot2 = fig.add_subplot(2, 2, 2)
subplot3 = fig.add_subplot(2, 2, 3)
subplot4 = fig.add_subplot(2, 2, 4)
plt.ion()  # Interactive mode activation

#######################################################################################################################
# Loop over files
if len(files) > 0:
    for file in files:  # Loop through all files in folder
        print("\nChecking [" + file + "]")
        (filename, extension) = os.path.splitext(file)  # Split our original filename into name and extension

        # OPEN and CHECK that file is an image file. IF YES, THEN PROCESS
        if extension == ".tif" : # or extension == ".nd2": # if file is an image
            try:  # Attempt to open an image file
                print("[" + filename + "] is [" + extension + "] -> Reading with bioformats...\n")
                # image reader definition, gathering & displaying hyperstack information
                image_reader.setId(Dir + "/" + file)
                Hyperstack_NC = image_reader.getSizeC()
                Hyperstack_NZ = image_reader.getSizeZ()
                Hyperstack_NT = image_reader.getSizeT()

                if isinstance(frame_end, int): # if last frame value is a number, ...
                    if frame_end > Hyperstack_NT: # and if last frame value is bigger than the sequence length, ..
                        frame_end = Hyperstack_NT # adjust to last frame number
                elif isinstance(frame_end, str): # else, if last frame value is not a number,...
                    frame_end = int(Hyperstack_NT) # then set to int with the last frame number.

                print("N channels: ", Hyperstack_NC, " // N frames: ", Hyperstack_NT, " // N slices: ", Hyperstack_NZ)
                print("Bright-field is expected on channel ", ch_BF)
            except IOError as e:  # Report error if cannot open image
                print("Problem opening", file, ":", e)
                continue  # skip to the next file if error
        else:
            print(filename + " is not .nd2 or .tif\nMoving to next file.\n")
            continue  # skip to the next file if not .tif or .nd2

        print("--------------------\nPROCESSSING [" + filename + "] FOR YEAZ SEGMENTATION\n--------------------\n")
        # adjustment of channel and Z-slice number of Bright-field to start from 0
        ch_BF=int(ch_BF)-1
        z_BF=int(z_BF)-1
        # For each frame in image, do segmentation
        for t in range(frame_start-1, frame_end):
            print("--------------------\nProcessing frame ", t + 1)
            fig.suptitle("[" + filename + "] - frame " + str(t + 1))
            # ___________IMAGE PROCESSING -> SEGMENTATION________________
            # read single image within hyperstack with python bioformats
            im = bioformats.load_image(Dir + "/" + file, c=ch_BF, z=z_BF, t=t)
            subplot1.set_title("Bright-field")
            subplot1.imshow(im, cmap='gray')  # show original image (should be Bright-field)
            plt.show()

            # YeaZ histogram equalization
            im_EQ = exposure.equalize_adapthist(im, clip_limit=0.03)
            plt.draw()  # draw // refresh content
            plt.pause(0.2)  # very important to leave some time for display to be effective
            print("Histogram equalization completed")

            # YeaZ Prediction image (CNN)
            pred = prediction(im_EQ, 1, pretrained_weights=unet_weights)
            subplot2.set_title("predictions map")
            subplot2.imshow(pred, cmap='gray')
            plt.draw()  # draw // refresh content
            plt.pause(0.2)  # very important to leave some time for display to be effective
            print("Prediction image completed")

            # Thresholding of prediction map: getting Th value with Otsu, and thersholding
            th_value = filters.threshold_otsu(pred) * TH_modifier
            print("Otsu thresholding value: ", th_value, "*", TH_modifier)
            th_pred = pred > th_value
            subplot3.set_title("Thesholded predictions")
            subplot3.imshow(th_pred, cmap='gray')
            plt.draw()  # draw // refresh content
            plt.pause(0.2)  # very important to leave some time for display to be effective
            print("Thresholding of Prediction image completed")

            # MAKE MASK SEQUENCE FROM THRESHOLDED PREDICTION :
            seg = segment(th_pred, pred, min_distance=10)
            subplot4.set_title("Watershed")
            subplot4.imshow(seg, cmap='gray')
            plt.draw()  # draw // refresh content
            plt.pause(0.2)  # very important to leave some time for display to be effective
            print("Watershed segmentation completed\n")
            seg = (seg * 256).astype("uint16")
            # print("asarray(seg).dtype", asarray(seg).dtype, "| numpy.amax(seg)", numpy.amax(seg))

            ## ---------END OF PROCESSING---------
            ## ---------Saving result images---------

            # 1. COMPOSITE: copy input images/hyperstack and ADD a new channel in a newly created hyperstack.
            # un-comment to activate the function
            # print("\nOutput2: Writing output hyperstack & adding seg channel image for frame ", t)
            # for z in range(Hyperstack_NZ):                          #Copy hyperstack in new file
            #     if z == z_BF:
            #         for c in range(Hyperstack_NC):
            #                 print("   Copying channel ", c, ", slice", z, " of original image to _seg filec at frame", t)
            #                 temp_im = bioformats.load_image(Dir + "/" + file, c=c, z=z, t=t, rescale=False)
            #                 bioformats.write_image(DirOut+"/"+filename+"_seg.tif", temp_im, bioformats.PT_UINT16,
            #                                        c=c, z=z, t=t,
            #                                        size_c=Hyperstack_NC + 1,
            #                                        size_z=Hyperstack_NZ,
            #                                        size_t=Hyperstack_NT)
            #                 print("   ...Successful")
            # print("   Adding segmentation image in supplementary channel", Hyperstack_NC + 1, "and slice", z, "at T", t)
            # bioformats.write_image(DirOut + "/" + filename + "_seg.tif", seg, bioformats.PT_UINT16,
            #                        c=c+1, z=z_BF, t=t,
            #                        size_c=Hyperstack_NC + 1,
            #                        size_z=Hyperstack_NZ,
            #                        size_t=Hyperstack_NT)
            # print("   ...Successful") # still to solve: proper channel LUT (colors)

            # 2. single sequence of mask images
            print("\nOutput1: Writing _maskSequence file (C=1, Z=1). Frame", t + 1, "of", Hyperstack_NT)
            bioformats.write_image(DirOut + "/" + filename + "_" + suffix + "_Th" + str(TH_modifier)+ "_T" + str(frame_start) + "-T" + str(frame_end) + ".tif",
                                   seg,
                                   bioformats.PT_UINT16,
                                   c=0, z=0, t=t,
                                   size_c=1,
                                   size_z=1,
                                   size_t=Hyperstack_NT)
            print("   ...Successful")
        
            # plt.show()  # shows the window for follow up of the segmentation process.
            # plt.draw()  # draw // refresh content
            # plt.pause(0.2)  # very important to leave some time for display to be effective
            print("\nFRAME #", t + 1, "of [" + filename + "] PROCESSED")
        print("ALL DEFINED FRAMES OF [" + filename + "] PROCESSED")
        # HERE REOPEN THE Stack (with another tool?) and set bands/channels LUT/colors

    print("\nALL FILES PROCESSED")
    plt.ioff()  # Interactive mode deactivation
    plt.show()  # show window until closed by user REMOVE IN FULL BATCH
    JB.kill_vm()
    print("Batch YeaZ segmentation completed")
else:
    print("No files in defined folder")