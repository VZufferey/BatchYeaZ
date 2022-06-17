# In case you only want to use the functionalities of the convolutional neural network and the segmentation,
# but not the full GUI, you only need the files in the same folder :
# `unet/model.py`,
# as well as the weights for the neural network which

# You can create predictions using the `prediction` function in `neural_network.py`
# (note that before making predictions, you have to use the function `equalize_adapthist` from `skimage.exposure` on the image).
# The segmentations can be obtained with the `segment` function in `segment.py`,
# and tracking between two frames is done using the `correspondence` function in `hungarian.py`.

#Python libraries import
#general
#import os
#import sys, time
from os import path, listdir

#images and data
#from PIL import Image, ImageSequence
import numpy
from numpy import asarray
from skimage import exposure, filters
import matplotlib.pyplot as plt

#UI
#from tkinter import filedialog
import PySimpleGUI as GUI

#bioformats for hyperstack management, requires javabridge
import javabridge as JB
import bioformats

#import of YeaZ modules (must be in the same folder as this script)
#from model import *
from neural_network import *
from segment import *
#from hungarian import *

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
        if extension==".hdf5":
            print("unet defined:", unet)
            return 1
        else:
            print("Unet path and file exists, but is not .Hdf5")
    else:
        print("unet does not exist")
        return 0

def checkInt(text):
        if text.isdigit():
            print("is integer")
            return 1
        else:
            print("is not integer")
            return 0

#vVARIABLE DEFINITION--> IDEALLY THROUGH USE INPUT THROUGH A SIMPLE GUI
# Dir = filedialog.askDirectory()
Dir = Dir0 = "/no   folder"
# unet_weights = filedialog.askopenfilename()    # Get neural network weights (IN COMMENT) and define default (for development) on the line below
unet_weights = unet_weights_0 = r"C:\Users\vzuffer1\OneDrive - Université de Lausanne\PhD VZ (OneDrive)\0-MANIPS\0-IMAGING\0_python_scripts\Batch YeaZ segmenter\unet_weights_fission_BF_multilab_basic_SJR_0_1_batchsize_10_Nepochs_500.hdf5"
ch_BF = 0                              # Default Bright-field channel index
z_BF = 0                               # default Z slice where Bright-field is present (starts at 0)

#Working folder definition single pop up (leave as comment, FOR DEBUG)
# Dir = filedialog.askDirectory()                              # request for a folder to work in
# if not len(Dir):                                             # check a Directory was entered
#         print("No file selected. interrupting script")
#         exit()
#Working folder definition single pop up (leave as comment, FOR DEBUG)

# GUI GUI GUI GUI GUI (PysimpleGUI)
GUI.theme('DarkBlue')
layout = [
            [GUI.Text("Select folder with .tif or .nd2 to segment")],
            [GUI.FolderBrowse("Folder", enable_events=True)],
            [GUI.FileBrowse("Neural network weights file (*unet*.hdf5)", enable_events=True)],
            [GUI.Text("\nBright-field", font="bold")],
            [GUI.Text("Channel"),   GUI.Input(key="channel",default_text=ch_BF, size=[5, 3], enable_events=True),
            GUI.Text("slice"),      GUI.Input(key="slice",default_text=z_BF, size=[5, 3], enable_events=True)],
            [GUI.Text("\n")],
            [GUI.Button("OK"), GUI.Button("Cancel")]
         ]
window = GUI.Window("Batch YeaZ", layout, size=(400, 250))

#GUI events definition
while True:
    event, values = window.read()
    if event == GUI.WIN_CLOSED or event == 'Cancel':
        print("Program closed")
        exit()

    if event == 'Folder':
        checkpath(Dir, Dir0)
        Dir = values['Folder']
        files = listdir(Dir)

    if event == 'Neural network weights file (*unet*.hdf5)':
        unet_weights = values['Neural network weights file (*unet*.hdf5)']
        checkUnet(unet_weights)

    if event == 'channel':
        if checkInt(values['channel']):
            ch_BF=values['channel']
            print("Bright-field set to channel #", ch_BF)
        else:
            print("specified channel is not a number")

    if event == 'slice':
        if checkInt(values['slice']):
            z_BF=values['slice']
            print("Bright-field set to slice #", z_BF)
        else:
            print("specified slice is not a number")

    if event == 'OK':
        print("Parameters defined")
        if checkpath(Dir, Dir0):
            window.close()
            break

DirOut=str(Dir+"/seg")                                      # make output Directory
if not os.path.exists(DirOut):
    os.makedirs(DirOut)
                                 # get file names
# post initialisation variable summary
print("Loaded neural network: ", unet_weights)
print("Bright-field slice # : ", z_BF)
print("Bright-field channel #: ", ch_BF)

#initialisations for 1. Java virtual machine and 2. image reader of the python-bioformats (python-bioformats 1.5.2)
JB.start_vm(class_path=bioformats.JARS)
#this code comes from https://forum.image.sc/t/python-bioformats-and-javabridge-debug-messages/12578/12, and is used to remove log message during execution
myloglevel="ERROR" # user string argument for logLevel.
rootLoggerName = JB.get_static_field("org/slf4j/Logger","ROOT_LOGGER_NAME", "Ljava/lang/String;")
rootLogger = JB.static_call("org/slf4j/LoggerFactory","getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
logLevel = JB.get_static_field("ch/qos/logback/classic/Level",myloglevel, "Lch/qos/logback/classic/Level;")
JB.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)

