# CAPTURE: A CAsa Pipeline-cum-Toolkit for Upgraded Giant Metrewave Radio Telescope data REduction

# uGMRT-pipeline
This is a continuum data reduction pipeline for the Upgraded GMRT developed by Ruta Kale and Ishwara Chandra. It has been tested on bands 3, 4 and 5 of the uGMRT and 325, 610 and 1400 MHz bands of the legacy GMRT. uGMRT Band 2 data can also be reduced with minor modification to the pipeline - interested users can get in touch with me for that. 

To use CAPTURE:

1. Open capture-pipeline-V0.py in a text editor. Change and save the settings as per your requirements.

2. Run the pipeline using:

casa -c capture-pipeline-V0.py
OR 

execfile("capture-pipeline-V0.py")

############################################################################################
CAVEATS for CAPTURE V0:

Primary beam correction:
The images produced by the pipeline are not corrected for the effect of the primary beam. You need to run the primary beam correction separately.



