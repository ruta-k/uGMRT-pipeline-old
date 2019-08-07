# CAPTURE: A CAsa Pipeline-cum-Toolkit for Upgraded Giant Metrewave Radio Telescope data REduction

# uGMRT-pipeline
This is a continuum data reduction pipeline for the Upgraded GMRT developed by Ruta Kale and Ishwara Chandra.

To use CAPTURE:

1. Open capture-V0.py in a text editor. Change and save the settings as per your requirements.

2. Run the pipeline using:

casa -c capture-V0.py
OR 

execfile("capture-V0.py")

############################################################################################
CAVEATS for CAPTURE V0:

Primary beam correction:
The images produced by the pipeline are not corrected for the effect of the primary beam. You need to run the primary beam correction separately.

############################################################################################
The early release version was ugmrt-pipeline-V17-uf.py (will not be updated anymore):

To use the older version:
1. Open ugmrt-pipeline-V17-uf.py in a text editor. Change and save the settings as per your requirements.

2. Run the pipeline using:

casa -c ugmrt-pipeline-V17-uf.py

OR 

execfile("ugmrt-pipeline-V17-uf.py")


###########################################################################################

CAVEATS for the older version:

Absolute flux calibration:
Perley - Butler 2013 is hardcoded in the pipeline at the moment as the pipeline was tested in CASA 5.1 where more recent calibration coefficients were not available. 
If you would like to use Perley - Butler 2017, you may search and replace accordingly in the python code. The speed of tclean is found to be compromised in more recent versions of CASA (e. g. 5.4.0 or 5.5.0).
A work around is to run the part up to calibration in CASA 5.5 and then use CASA 5.1.2 for the imaging and self-calibration part.

Primary beam correction:
The images produced by the pipeline are not corrected for the effect of the primary beam. You need to run the primary beam correction separately.