image_reader = bioformats.formatreader.make_image_reader_class()() # https://downloads.openmicroscopy.org/bio-formats/5.1.5/api/loci/formats/ImageReader.html

# initialisations for image displays
fig = plt.figure(1, figsize=(16, 4))  # figure definition (1x4 layout)
subplot1 = fig.add_subplot(1, 4, 1)
subplot2 = fig.add_subplot(1, 4, 2)
subplot3 = fig.add_subplot(1, 4, 3)
subplot4 = fig.add_subplot(1, 4, 4)
plt.ion()  # Interactive mode activation

#######################################################################################################################
# Loop over files
for file in files:                                                  # Loop through all files in folder
    sequence=[]
    print("\nChecking ["+file+"]")
    (filename, extension) = os.path.splitext(file)                  # Split our original filename into name and extension

    #OPEN and CHECK that file is an image file. IF YES, THEN PROCESS
    if extension == ".tif" or extension == ".nd2":
        try:                                                        # Attempt to open an image file
            print("["+filename+"] is ["+extension+"] -> Reading with bioformats...\n")
            #image reader definition, gathering & displaying hyperstack information
            image_reader.setId(Dir+"/"+file)
            Hyperstack_NC = image_reader.getSizeC()
            Hyperstack_NT = image_reader.getSizeT()
            Hyperstack_NZ = image_reader.getSizeZ()
            print("N channels: ", Hyperstack_NC, " // N frames: ", Hyperstack_NT, " // N slices: ", Hyperstack_NZ)
            print("Bright-field is expected on channel ", ch_BF)
        except IOError as e:                                        # Report error if cannot open
            print ("Problem opening", file, ":", e)
            continue                                                # skip to the next file if error
    else:
        print(filename+" is not .nd2 or .tif\nMoving to next file.\n")
        continue                                                    # skip to the next file if not .tif or .nd2

    print("--------------------\nPROCESSSING [" + filename + "] FOR YEAZ SEGMENTATION\n--------------------\n")

    # For each frame in image, do segmentation
    for t in range(Hyperstack_NT):
        print("--------------------\nProcessing frame ", t)
        fig.suptitle("[" + filename + "] - frame " + str(t))
        #___________IMAGE PROCESSING -> SEGMENTATION________________
        # read single image within hyperstack with python bioformats
        im = bioformats.load_image(Dir + "/" + file, c=ch_BF, z=z_BF,t=t)
        subplot1.imshow(im, cmap='gray')                            # show original image (should be Bright-field)

        # Here get channels colors, save them into a variable to re-apply them to the output file.
        print("TEST TEST TEST TEST:::::", image_reader.get16BitLookupTable())

        #YeaZ histogram equalization
        im_EQ = exposure.equalize_adapthist(im, clip_limit=0.03)
        print("Histogram equalization completed")

        #YeaZ Prediction image (CNN)
        pred = prediction(im_EQ, 1, pretrained_weights = unet_weights)
        subplot2.imshow(pred, cmap='gray')
        print("Prediction image completed")

        # Thresholding of prediction map: getting Th value with Otsu, and thersholding
        th_value=filters.threshold_otsu(pred)
        print("Otsu thresholding value: ", th_value)
        th_pred=pred>th_value
        subplot3.imshow(th_pred, cmap='gray')
        print("Thresholding of Prediction image completed")

        #SEGMENTATION MASK FROM THRESHOLDED PREDICTION :
        seg = segment(th_pred, pred, min_distance=10)
        subplot4.imshow(seg, cmap='gray')
        print("Watershed segmentation completed\n")
        seg=(seg*256).astype("uint16")
        print("asarray(seg).dtype", asarray(seg).dtype, "| numpy.amax(seg)", numpy.amax(seg))

        ## ---------END OF PROCESSING---------

        ## ---------Saving result images---------
        # 1. COMPOSITE: copy input images and add new channel to an output hyperstack
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
        # print("   ...Successful")

        # 2. single sequence of mask
        print("\nOutput1: Writing _maskSequence file (C=1, Z=1). Frame", t, "of", Hyperstack_NT)
        bioformats.write_image(DirOut+"/"+filename+"_maskSequence.tif",
                                seg,
                                bioformats.PT_UINT16,
                                c=0, z=0, t=t,
                                size_c=1,
                                size_z=1,
                                size_t=Hyperstack_NT)
        print("   ...Successful")

        plt.show()                  # shows the window for follow up of the segmentation process.
        plt.draw()                  # draw // refresh content
        plt.pause(0.2)              # very important to leave some time for display to be effective
        print("\nFRAME", t, "of [" + filename + "] PROCESSED")
        # HERE APPEND FRAMES TO FRAMES
    print("ALL FRAMES OF ["+filename+"] PROCESSED")
    # HERE REOPEN THE Stack (with another tool?) and set bands/channels LUT/colors

print("\nALL FILES PROCESSED")
plt.ioff()                                                      # Interactive mode deactivation
plt.show()                                                      # show window until closed by user REMOVE IN FULL BATCH
JB.kill_vm()
print("Batch YeaZ segmentation completed")