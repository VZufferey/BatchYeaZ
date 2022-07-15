# read the instruction for python and conda install at Install python and conda 
# https://github.com/lpbsscientist/YeaZ-GUI


###### create an environment with 
# $ conda create --name BatchYeaZ python=3.6.8
# activate the environement with: $ conda activate BatchYeaZ 

###### and install packages with:
# $ pip install -r requirements.txt
#(you need to be located in the same folder as the requirement files. either use "cd" command to navigate or just type cmd in the explorator adress bar in windows)


# Then install manually the following packages using the following command lines

# conda install -c zacsimile python-bioformats


Execute the script using:
$ python batchyeaz.py

////////////////////////////////////////////////////////////////////////////////////////////////////////
PRELIMINARY INSTALLATION: Prepare Conda, and YeaZ scripts (Done By Valentin on june 2022)
# read the instruction to Install python and conda (Variable was added to path (in case, see variable_PATH.JPEG to reproduce))

////////////////////////////////////////////////////////////////////////////////////////////////////////
BatchYeaZ INSTALLATION
# Get model.py, neural_network.py and segment.py from YeaZ's Github (https://github.com/lpbsscientist/YeaZ-GUI) and place them in the BatchYeaZ folder 
# Open the console from within BatchYeaz location by typing "cmd" in the adress bar of the windows explorer
# then enter the following commands:

###### create an environment with the following command (these commands the conda variables was added to PATH, not explained here, already done)
$ conda create --name BatchYeaZ python=3.6.8
# the  environement can be activated with: 
$ conda activate BatchYeaZ
# or
$ activate BatchYeaZ

###### and install packages in the activated environemnent with:
$ pip install -r requirements.txt
# (you need to be located in the same folder as the requirement files: either use the "cd" command to navigate or just type "cmd" in the windows explorator's adress bar where you'd like to use the command lines)

# Then install  the following package manually using the following command lines
$ conda install -c zacsimile python-bioformats

////////////////////////////////////////////////////////////////////////////////////////////////////////
TO EXECUTE THE SCRIPT
# # Open the console from withnin BatchYeaz folder by typing "cmd" in the adress bar of the windows explorer
# then enter the follwing commands:

1: activate the corresponding environment 
$ conda activate BatchYeaz

2: launch the script:
$ python BatchYeaZ.py

At launch the following warning is displayed, and this is normal:
I tensorflow/core/platform/cpu_feature_guard.cc:142] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2