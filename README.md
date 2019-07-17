# uGMRT-pipeline
This is a continuum data reduction pipeline for the Upgraded GMRT.
To run the pipeline:

casa -c ugmrt-pipeline-V17-uf.py

OR 

execfile("ugmrt-pipeline-V17-uf.py")

###########################################################################################

CAVEATS:

Absolute flux calibration:
Perley - Butler 2013 is hardcoded in the pipeline at the moment as it was tested in CASA 5.1 where more recent calibration coefficients are not available. 
If you would like to use Perley - Butler 2017, you may search and replace accordingly in the python code.

Primary beam correction:
The images produced by the pipeline are not corrected for the effect of the primary beam. You need to run the primary beam correction separately.

