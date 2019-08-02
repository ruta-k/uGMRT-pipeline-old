# uGMRT-pipeline
This is a continuum data reduction pipeline for the Upgraded GMRT developed by Ruta Kale and Ishwara Chandra.

To use the pipeline:
1. Open ugmrt-pipeline-V17-uf.py in a text editor and make the setting as per your requirements.

2. Run the pipeline using:

casa -c ugmrt-pipeline-V17-uf.py

OR 

execfile("ugmrt-pipeline-V17-uf.py")

###########################################################################################

CAVEATS:

Absolute flux calibration:
Perley - Butler 2013 is hardcoded in the pipeline at the moment as the pipeline was tested in CASA 5.1 where more recent calibration coefficients were not available. 
If you would like to use Perley - Butler 2017, you may search and replace accordingly in the python code. The speed of tclean is found to be compromised in more recent versions of CASA (e. g. 5.4.0 or 5.5.0).
A work around is to run the part up to calibration in CASA 5.5 and then use CASA 5.1.2 for the imaging and self-calibration part.

Primary beam correction:
The images produced by the pipeline are not corrected for the effect of the primary beam. You need to run the primary beam correction separately.

