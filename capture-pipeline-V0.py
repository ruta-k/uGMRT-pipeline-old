###################################################################
# CAPTURE: CAsa Pipeline-cum-Toolkit for Upgraded GMRT data REduction
###################################################################
# Pipeline for analysing data from the GMRT and the uGMRT.
# Combination of pipelines done by Ruta Kale based on pipelines developed independently by Ruta Kale 
# and Ishwar Chandra.
# Date: 8th Aug 2019
# README : Please read the following instructions to run this pipeline on your data
# Files and paths required
# 0. This script should be placed and executed in the directory where your data files are located.
# 1. If starting from lta file, please provide the paths to the listscan and gvfits binaries in "gvbinpath" as shown.
# 2. Keep the vla-cals.list file in the same area.
# 3. The settings True/False at the beginning are relevant for processing the file from a given stage.
# 4. Below these there are inputs to be set for your data.
# 5. You will not need to change anything below the Inputs block under normal circumstances.
# 6. You will have self-calibrated image of your target source at the end of the pipeline.
# Please email ruta@ncra.tifr.res.in if you run into any issue and cannot solve.
# 
###### SET THE STAGE FOR DATA ANALYSIS #############################
fromlta = False                               # If starting from lta file set it True. Provide the lta file name and check that the gvfits binaries are given properly.
gvbinpath = ['./listscan','./gvfits']   # set the path to listscan and gvfits
fromraw = True                               # True if starting from FITS data. Otherwise keep it False.
fromms = True                                # True If working with multi-source MS file.
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
findbadants = True                           # find bad antennas when True
flagbadants= True                           # find and flag bad antennas when True
findbadchans = True                          # find bad channels within known RFI affected freq ranges when True
flagbadfreq= True                            # find and flag bad channels within known RFI affected freq ranges when True
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
myflaginit = True                             # True to flag first channel, quack, initial clips
doinitcal = True                              # True to calibrate data
mydoflag = True                               # True to flag on the calibrated data
redocal = True                               # True to redo calibration - recommended
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
dosplit = True                                # True to split calibrated data on target source
mysplitflag = True                            # True to flag on the target source
dosplitavg = True                             # True to average channels - set mywidth2 input below to choose how many channels to average
doflagavg = True                              # True to flag on the channel averaged file  
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
makedirty = False                             # True only if you want to make a dirty image of your target source; you can do this before proceeding to self-calibration to check the field
doselfcal = True                              # True if selfcal loop should be run: set inputs below regarding how many iterations you want.
usetclean = True                              # True if you want to use tclean (recommended); False will use clean.
####################################################################
# Please provide appropriate inputs below. No defaults.
###### INPUTS ######################################################
ltafile =''                         # Provide the name of the lta file
rawfile = '1543+480.FITS'                         # Provide the name of the FITS file if you already have; 
                                              # NOTE: It should be TEST.FITS if you are choosing to start from lta file and proceeding to next steps using this script.
myfile1 ='multi.ms'                                   # Provide the name for the MS file 
mysplitfile =''                               # You need to provide this if you are starting from the step after splitting
mysplitavgfile = ''                           # You need to provide this if you are starting from the step after splitting and averaging
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Inputs for flagging steps
myquackinterval = 10.0                        # time in s to flag at the beginning of a scan and at the end of the scan.
# calibration
myrefant = 'C00'                              # choose a reference antenna - make sure it is one of the working antennas.
uvracal =''                                   # Leave it to '' - should work in most cases
# Clip levels for flagging : change depending on what you expect
clipfluxcal =[0.0,60.0]                       # typically twice the expected flux; only to remove high points
clipphasecal =[0.0,60.0]                      # typically twice the expected flux; only to remove high points
cliptarget =[0.0,30.0]                        # typically four times the expected flux; only to remove high points
clipresid=[0.0,10.0]                          # 10 times the rms for single channel and single baseline
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Inputs for post split averaging of channels
mywidth2 = 10                                 # number of channels to average - choose aptly to avoid bandwidth smearing.
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Inputs for imaging and self-calibration : You will need to change relevant advanced controls if you change the values here.
mycell = ['0.5arcsec']                         # Set the cellsize: for 610 MHz 0.5 or 1.0 arcsec, for 325 MHz 1.0 or 2.0 arcsec, 0.3 or 0.5 arcsec for 1.4 GHz will work.
myimsize = [5000]                              # Set the size of the image in pixel units. Should cover the primary beam.
scaloops = 8                                   # Total number of self-cal loops (including both phase-only and amp-ph)
mythresholds = 0.01                            # A starting thereshold in mJy- will reduce with scal iterations.              
mypcaloops = 4                                 # Number of p-only selfcal loops; should be <= scaloops. The remaning loops will be a&p self-cal.
mysolint2 = ['8.0min','4.0min','2.0min','1.0min','8.0min','4.0min','2.0min','1.0min']   # Solint used for self-cal: provide solints for each self-cal iteration : edit if scaloops changed. 
##################################################################
# For advanced control, you may modify the following inputs to the tasks. However you could go ahead without modifying these.
##################################################################
mynterms = 2                                   # This is the nterms used in tclean. For uGMRT this needs to be 2 at least. A larger value implies very slow imaging.
mywproj2 = -1                                  # Number of wprojection planes- leave it to -1 so that it is determined internally in tclean
uvrascal=''                                    # uvrange cutoff used in self-calibration (Not tested enough.)
#######################################################################################################################
# You can choose to not change anything below this line if you are not familiar with this pipeline.
########################################################################################################################
target = True                                # Should be True when a target different from calibrators is being imaged. Leave it to true always.
##################################################################
# FUNCTIONS
###############################################################
# A library of function that are used in the pipeline

def vislistobs(msfile):
	'''Writes the verbose output of the task listobs.'''
	os.system('rm '+msfile+'.list')
	ms.open(msfile)  
	outr=ms.summary(verbose=True,listfile=msfile+'.list')
	print "A file containing listobs output is saved."
	return outr

def getfields(msfile):
	'''get list of field names in the ms'''
	msmd.open(msfile)  
	fieldnames = msmd.fieldnames()
	msmd.done()
	return fieldnames

def getscans(msfile, mysrc):
	'''get a list of scan numbers for the specified source'''
	msmd.open(msfile)
	myscan_numbers = msmd.scansforfield(mysrc)
	myscanlist = myscan_numbers.tolist()
	msmd.done()
	return myscanlist

def getantlist(myvis,scanno):
	msmd.open(myvis)
	antenna_name = msmd.antennasforscan(scanno)
	antlist=[]
	for i in range(0,len(antenna_name)):
		antlist.append(msmd.antennanames(antenna_name[i])[0])
	return antlist


def getnchan(msfile):
	msmd.open(msfile)
	nchan = msmd.nchan(0)
	msmd.done()
	return nchan


def freq_info(ms_file):									
	sw = 0
	msmd.open(ms_file)
	freq=msmd.chanfreqs(sw)								
	msmd.done()
	return freq									

def makebl(ant1,ant2):
	mybl = ant1+'&'+ant2
	return mybl


def getbllists(myfile):
	myfields = getfields(myfile)
	myallscans =[]
	for i in range(0,len(myfields)):
		myallscans.extend(getscans(myfile, myfields[i]))
	myantlist = getantlist(myfile1,int(myallscans[0]))
	allbl=[]
	for i in range(0,len(myantlist)):
		for j in range(0,len(myantlist)):
			if j>i:
				allbl.append(makebl(myantlist[i],myantlist[j]))
	mycc=[]
	mycaa=[]
	for i in range(0,len(allbl)):
		if allbl[i].count('C')==2:
			mycc.append(allbl[i])
		else:
			mycaa.append(allbl[i])
	myshortbl =[]
	myshortbl.append(str('; '.join(mycc)))
	mylongbl =[]
	mylongbl.append(str('; '.join(mycaa)))
	return myshortbl, mylongbl

def myvisstatampraw1(myfile,myfield,myspw,myant,mycorr,myscan):
	default(visstat)
	mystat = visstat(vis=myfile,axis="amp",datacolumn="data",useflags=False,spw=myspw,
		field=myfield,selectdata=True,antenna=myant,uvrange="",timerange="",
		correlation=mycorr,scan=myscan,array="",observation="",timeaverage=False,
		timebin="0s",timespan="",maxuvwdistance=0.0,disableparallel=None,ddistart=None,
		taql=None,monolithic_processing=None,intent="",reportingaxes="ddid")
	mymean1 = mystat['DATA_DESC_ID=0']['mean']
	return mymean1

def myvisstatampraw(myfile,myspw,myant,mycorr,myscan):
	default(visstat)
	mystat = visstat(vis=myfile,axis="amp",datacolumn="data",useflags=False,spw=myspw,
		selectdata=True,antenna=myant,uvrange="",timerange="",
		correlation=mycorr,scan=myscan,array="",observation="",timeaverage=False,
		timebin="0s",timespan="",maxuvwdistance=0.0,disableparallel=None,ddistart=None,
		taql=None,monolithic_processing=None,intent="",reportingaxes="ddid")
	mymean1 = mystat['DATA_DESC_ID=0']['mean']
	return mymean1


def mygaincal_ap1(myfile,mycal,myref,myflagspw,myuvracal,calsuffix):
	default(gaincal)
#	gaincal(vis=myfile, caltable=str(myfile)+'.AP.G.', spw =myflagspw,uvrange=myuvracal,append=True,
#		field=mycal,solint = 'int',refant = myref, minsnr = 2.0, solmode ='L1R', gaintype = 'G', calmode = 'ap',
#		gaintable = [str(myfile)+'.K1', str(myfile)+'.B1' ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
#		parang = True )
	gaincal(vis=myfile, caltable=str(myfile)+'.AP.G.', spw =myflagspw,uvrange=myuvracal,append=True,
		field=mycal,solint = '120s',refant = myref, minsnr = 2.0, gaintype = 'G', calmode = 'ap',
		gaintable = [str(myfile)+'.K1', str(myfile)+'.B1' ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
		parang = True )
	return gaintable


def mygaincal_ap2(myfile,mycal,myref,myflagspw,myuvracal,calsuffix):
	default(gaincal)
#	gaincal(vis=myfile, caltable=str(myfile)+'.AP.G.'+'recal', append=True, field=mycal, spw =myflagspw,
#		uvrange=myuvracal, solint = 'int', refant = myref, solmode ='L1R', minsnr = 2.0, gaintype = 'G', calmode = 'ap',
#		gaintable = [str(myfile)+'.K1'+'recal', str(myfile)+'.B1'+'recal' ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
#		parang = True )
	gaincal(vis=myfile, caltable=str(myfile)+'.AP.G.'+calsuffix, spw =myflagspw,uvrange=myuvracal,append=True,
		field=mycal,solint = '120s',refant = myref, minsnr = 2.0, gaintype = 'G', calmode = 'ap',
		gaintable = [str(myfile)+'.K1'+calsuffix, str(myfile)+'.B1'+calsuffix ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
		parang = True )
	return gaintable

def getfluxcal(myfile,mycalref,myscal):
	myscale = fluxscale(vis=myfile, caltable=str(myfile)+'.AP.G.', fluxtable=str(myfile)+'.fluxscale', reference=mycalref, transfer=myscal,
                    incremental=False)
#	myscale = fluxscale(vis=myfile, caltable=str(myfile)+'.AP.G.'+'recal', fluxtable=str(myfile)+'.fluxscale'+'recal', reference=mycalref,
#                    transfer=myscal, incremental=False)
	return myscale


def getfluxcal2(myfile,mycalref,myscal,calsuffix):
#	if calsuffix == '':
#	myscale = fluxscale(vis=myfile, caltable=str(myfile)+'.AP.G.', fluxtable=str(myfile)+'.fluxscale', reference=mycalref, transfer=myscal,
#                    incremental=False)
#	if calsuffix == 'recal':
	myscale = fluxscale(vis=myfile, caltable=str(myfile)+'.AP.G.'+calsuffix, fluxtable=str(myfile)+'.fluxscale'+calsuffix, reference=mycalref,
       	            transfer=myscal, incremental=False)
	return myscale



def mygaincal_ap_redo(myfile,mycal,myref,myflagspw,myuvracal):
	default(gaincal)
#	gaincal(vis=myfile, caltable=str(myfile)+'.AP.G.'+'recal', append=True, field=mycal, spw =myflagspw,
#		uvrange=myuvracal, solint = 'int', refant = myref, solmode ='L1R', minsnr = 2.0, gaintype = 'G', calmode = 'ap',
#		gaintable = [str(myfile)+'.K1'+'recal', str(myfile)+'.B1'+'recal' ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
#		parang = True )
	gaincal(vis=myfile, caltable=str(myfile)+'.AP.G.'+'recal', append=True, spw =myflagspw, uvrange=myuvracal,
		field=mycal,solint = '120s',refant = myref, minsnr = 2.0, gaintype = 'G', calmode = 'ap',
		gaintable = [str(myfile)+'.K1'+'recal', str(myfile)+'.B1'+'recal' ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
		parang = True )
	return gaintable

def getfluxcal_redo(myfile,mycalref,myscal):
	myscale = fluxscale(vis=myfile, caltable=str(myfile)+'.AP.G.'+'recal', fluxtable=str(myfile)+'.fluxscale'+'recal', reference=mycalref,
                    transfer=myscal, incremental=False)
	return myscale

def mytfcrop(myfile,myfield,myants,tcut,fcut,mydatcol,myflagspw):
	default(flagdata)
	flagdata(vis=myfile, antenna = myants, field = myfield,	spw = myflagspw, mode='tfcrop', ntime='300s', combinescans=False,
		datacolumn=mydatcol, timecutoff=tcut, freqcutoff=fcut, timefit='line', freqfit='line', flagdimension='freqtime',
		usewindowstats='sum', extendflags = False, action='apply', display='none')
	return


def myrflag(myfile,myfield, myants, mytimdev, myfdev,mydatcol,myflagspw):
	default(flagdata)
	flagdata(vis=myfile, field = myfield, spw = myflagspw, antenna = myants, mode='rflag', ntime='scan', combinescans=False,
		datacolumn=mydatcol, winsize=3, timedevscale=mytimdev, freqdevscale=myfdev, spectralmax=1000000.0, spectralmin=0.0,
		extendflags=False, channelavg=False, timeavg=False, action='apply', display='none')
	return


def myrflagavg(myfile,myfield, myants, mytimdev, myfdev,mydatcol,myflagspw):
	default(flagdata)
	flagdata(vis=myfile, field = myfield, spw = myflagspw, antenna = myants, mode='rflag', ntime='300s', combinescans=True,
		datacolumn=mydatcol, winsize=3,	minchanfrac= 0.8, flagneartime = True, basecnt = True, fieldcnt = True,
		timedevscale=mytimdev, freqdevscale=myfdev, spectralmax=1000000.0, spectralmin=0.0, extendflags=False,
		channelavg=False, timeavg=False, action='apply', display='none')
	return




def mysplitinit(myfile,myfield,myspw,mywidth):
	'''function to split corrected data for any field'''
	default(mstransform)
	mstransform(vis=myfile, field=myfield, spw=myspw, chanaverage=False, chanbin=mywidth, datacolumn='corrected', outputvis=str(myfield)+'split.ms')
	myoutvis=str(myfield)+'split.ms'
	return myoutvis


def mysplitavg(myfile,myfield,myspw,mywidth):
	'''function to split corrected data for any field'''
	myoutname=myfile.split('s')[0]+'avg-split.ms'
	default(mstransform)
	mstransform(vis=myfile, field=myfield, spw=myspw, chanaverage=True, chanbin=mywidth, datacolumn='data', outputvis=myoutname)
	return myoutname


def mytclean(myfile,myniter,mythresh,srno,cell,imsize, mynterms1,mywproj):    # you may change the multi-scale inputs as per your field
	if myniter==0:
		myoutimg = 'dirty-img'
	else:
		myoutimg = 'selfcal'+'img'+str(srno)
	default(tclean)
	if mynterms1 > 1:
		tclean(vis=myfile,
       			imagename=myoutimg, selectdata= True, field='0', spw='0', imsize=imsize, cell=cell, robust=0, weighting='briggs', 
       			specmode='mfs',	nterms=mynterms1, niter=myniter, usemask='auto-multithresh',minbeamfrac=0.1, sidelobethreshold = 1.5,
#			minpsffraction=0.05,
#			maxpsffraction=0.8,
			smallscalebias=0.6, threshold= mythresh, aterm =True, pblimit=-1,
	        	deconvolver='mtmfs', gridder='wproject', wprojplanes=mywproj, scales=[0,5,15],wbawp=False,
			restoration = True, savemodel='modelcolumn', cyclefactor = 0.5, parallel=False,
       			interactive=False)
	else:
		tclean(vis=myfile,
       			imagename=myoutimg, selectdata= True, field='0', spw='0', imsize=imsize, cell=cell, robust=0, weighting='briggs', 
       			specmode='mfs',	nterms=mynterms1, niter=myniter, usemask='auto-multithresh',minbeamfrac=0.1,sidelobethreshold = 1.5,
#			minpsffraction=0.05,
#			maxpsffraction=0.8,
			smallscalebias=0.6, threshold= mythresh, aterm =True, pblimit=-1,
	        	deconvolver='multiscale', gridder='wproject', wprojplanes=mywproj, scales=[0,5,15],wbawp=False,
			restoration = True, savemodel='modelcolumn', cyclefactor = 0.5, parallel=False,
       			interactive=False)
	return myoutimg

def myonlyclean(myfile,myniter,mythresh,srno,cell,imsize,mynterms1,mywproj):
	default(clean)
	clean(vis=myfile,
	selectdata=True,
	spw='0',
	imagename='selfcal'+'img'+str(srno),
	imsize=imsize,
	cell=cell,
	mode='mfs',
	reffreq='',
	weighting='briggs',
	niter=myniter,
	threshold=mythresh,
	nterms=mynterms1,
	gridmode='widefield',
	wprojplanes=mywproj,
	interactive=False,
	usescratch=True)
	myname = 'selfcal'+'img'+str(srno)
	return myname


def mysplit(myfile,srno):
	default(mstransform)
	mstransform(vis=myfile, field='0', spw='0', datacolumn='corrected', outputvis='vis-selfcal'+str(srno)+'.ms')
	myoutvis='vis-selfcal'+str(srno)+'.ms'
	return myoutvis


def mygaincal_ap(myfile,myref,mygtable,srno,pap,mysolint,myuvrascal,mygainspw):
	if pap=='ap':
		mycalmode='ap'
		mysol= mysolint[srno] 
		mysolnorm = True
	else:
		mycalmode='p'
		mysol= mysolint[srno] 
		mysolnorm = False
	os.system('rm -rf '+str(pap)+str(srno)+'.GT')
	default(gaincal)
#	gaincal(vis=myfile, caltable=str(pap)+str(srno)+'.GT', append=False, field='0', spw=mygainspw,
#		uvrange=myuvrascal, solint = mysol, refant = myref, minsnr = 2.0, gaintype = 'G',
# for casa 5.5 release
#		solmode='L1R', solnorm= mysolnorm, 
# new options in gaincal
#		calmode = mycalmode, gaintable = [], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
#		parang = True )
	gaincal(vis=myfile, caltable=str(pap)+str(srno)+'.GT', append=False, field='0', spw=mygainspw,
		uvrange=myuvrascal, solint = mysol, refant = myref, minsnr = 2.0, gaintype = 'G',
		solnorm= mysolnorm, calmode = mycalmode, gaintable = [], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
		parang = True )
	mycal = str(pap)+str(srno)+'.GT'
	return mycal


def myapplycal(myfile,mygaintables):
	# applycal
	default(applycal)
	applycal(vis=myfile, field='0', gaintable=mygaintables, gainfield=['0'], applymode='calflag', 
	         interp=['linear'], calwt=False, parang=False)
	print 'Did applycal.'




def flagresidual(myfile,myclipresid,myflagspw):
	default(flagdata)
	flagdata(vis=myfile, mode ='rflag', datacolumn="RESIDUAL_DATA", field='', timecutoff=6.0,  freqcutoff=6.0,
		timefit="line", freqfit="line",	flagdimension="freqtime", extendflags=False, timedevscale=3.0,
		freqdevscale=3.0, spectralmax=500.0, extendpols=False, growaround=False, flagneartime=False,
		flagnearfreq=False, action="apply", flagbackup=True, overwrite=True, writeflags=True)
	default(flagdata)
	flagdata(vis=myfile, mode ='clip', datacolumn="RESIDUAL_DATA", clipminmax=myclipresid,
		clipoutside=True, clipzeros=True, field='', spw=myflagspw, extendflags=False,
		extendpols=False, growaround=False, flagneartime=False,	flagnearfreq=False,
		action="apply",	flagbackup=True, overwrite=True, writeflags=True)
	flagdata(vis=myfile,mode="summary",datacolumn="RESIDUAL_DATA", extendflags=False, 
		name=myfile+'temp.summary', action="apply", flagbackup=True,overwrite=True, writeflags=True)
#


	 

def myselfcal(myfile,myref,nloops,nploops,myvalinit,mycellsize,myimagesize,mynterms2,mywproj1,mysolint1,myclipresid,myflagspw,mygainspw2,mymakedirty):
	myref = myref
	nscal = nloops # number of selfcal loops
	npal = nploops # number of phasecal loops
	# selfcal loop
	myimages=[]
	mygt=[]
	myniterstart = 1500
	myniterend = 200000	
#	myval= myvalinit # mJy
	if nscal == 0:
		i = nscal
		myniter = 0 # this is to make a dirty image
#		mythresh = myval[i]   #str(startthreshold/(count+1))+'mJy'
		mythresh = str(myvalinit/(i+1))+'mJy'
		print "Using "+ myfile[i]+" for making only an image."
		if usetclean == False:
			myimg = myonlyclean(myfile[i],myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # clean
		else:
			myimg = mytclean(myfile[i],myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # tclean
		exportfits(imagename=myimg+'.image.tt0', fitsimage=myimg+'.fits')
	else:
		for i in range(0,nscal+1): # plan 4 P and 4AP iterations
			if mymakedirty == True:
				if i == 0:
					myniter = 0 # this is to make a dirty image
#					mythresh = myval[i]
					mythresh = str(myvalinit/(i+1))+'mJy'
					print "Using "+ myfile[i]+" for making only a dirty image."
					if usetclean == False:
						myimg = myonlyclean(myfile[i],myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # clean
					else:
						myimg = mytclean(myfile[i],myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # tclean
					if mynterms2 > 1:
						exportfits(imagename=myimg+'.image.tt0', fitsimage=myimg+'.fits')
					else:
						exportfits(imagename=myimg+'.image', fitsimage=myimg+'.fits')

			else:
				myniter=int(myniterstart*2**i) #myniterstart*(2**i)  # niter is doubled with every iteration int(startniter*2**count)
				if myniter > myniterend:
					myniter = myniterend
#				mythresh = myval[i]
				mythresh = str(myvalinit/(i+1))+'mJy'
#				print i, 'mythreshold=',mythresh
				if i < npal:
					mypap = 'p'
					print "Using "+ myfile[i]+" for imaging."
					if usetclean == False:
						myimg = myonlyclean(myfile[i],myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # clean
					else:
						myimg = mytclean(myfile[i],myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # tclean
					if mynterms2 > 1:
						exportfits(imagename=myimg+'.image.tt0', fitsimage=myimg+'.fits')
					else:
						exportfits(imagename=myimg+'.image', fitsimage=myimg+'.fits')
					myimages.append(myimg)	# list of all the images created so far
					flagresidual(myfile[i],clipresid,'')
					if i>0:
						myctables = mygaincal_ap(myfile[i],myref,mygt[i-1],i,mypap,mysolint1,uvrascal,mygainspw2)
					else:					
						myctables = mygaincal_ap(myfile[i],myref,mygt,i,mypap,mysolint1,uvrascal,mygainspw2)						
					mygt.append(myctables) # full list of gaintables
					if i < nscal+1:
						myapplycal(myfile[i],mygt[i])
						myoutfile= mysplit(myfile[i],i)
						myfile.append(myoutfile)
#						print i, myfile1
				else:
					mypap = 'ap'
					print "Using "+ myfile[i]+" for imaging."
					if usetclean == False:
						myimg = myonlyclean(myfile[i],myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # clean
					else:
						myimg = mytclean(myfile[i],myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # tclean
					if mynterms2 > 1:
						exportfits(imagename=myimg+'.image.tt0', fitsimage=myimg+'.fits')
					else:
						exportfits(imagename=myimg+'.image', fitsimage=myimg+'.fits')
					myimages.append(myimg)	# list of all the images created so far
					flagresidual(myfile[i],clipresid,'')
					if i!= nscal:
						myctables = mygaincal_ap(myfile[i],myref,mygt[i-1],i,mypap,mysolint1,'',mygainspw2)
						mygt.append(myctables) # full list of gaintables
						if i < nscal+1:
							myapplycal(myfile[i],mygt[i])
							myoutfile= mysplit(myfile[i],i)
							myfile.append(myoutfile)
							print i, myfile1
				print "Visibilities from the previous selfcal will be deleted."
				if i < nscal:
					myoldvis = 'vis-selfcal'+str(i-1)+'.ms'
					print "Deleting "+str(myoldvis)
					os.system('rm -rf '+str(myoldvis))
			print 'Ran the selfcal loop'
	return myfile, mygt, myimages

def myflagsum(myfile,myfields):
	flagsum = flagdata(vis=myfile, field =myfields[0], mode='summary')
	for i in range(0,len(myfields)):
		src = myfields[i]
		flagpercentage = 100.0 * flagsum['field'][src]['flagged'] / flagsum['field'][src]['total']
#		print("\n %2.1f%% of the source are flagged.\n" % (100.0 * flagsum['field'][src]['flagged'] / flagsum['field'][src]['total']))
	return flagpercentage

#############End of functions##############################################################################
print "#######################################################################################"
print "You are using CAPTURE: CAsa Pipeline-cum-Toolkit for Upgraded GMRT data REduction."
print "This has been developed at NCRA by Ruta Kale and Ishwara Chandra."
print "#######################################################################################"

if fromlta == True:
	os.system(gvbinpath[0]+' '+ltafile)
	os.system(gvbinpath[1]+' '+ltafile.split('.')[0]+'.log')

# Step 0. Importgmrt  - will also create a .list file 
if fromraw == True:
	myfitsfile = rawfile
	myoutvis = myfile1
	default(importgmrt)
	importgmrt(fitsfile=myfitsfile, vis = myoutvis)
	# create a dummy flagdata table
	os.system("rm -rf dummy-flg.dat")
	default(flagdata)
	flagdata(vis=myfile1, mode='clip', clipminmax=[0,20000.], field='', spw='0:0', antenna='',correlation='',
		action='apply',	savepars=True,	cmdreason='dummy', flagbackup=False, outfile='dummy-flg.dat')
	vislistobs(myfile1)
	print "You have the following fields in your file:",getfields(myfile1)

############################################3

if fromms == True:
	mynchan = getnchan(myfile1)
	print "The number of channels in your file:", mynchan
	if mynchan == 1024:
		mygoodchans = '0:250~300'   # used for visstat
		flagspw = '0:51~950'
		gainspw = '0:101~900'
		gainspw2 = ''   # central good channels after split file for self-cal	
	elif mynchan == 2048:
		mygoodchans = '0:500~600'   # used for visstat
		flagspw = '0:101~1900'
		gainspw = '0:201~1800'
		gainspw2 = ''   # central good channels after split file for self-cal
	elif mynchan == 4096:
		mygoodchans = '0:1000~1200'
		flagspw = '0:41~4050'
		gainspw = '0:201~3600'
		gainspw2 = ''   # central good channels after split file for self-cal
	elif mynchan == 8192:
		mygoodchans = '0:2000~3000'
		flagspw = '0:500~7800'
		gainspw = '0:1000~7000'
		gainspw2 = ''   # central good channels after split file for self-cal
	elif mynchan == 16384:
		mygoodchans = '0:4000~6000'
		flagspw = '0:1000~14500'
		gainspw = '0:2000~13500'
		gainspw2 = ''   # central good channels after split file for self-cal
	elif mynchan == 128:
		mygoodchans = '0:50~70'
		flagspw = '0:5~115'
		gainspw = '0:11~115'
		gainspw2 = ''   # central good channels after split file for self-cal
	elif mynchan == 256:
		mygoodchans = '0:100~120'
		flagspw = '0:11~240'
		gainspw = '0:21~230'
		gainspw2 = ''   # central good channels after split file for self-cal	
	elif mynchan == 512:
		mygoodchans = '0:200~240'
		flagspw = '0:21~480'
		gainspw = '0:41~460'
		gainspw2 = ''   # central good channels after split file for self-cal	

# fix targets
	myfields = getfields(myfile1)
	stdcals = ['3C48','3C147','3C286','0542+498','1331+305','0137+331']
	vlacals = np.loadtxt('./vla-cals.list',dtype='string')
	myampcals =[]
	mypcals=[]
	mytargets=[]
	for i in range(0,len(myfields)):
		if myfields[i] in stdcals:
			myampcals.append(myfields[i])
		elif myfields[i] in vlacals:
			mypcals.append(myfields[i])
		else:
			mytargets.append(myfields[i])
	mybpcals = myampcals
##################################
#	if mypcals==[]:
#		mypcals = myampcals
##################################
	print "Amplitude caibrators are", myampcals
	print "Phase calibrators are", mypcals
	print "Target sources are", mytargets
# need a condition to see if the pcal is same as 
#if fromms==True:
	ampcalscans =[]
#	ampcalscans=0
	for i in range(0,len(myampcals)):
		ampcalscans.extend(getscans(myfile1, myampcals[i]))
#		ampcalscans=ampcalscans+ getscans(myfile1, myampcals[i])
	pcalscans=[]
#	pcalscans=0
	for i in range(0,len(mypcals)):
		pcalscans.extend(getscans(myfile1, mypcals[i]))
#		pcalscans=pcalscans+getscans(myfile1, mypcals[i])
	tgtscans=[]
#	tgtscans=0
	for i in range(0,len(mytargets)):
		tgtscans.extend(getscans(myfile1,mytargets[i]))
#		tgtscans=tgtscans+(getscans(myfile1,mytargets[i]))
	print ampcalscans
	print pcalscans	
	print tgtscans
	allscanlist= ampcalscans+pcalscans+tgtscans
###################################
# get a list of antennas
	antsused = getantlist(myfile1,int(allscanlist[0]))
	print antsused
###################################
# find band ants
	if flagbadants==True:
		findbadants = True
	if findbadants == True:
		myantlist = antsused
#['C00', 'C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13', 'C14', 'E02', 'E03', 'E04', 'E05', 'E06', 'S01', 'S02', 'S03', 'S04', 'S06', 'W01', 'W02', 'W03', 'W04', 'W05', 'W06']
		mycmds = []
		meancutoff = 0.4    # uncalibrated mean cutoff
		mycorr1='rr'
		mycorr2='ll'
		mygoodchans1=mygoodchans
		mycalscans = ampcalscans+pcalscans
		print mycalscans
#		myscan1 = pcalscans
		allbadants=[]
		for j in range(0,len(mycalscans)):
			myantmeans = []
			badantlist = []
			for i in range(0,len(myantlist)):
				oneantmean1 = myvisstatampraw(myfile1,mygoodchans,myantlist[i],mycorr1,str(mycalscans[j]))
				oneantmean2 = myvisstatampraw(myfile1,mygoodchans,myantlist[i],mycorr2,str(mycalscans[j]))
				oneantmean = min(oneantmean1,oneantmean2)
				myantmeans.append(oneantmean)
#				print myantlist[i], oneantmean1, oneantmean2
				if oneantmean < meancutoff:
					badantlist.append(myantlist[i])
					allbadants.append(myantlist[i])
			print "The following antennas are bad for the given scan numbers."
			print badantlist, str(mycalscans[j])
			if badantlist!=[]:
				myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str('; '.join(badantlist)), str(mycalscans[j]))
				mycmds.append(myflgcmd)
				print myflgcmd
				onelessscan = mycalscans[j] - 1
				onemorescan = mycalscans[j] + 1
				if onelessscan in tgtscans:
					myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str('; '.join(badantlist)), str(mycalscans[j]-1))
					mycmds.append(myflgcmd)
					print myflgcmd
				if onemorescan in tgtscans:
					myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str('; '.join(badantlist)), str(mycalscans[j]+1))
					mycmds.append(myflgcmd)
					print myflgcmd
# execute the flagging commands accumulated in cmds
		print mycmds
		if flagbadants==True:
			print "Now flagging the bad antennas."
			default(flagdata)
			flagdata(vis=myfile1,mode='list', inpfile=mycmds)	
######### Bad channel flagging for known persistent RFI.
	if flagbadfreq==True:
		findbadchans = True
	if findbadchans ==True:
		rfifreqall =[0.36E09,0.3796E09,0.486E09,0.49355E09,0.8808E09,0.885596E09,0.7646E09,0.769092E09] # always bad
		myfreqs =  freq_info(myfile1)
		mybadchans=[]
		for j in range(0,len(rfifreqall)-1,2):
#			print rfifreqall[j]
			for i in range(0,len(myfreqs)):
				if (myfreqs[i] > rfifreqall[j] and myfreqs[i] < rfifreqall[j+1]): #(myfreqs[i] > 0.486E09 and myfreqs[i] < 0.49355E09):
					mybadchans.append('0:'+str(i))
		mychanflag = str(', '.join(mybadchans))
#		print mychanflag
		if mybadchans!=[]:
#			print mychanflag
			myflgcmd = ["mode='manual' spw='%s'" % (mychanflag)]
			if flagbadfreq==True:
				default(flagdata)
				flagdata(vis=myfile1,mode='list', inpfile=myflgcmd)
		else:
			print "No bad frequencies found in the range."

############ Initial flagging ################

if myflaginit == True:
	casalog.filter('INFO')
#Step 1 : Flag the first channel.
	default(flagdata)
	flagdata(vis=myfile1, mode='manual', field='', spw='0:0', antenna='', correlation='', action='apply', savepars=True,
		cmdreason='badchan', outfile='flg1.dat')
#Step 3: Do a quack step 
	default(flagdata)
	flagdata(vis=myfile1, mode='quack', field='', spw='0', antenna='', correlation='', timerange='',
		quackinterval=myquackinterval, quackmode='beg', action='apply', savepars=True, cmdreason='quackbeg',
	        outfile='flg3.dat')
	default(flagdata)
	flagdata(vis=myfile1, mode='quack', field='', spw='0', antenna='', correlation='', timerange='', quackinterval=myquackinterval,
		quackmode='endb', action='apply', savepars=True, cmdreason='quackendb', outfile='flg3.dat')
# Clip at high amp levels
	if myampcals !=[]:
		default(flagdata)
		flagdata(vis=myfile1,mode="clip", spw=flagspw,field=str(','.join(myampcals)), clipminmax=clipfluxcal, datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
        		action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
	if mypcals !=[]:
		default(flagdata)
		flagdata(vis=myfile1,mode="clip", spw=flagspw,field=str(','.join(mypcals)), clipminmax=clipphasecal, datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
        		action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# After clip, now flag using 'tfcrop' option for flux and phase cal tight flagging
		flagdata(vis=myfile1,mode="tfcrop", datacolumn="DATA", field=str(','.join(mypcals)), ntime="scan",
		        timecutoff=5.0, freqcutoff=5.0, timefit="line",freqfit="line",flagdimension="freqtime", 
		        extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
		        action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (80% more means full flag, change if required)
		flagdata(vis=myfile1,mode="extend",spw=flagspw,field=str(','.join(mypcals)),datacolumn="DATA",clipzeros=True,
		         ntime="scan", extendflags=False, extendpols=True,growtime=80.0, growfreq=80.0,growaround=False,
		         flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
######### target flagging ### clip first
	if target == True:
		if mytargets !=[]:
			flagdata(vis=myfile1,mode="clip", spw=flagspw,field=str(','.join(mytargets)), clipminmax=cliptarget, datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
		        	action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# flagging with tfcrop before calibration
			default(flagdata)
			flagdata(vis=myfile1,mode="tfcrop", datacolumn="DATA", field=str(','.join(mytargets)), ntime="scan",
		        	timecutoff=6.0, freqcutoff=6.0, timefit="poly",freqfit="poly",flagdimension="freqtime", 
		        	extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
		        	action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (80% more means full flag, change if required)
			flagdata(vis=myfile1,mode="extend",spw=flagspw,field=str(','.join(mytargets)),datacolumn="DATA",clipzeros=True,
		        	 ntime="scan", extendflags=False, extendpols=True,growtime=80.0, growfreq=80.0,growaround=False,
		        	 flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now summary
		flagdata(vis=myfile1,mode="summary",datacolumn="DATA", extendflags=True, 
	        	 name=vis+'summary.split', action="apply", flagbackup=True,overwrite=True, writeflags=True)	
#####################################################################
#if doinitcal==True:
#	print "After initial flagging:"
#	myflagtabs = flagmanager(vis = myfile1, mode ='list')
#	print 'myflagtabs=',myflagtabs

# Calibration begins.
if doinitcal == True:
	mycalsuffix = ''
	casalog.filter('INFO')
#	print "Summary of flagtables before initial calibration:"
#	myflagtabs = flagmanager(vis = myfile1, mode ='list')
#	print 'myflagtabs=',myflagtabs
	clearcal(vis=myfile1)
#delmod step to keep model column free of spurious values
	for i in range(0,len(myampcals)):
#		delmod(vis=myfile1)	
		default(setjy)
		setjy(vis=myfile1, spw=flagspw, field=myampcals[i])
		print "Done setjy on %s"%(myampcals[i])
# Delay calibration  using the first flux calibrator in the list - should depend on which is less flagged
	os.system('rm -rf '+str(myfile1)+'.K1'+mycalsuffix)
	gaincal(vis=myfile1, caltable=str(myfile1)+'.K1'+mycalsuffix, spw =flagspw, field=myampcals[0], 
		solint='60s', refant=myrefant,	solnorm= True, gaintype='K', gaintable=[], parang=True)
	kcorrfield =myampcals[0]
#	print 'wrote table',str(myfile1)+'.K1'
# an initial bandpass
	os.system('rm -rf '+str(myfile1)+'.AP.G0'+mycalsuffix)
	default(gaincal)
#	gaincal(vis=myfile1, caltable=str(myfile1)+'.AP.G0', append=True, field=str(','.join(mybpcals)), 
#		spw =flagspw, solint = 'int', refant = myrefant, minsnr = 2.0, solmode ='L1R', gaintype = 'G', calmode = 'ap', gaintable = [str(myfile1)+'.K1'],
#		interp = ['nearest,nearestflag', 'nearest,nearestflag' ], parang = True)
	gaincal(vis=myfile1, caltable=str(myfile1)+'.AP.G0'+mycalsuffix, append=True, field=str(','.join(mybpcals)), 
		spw =flagspw, solint = 'int', refant = myrefant, minsnr = 2.0, gaintype = 'G', calmode = 'ap', gaintable = [str(myfile1)+'.K1'+mycalsuffix],
		interp = ['nearest,nearestflag', 'nearest,nearestflag' ], parang = True)
	os.system('rm -rf '+str(myfile1)+'.B1'+mycalsuffix)
	default(bandpass)
	bandpass(vis=myfile1, caltable=str(myfile1)+'.B1'+mycalsuffix, spw =flagspw, field=str(','.join(mybpcals)), solint='inf', refant=myrefant, solnorm = True,
		minsnr=2.0, fillgaps=8, parang = True, gaintable=[str(myfile1)+'.K1'+mycalsuffix,str(myfile1)+'.AP.G0'+mycalsuffix], interp=['nearest,nearestflag','nearest,nearestflag'])
# do a gaincal on all calibrators
	mycals=myampcals+mypcals
	i=0
	os.system('rm -rf '+str(myfile1)+'.AP.G.'+mycalsuffix)
	for i in range(0,len(mycals)):
		mygaincal_ap2(myfile1,mycals[i],myrefant,gainspw,uvracal,mycalsuffix)
# Get flux scale
	os.system('rm -rf '+str(myfile1)+'.fluxscale'+mycalsuffix)
######################################
	if mypcals !=[]:
		if '3C286' in myampcals:
			myfluxscale= getfluxcal2(myfile1,'3C286',str(', '.join(mypcals)),mycalsuffix)
			myfluxscaleref = '3C286'
		elif '3C147' in myampcals:
			myfluxscale= getfluxcal2(myfile1,'3C147',str(', '.join(mypcals)),mycalsuffix)
			myfluxscaleref = '3C147'
		else:
			myfluxscale= getfluxcal2(myfile1,myampcals[0],str(', '.join(mypcals)),mycalsuffix)
			myfluxscaleref = myampcals[0]
		print myfluxscale
		mygaintables =[str(myfile1)+'.fluxscale'+mycalsuffix,str(myfile1)+'.K1'+mycalsuffix, str(myfile1)+'.B1'+mycalsuffix]
	else:
		mygaintables =[str(myfile1)+'.AP.G.'+mycalsuffix,str(myfile1)+'.K1'+mycalsuffix, str(myfile1)+'.B1'+mycalsuffix]
##############################
	for i in range(0,len(myampcals)):
		default(applycal)
		applycal(vis=myfile1, field=myampcals[i], spw = flagspw, gaintable=mygaintables, gainfield=[myampcals[i],'',''], 
        		 interp=['nearest','',''], calwt=[False], parang=False)
#For phase calibrator:
	if mypcals !=[]:
		default(applycal)
		applycal(vis=myfile1, field=str(', '.join(mypcals)), spw = flagspw, gaintable=mygaintables, gainfield=str(', '.join(mypcals)), 
		         interp=['nearest','','nearest'], calwt=[False], parang=False)
#For the target:
	if target ==True:
		if mypcals !=[]:
			default(applycal)
			applycal(vis=myfile1, field=str(', '.join(mytargets)), spw = flagspw, gaintable=mygaintables,
		        	 gainfield=[str(', '.join(mypcals)),'',''],interp=['linear','','nearest'], calwt=[False], parang=False)
		else:
			default(applycal)
			applycal(vis=myfile1, field=str(', '.join(mytargets)), spw = flagspw, gaintable=mygaintables,
		        	 gainfield=[str(', '.join(myampcals)),'',''],interp=['linear','','nearest'], calwt=[False], parang=False)	
	print "Finished initial calibration."
#	print "Summary of flagtables after initial calibration:"
#	myflagtabs = flagmanager(vis = myfile1, mode ='list')
#	print 'myflagtabs=',myflagtabs

#############################################################################3

# Do tfcrop on the file first - only for the target
# No need for antenna selection




#######Ishwar post calibration flagging
if mydoflag == True:
	print "You have chosen to flag after the initial calibration."
	default(flagdata)
	if myampcals !=[]:
		flagdata(vis=myfile1,mode="clip", spw=flagspw,field=str(', '.join(myampcals)), clipminmax=clipfluxcal,
        		datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        		action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
	if mypcals !=[]:
		flagdata(vis=myfile1,mode="clip", spw=flagspw,field=str(', '.join(mypcals)), clipminmax=clipphasecal,
        		datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        		action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# After clip, now flag using 'tfcrop' option for flux and phase cal tight flagging
		flagdata(vis=myfile1,mode="tfcrop", datacolumn="corrected", field=str(', '.join(mypcals)), ntime="scan",
        		timecutoff=6.0, freqcutoff=5.0, timefit="line",freqfit="line",flagdimension="freqtime", 
        		extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
        		action="apply", flagbackup=True,overwrite=True, writeflags=True)
# now flag using 'rflag' option  for flux and phase cal tight flagging
		flagdata(vis=myfile1,mode="rflag",datacolumn="corrected",field=str(', '.join(mypcals)), timecutoff=5.0, 
		        freqcutoff=5.0,timefit="poly",freqfit="line",flagdimension="freqtime", extendflags=False,
		        timedevscale=4.0,freqdevscale=4.0,spectralmax=500.0,extendpols=False, growaround=False,
		        flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (70% more means full flag, change if required)
		flagdata(vis=myfile1,mode="extend",spw=flagspw,field=str(', '.join(mypcals)),datacolumn="corrected",clipzeros=True,
		         ntime="scan", extendflags=False, extendpols=False,growtime=90.0, growfreq=90.0,growaround=False,
		         flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now flag for target - moderate flagging, more flagging in self-cal cycles
	if mytargets !=[]:
		flagdata(vis=myfile1,mode="clip", spw=flagspw,field=str(', '.join(mytargets)), clipminmax=cliptarget,
		        datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
		        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# C-C baselines are selected
		a, b = getbllists(myfile1)
		flagdata(vis=myfile1,mode="tfcrop", datacolumn="corrected", field=str(', '.join(mytargets)), antenna=a[0],
			ntime="scan", timecutoff=8.0, freqcutoff=8.0, timefit="poly",freqfit="line",flagdimension="freqtime", 
		        extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
		        action="apply", flagbackup=True,overwrite=True, writeflags=True)
# C- arm antennas and arm-arm baselines are selected.
		flagdata(vis=myfile1,mode="tfcrop", datacolumn="corrected", field=str(', '.join(mytargets)), antenna=b[0],
			ntime="scan", timecutoff=6.0, freqcutoff=5.0, timefit="poly",freqfit="line",flagdimension="freqtime", 
        		extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
        		action="apply", flagbackup=True,overwrite=True, writeflags=True)
# now flag using 'rflag' option
# C-C baselines are selected
		flagdata(vis=myfile1,mode="rflag",datacolumn="corrected",field=str(', '.join(mytargets)), timecutoff=5.0, antenna=a[0],
        		freqcutoff=8.0,timefit="poly",freqfit="poly",flagdimension="freqtime", extendflags=False,
        		timedevscale=8.0,freqdevscale=5.0,spectralmax=500.0,extendpols=False, growaround=False,
        		flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
# C- arm antennas and arm-arm baselines are selected.
		flagdata(vis=myfile1,mode="rflag",datacolumn="corrected",field=str(', '.join(mytargets)), timecutoff=5.0, antenna=b[0],
        		freqcutoff=5.0,timefit="poly",freqfit="poly",flagdimension="freqtime", extendflags=False,
        		timedevscale=5.0,freqdevscale=5.0,spectralmax=500.0,extendpols=False, growaround=False,
        		flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
# Now summary
	flagdata(vis=myfile1,mode="summary",datacolumn="corrected", extendflags=True, 
         name=vis+'summary.split', action="apply", flagbackup=True,overwrite=True, writeflags=True)


#################### new redocal #########################3
# Calibration begins.
if redocal == True:
	print "You have chosen to redo the calibration on your data."
	mycalsuffix = 'recal'
	casalog.filter('INFO')
#	print "Summary of flagtables before calibration:"
#	myflagtabs = flagmanager(vis = myfile1, mode ='list')
#	print 'myflagtabs=',myflagtabs
	clearcal(vis=myfile1)
#delmod step to keep model column free of spurious values
	for i in range(0,len(myampcals)):
#		delmod(vis=myfile1)	
		default(setjy)
		setjy(vis=myfile1, spw=flagspw, field=myampcals[i])
		print "Done setjy on %s"%(myampcals[i])
# Delay calibration  using the first flux calibrator in the list - should depend on which is less flagged
	os.system('rm -rf '+str(myfile1)+'.K1'+mycalsuffix)
	gaincal(vis=myfile1, caltable=str(myfile1)+'.K1'+mycalsuffix, spw =flagspw, field=myampcals[0], 
		solint='60s', refant=myrefant,	solnorm= True, gaintype='K', gaintable=[], parang=True)
	kcorrfield =myampcals[0]
#	print 'wrote table',str(myfile1)+'.K1'+mycalsuffix
# an initial bandpass
	os.system('rm -rf '+str(myfile1)+'.AP.G0'+mycalsuffix)
	default(gaincal)
#	gaincal(vis=myfile1, caltable=str(myfile1)+'.AP.G0', append=True, field=str(','.join(mybpcals)), 
#		spw =flagspw, solint = 'int', refant = myrefant, minsnr = 2.0, solmode ='L1R', gaintype = 'G', calmode = 'ap', gaintable = [str(myfile1)+'.K1'],
#		interp = ['nearest,nearestflag', 'nearest,nearestflag' ], parang = True)
	gaincal(vis=myfile1, caltable=str(myfile1)+'.AP.G0'+mycalsuffix, append=True, field=str(','.join(mybpcals)), 
		spw =flagspw, solint = 'int', refant = myrefant, minsnr = 2.0, gaintype = 'G', calmode = 'ap', gaintable = [str(myfile1)+'.K1'],
		interp = ['nearest,nearestflag', 'nearest,nearestflag' ], parang = True)
	os.system('rm -rf '+str(myfile1)+'.B1')
	default(bandpass)
	bandpass(vis=myfile1, caltable=str(myfile1)+'.B1'+mycalsuffix, spw =flagspw, field=str(','.join(mybpcals)), solint='inf', refant=myrefant, solnorm = True,
		minsnr=2.0, fillgaps=8, parang = True, gaintable=[str(myfile1)+'.K1'+mycalsuffix,str(myfile1)+'.AP.G0'+mycalsuffix], interp=['nearest,nearestflag','nearest,nearestflag'])
# do a gaingal on alll calibrators
	mycals=myampcals+mypcals
	i=0
	os.system('rm -rf '+str(myfile1)+'.AP.G.'+mycalsuffix)
	for i in range(0,len(mycals)):
		mygaincal_ap2(myfile1,mycals[i],myrefant,gainspw,uvracal,mycalsuffix)
# Get flux scale
#if doinitcal == True:	
	os.system('rm -rf '+str(myfile1)+'.fluxscale'+mycalsuffix)
########################################
	if mypcals !=[]:
		if '3C286' in myampcals:
#			myfluxscale= getfluxcal(myfile1,'3C286',str(', '.join(mypcals)))
			myfluxscale= getfluxcal2(myfile1,'3C286',str(', '.join(mypcals)),mycalsuffix)
			myfluxscaleref = '3C286'
		elif '3C147' in myampcals:
#			myfluxscale= getfluxcal(myfile1,'3C147',str(', '.join(mypcals)))
			myfluxscale= getfluxcal2(myfile1,'3C147',str(', '.join(mypcals)),mycalsuffix)
			myfluxscaleref = '3C147'
		else:
#			myfluxscale= getfluxcal(myfile1,myampcals[0],str(', '.join(mypcals)))
			myfluxscale= getfluxcal2(myfile1,myampcals[0],str(', '.join(mypcals)),mycalsuffix)
			myfluxscaleref = myampcals[0]
		print myfluxscale
		mygaintables =[str(myfile1)+'.fluxscale'+mycalsuffix,str(myfile1)+'.K1'+mycalsuffix, str(myfile1)+'.B1'+mycalsuffix]
	else:
		mygaintables =[str(myfile1)+'.AP.G.'+mycalsuffix,str(myfile1)+'.K1'+mycalsuffix, str(myfile1)+'.B1'+mycalsuffix]
###############################################################
	for i in range(0,len(myampcals)):
		default(applycal)
		applycal(vis=myfile1, field=myampcals[i], spw = flagspw, gaintable=mygaintables, gainfield=[myampcals[i],'',''], 
        		 interp=['nearest','',''], calwt=[False], parang=False)
#For phase calibrator:
	if mypcals !=[]:
		default(applycal)
		applycal(vis=myfile1, field=str(', '.join(mypcals)), spw = flagspw, gaintable=mygaintables, gainfield=str(', '.join(mypcals)), 
		         interp=['nearest','','nearest'], calwt=[False], parang=False)
#For the target:
	if target ==True:
		if mypcals !=[]:
			default(applycal)
			applycal(vis=myfile1, field=str(', '.join(mytargets)), spw = flagspw, gaintable=mygaintables,
		        	 gainfield=[str(', '.join(mypcals)),'',''],interp=['linear','','nearest'], calwt=[False], parang=False)
		else:
			default(applycal)
			applycal(vis=myfile1, field=str(', '.join(mytargets)), spw = flagspw, gaintable=mygaintables,
		        	 gainfield=[str(', '.join(myampcals)),'',''],interp=['linear','','nearest'], calwt=[False], parang=False)			
	print "Finished re-calibration."
#	print "Summary of flagtables after initial calibration:"
#	myflagtabs = flagmanager(vis = myfile1, mode ='list')
#	print 'myflagtabs=',myflagtabs

###############################################################
#############################################################
# SPLIT step
#############################################################
if dosplit == True:
	print "The data on targets will be split into separate files."
	casalog.filter('INFO')
# fix targets
	myfields = getfields(myfile1)
	stdcals = ['3C48','3C147','3C286','0542+498','1331+305','0137+331']
	vlacals = np.loadtxt('./vla-cals.list',dtype='string')
	myampcals =[]
	mypcals=[]
	mytargets=[]
	for i in range(0,len(myfields)):
		if myfields[i] in stdcals:
			myampcals.append(myfields[i])
		elif myfields[i] in vlacals:
			mypcals.append(myfields[i])
		else:
			mytargets.append(myfields[i])
	for i in range(0,len(mytargets)):
		os.system('rm -rf '+mytargets[i]+'split.ms')
		mysplitfile = mysplitinit(myfile1,mytargets[i],gainspw,1)

#############################################################
# Flagging on split file
#############################################################

if mysplitflag == True:
	print "You have chosen to flag on the split file."
	myantselect =''
	mytfcrop(mysplitfile,'',myantselect,8.0,8.0,'DATA','')
	a, b = getbllists(mysplitfile)
	tdev = 6.0
	fdev = 6.0
	myrflag(mysplitfile,'',a[0],tdev,fdev,'DATA','')
	tdev = 5.0
	fdev = 5.0
	myrflag(mysplitfile,'',b[0],tdev,fdev,'DATA','')
	

#############################################################
# SPLIT AVERAGE
#############################################################

if dosplitavg == True:
	print "Your data will be averaged in frequency."
#	os.system('rm -rf '+mytargets[i]+'avg-split.ms')
	mysplitavgfile = mysplitavg(mysplitfile,'','',mywidth2)


if doflagavg == True:
	print "Flagging on freqeuncy averaged data."
	a, b = getbllists(mysplitavgfile)
	myrflagavg(mysplitavgfile,'',b[0],6.0,6.0,'DATA','')
	myrflagavg(mysplitavgfile,'',a[0],6.0,6.0,'DATA','')


############################################################

if makedirty == True:
	myfile2 = [mysplitavgfile]
	usetclean = True
	if usetclean == True:
		myselfcal(myfile2,myrefant,scaloops,mypcaloops,mythresholds,mycell,myimsize,mynterms,mywproj2,mysolint2,clipresid,'','',makedirty)

if doselfcal == True:
	casalog.filter('INFO')
	clearcal(vis = mysplitavgfile)
	myfile2 = [mysplitavgfile]
	if usetclean == True:
		myselfcal(myfile2,myrefant,scaloops,mypcaloops,mythresholds,mycell,myimsize,mynterms,mywproj2,mysolint2,clipresid,'','',makedirty)


