////////////////////////////////////////////////////////////////////////////////////////////////////////
PRELIMINARY INSTALLATION: Conda -> Python
# to Install python and conda (Variable was added to path (in case, see variable_PATH.JPEG to reproduce))
# Instructions are available on YeaZ repository (https://github.com/lpbsscientist/YeaZ-GUI) 
# (Done by Valentin on jun 2022)

////////////////////////////////////////////////////////////////////////////////////////////////////////
BatchYeaZ INSTALLATION
# Dependency on YeaZ: Get model.py, neural_network.py and segment.py from YeaZ's Github (https://github.com/lpbsscientist/YeaZ-GUI) and place them in the BatchYeaZ folder 
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

at launch the following warning is displayed, and this is normal:
