# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 15:59:36 2018

@author: Jonathan
"""

import psychoLink as pl
from psychopy import visual, event, monitors
import pandas as pd
import numpy as np
import time
import traceback
import scipy.misc
# =============================================================================
# Settings
# =============================================================================
par = {}
# Monitor
par['widthCm'] = 47.5
par['screenDistCm'] = 70.0
par['units'] = 'pix'

# window
par['resolution'] = (1920,1080) #(1680 , 1050)
par['bgColor'] = [150, 150, 150]
par['screenNr'] = 0
par['fullscreen'] = False
par['screenCent'] = (0,0)
par['pxPerDeg'] = pl.angleToPixels(1,
                    par['screenDistCm'], par['widthCm'], par['resolution'])

# fixDot settings
par['fixDotColor'] = [0, 0, 0]
par['fixDotSize'] = 8
par['fixDotPos'] = (0,0)
par['edges'] = 50

# targDot settings
par['targDotColor'] = [255, 0, 0]
par['targDotSize'] = 8
par['leftFixPos'] = (-8.0,0.0) # X,Y cordinates in degrees
par['rightFixPos'] = (8.0,0.0) # X,Y cordinates in degrees

# Phillips pattern
par['philX'] = 5
par['philY'] = 5
par['philCol1'] = [255,255,255]
par['philCol2'] = [0,0,0]
par['philSize'] = (2*par['pxPerDeg'])/par['philX']

# gazeDot settings
par['gazeColor'] = [0, 0, 255]
par['gazeSize'] = 10

# Experiment settings
par['maxWaitForFix'] = 3
par['hitDistance'] = 2
par['maxDur'] = 4

# Conditions and header information
par['expReps'] = 10
par['nrRepsPerBlock'] = 8
cond1 = ['left', 'right']
conds = [cond1]
header = ['endPos']

# Extra header names (will be filled with zeros, use this for logging data)
zeroHeaders = ['tNr','tCor', 'tIncor', 'blockType']
zeroPads = len(zeroHeaders)
header = header + zeroHeaders

# make trialList 
expList = pl.makeTrialList(header, conds, zeroPads = zeroPads, \
                        reps = par['expReps'], shuffle = True)
expList['blockType'] = 'Experiment'
expList['tNr'] = range(1,len(expList)+1)

#==============================================================================
# Initiate screen and monitor
#==============================================================================
# Create monitor
mon = monitors.Monitor('testMonitor',width = par['widthCm'], distance = par['screenDistCm'])
# Create the window with the specified settings, giving mon as the monitor
win = visual.Window(units = par['units'],\
                monitor = mon,\
                size = par['resolution'],\
                colorSpace = 'rgb255',\
                color = par['bgColor'],\
                fullscr = par['fullscreen'],\
                screen = par['screenNr'])
par['refreshRate'] = win.getActualFrameRate()

#==============================================================================
# Initiate eye-Tracker
#==============================================================================
tracker = pl.eyeLink(win, fileName = 'XX.EDF')
par['trackerMode'] = tracker.mode
tracker.calibrate()

# =============================================================================
# Append all parameters to the experiment dataframes
# =============================================================================
for key in par.keys():
    expList[key] = [par[key] for x in range(0,len(expList))]


def makePhillipsPattern(imVect,x,y,px=1,c1=[255,255,255],c2=[0,0,0]):
    '''
    '''
    arr = imVect.reshape((x,y))
    arr = arr.repeat(px,axis = 0)
    arr = arr.repeat(px,axis = 1)
    collArr = np.zeros((arr.shape[0], arr.shape[1], 3))
    for idx, c in enumerate([c1, c2]):
        collArr[:,:,0][arr == idx] = c[0]
        collArr[:,:,1][arr == idx] = c[1]
        collArr[:,:,2][arr == idx] = c[2]
    return imVect, collArr   

def getRandomPhilIm(x,y, px, c1, c2): 
    vect = np.random.randint(0,2,x*y)
    philVect, philPattern = makePhillipsPattern(vect,x,y,px,c1,c2)
    philPattern = scipy.misc.toimage(philPattern)
    return philPattern

philPattern = getRandomPhilIm(par['philX'], par['philY'], par['philSize'], 
                              par['philCol1'], par['philCol2'])

# =============================================================================
# Initiate stimuli objects
# =============================================================================
fixDot = visual.Circle(win,\
                radius = par['fixDotSize'],\
                fillColorSpace = 'rgb255',
                lineColorSpace = 'rgb255',\
                lineColor = par['fixDotColor'],
                fillColor = par['fixDotColor'],\
                edges = par['edges'],\
                pos = [0,0])

targDot = visual.Circle(win,\
                radius = par['targDotSize'],\
                fillColorSpace = 'rgb255',
                lineColorSpace = 'rgb255',\
                lineColor = par['targDotColor'],
                fillColor = par['targDotColor'],\
                edges = par['edges'],\
                pos = [0,0])

gazeDot = visual.Circle(win,\
                radius = par['gazeSize'],\
                fillColorSpace = 'rgb255',
                lineColorSpace = 'rgb255',\
                lineColor = par['gazeColor'],
                fillColor = par['gazeColor'],\
                edges = par['edges'],\
                pos = [0,0])

philStim = visual.ImageStim(win, philPattern, size = philPattern.size)

# =============================================================================
# Make the experiment function
# =============================================================================
def runExp(tl):
    tNr = len(tl)
    tCor = np.zeros(tNr, dtype = bool)
    tIncor = tCor.copy()
    ABORT = False
    for i in range(len(tl)):
        # =====================================================================
        # Prep trial
        # =====================================================================
        fixPos = [ps* tl.pxPerDeg[0] for ps in tl.fixDotPos[i]]
        fixPos = ((np.random.random(2)-0.5)*2)*8*tl.pxPerDeg[0]
        fixDot.pos = fixPos
        fixDot.pos = [0,0]
        
        targPos = [ps* tl.pxPerDeg[0] for ps in tl[tl.endPos[i]+'FixPos'][i]]
        targDot.pos = targPos
        
        philPattern = getRandomPhilIm(par['philX'], par['philY'], par['philSize'], 
                              par['philCol1'], par['philCol2'])
        philStim.setImage(philPattern)
        philStim.pos = targPos
        
        shift = (np.random.randint(1,4)*tl.pxPerDeg[0])*([1,-1][np.random.randint(0,2)])
        targPos2 = [targPos[0]+shift, targPos[1]]
        #======================================================================
        # Display fixdot and wait for fixation
        #======================================================================
        # Gaze contingent start
        tracker.drawFixBoundry(fixPos[0], fixPos[1], tl.hitDistance[0]*tl.pxPerDeg[0]*2)
        pl.waitForFixation(win, tracker, fixDot, tl.hitDistance[0]*tl.pxPerDeg[0], 
                           tl.maxWaitForFix[0])

        tracker.startTrial()
        # Keep track of trial information for the researcher
        block = tl.blockType[i]
        nCor = np.sum(tCor)
        nIncor = np.sum(tIncor)
        trLeft = tNr-(i)
        tracker.drawTrialInfo(block,i+1,nCor,nIncor,trLeft)
        tracker.drawFixBoundry(targPos[0], targPos[1], tl.hitDistance[0]*tl.pxPerDeg[0]*2)
        time.sleep(1)
        
        #======================================================================
        # Start trial
        #======================================================================
        #philStim.setAutoDraw(True)
        fixDot.setAutoDraw(True)
        targDot.setAutoDraw(True)
        gazeDot.setAutoDraw(True)
        corTrial = False
        
        # Keep running trial and draw gaze position
        startTrial = time.time()
        while time.time()-startTrial < tl.maxDur[0]:
            gazePos = tracker.getCurSamp()
            gazeDot.pos = gazePos
            targDist = pl.distBetweenPoints(targDot.pos, gazePos)/tl.pxPerDeg[0]
            fixDist = pl.distBetweenPoints(fixDot.pos, gazePos)/tl.pxPerDeg[0]
            
#            if fixDist > 2.5:
#                targDot.setAutoDraw(False)
#                philStim.pos = targPos2
#                win.flip()  
#                break
            
            # Check if target hit
            if targDist <= tl.hitDistance[0]:
                corTrial = True
                tCor[i] = True
                break
            
            # Check abort
            if tracker.checkAbort():
                ABORT = True
                break
            # flip 
            win.flip()
        
        #time.sleep(0.25)
        
        # If timeout or break
        if corTrial == False:
            tIncor[i] = True
        else:
            wait = time.time()
            while time.time() - wait < 0.5:
                gazePos = tracker.getCurSamp()
                gazeDot.pos = gazePos
                win.flip()
                
        philStim.setAutoDraw(False)
        fixDot.setAutoDraw(False)
        targDot.setAutoDraw(False)
        gazeDot.setAutoDraw(False)
        win.flip()
        
        tracker.sendMsg('var '+str(corTrial))
        
        # Send stop message
        tracker.stopTrial()
        
        # Check abort
        if tracker.checkAbort():
            ABORT = True
            break
        
        if ABORT == True:
            break
        
    return tl

# =============================================================================
# Run experiment
# =============================================================================
try:
    expList = runExp(expList)
    pl.cleanUp(win, tracker)
except:
    pl.cleanUp(win, tracker)
    traceback.format_exc()
    print 'ERROR'
    print traceback.format_exc() 





