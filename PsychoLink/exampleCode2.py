# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 15:59:36 2018

@author: Jonathan
"""

import psychoLink as pl
from psychopy import visual, monitors
import pandas as pd
import numpy as np
import time
import traceback

# =============================================================================
# Settings
# =============================================================================
par = {}
# Monitor
par['widthCm'] = 47.5
par['screenDistCm'] = 70.0
par['units'] = 'pix'

# window
par['resolution'] = (1680,1050) #(1680 , 1050)
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

# gazeDot settings
par['gazeColor'] = [0, 0, 255]
par['gazeSize'] = 10

# Experiment settings
par['maxWaitForFix'] = 3
par['hitDistance'] = 2
par['maxDur'] = 4
par['logList'] = ['tCor', 'tIncor', 'blockType', 'corrFix', 'endPos']

# Conditions and header information
par['expReps'] = 10
par['nrRepsPerBlock'] = 8
cond1 = ['left', 'right']
conds = [cond1]
header = ['endPos']

# Extra header names (will be filled with zeros, use this for logging data)
zeroHeaders = ['tNr','tCor', 'tIncor', 'blockType', 'corrFix']
zeroPads = len(zeroHeaders)
header = header + zeroHeaders

# make trialList 
expList = pl.makeTrialList(header, conds, zeroPads = zeroPads, \
                        reps = par['expReps'], shuffle = True)
expList['blockType'] = 'Exp'
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

# =============================================================================
# Make the experiment function
# =============================================================================
def runExp(tl):
    tNr = len(tl)
    tCor = np.zeros(tNr, dtype = bool)
    tIncor = tCor.copy()
    for i in range(len(tl)):
        # =====================================================================
        # Prep trial
        # =====================================================================
        fixPos = [ps* tl.pxPerDeg[0] for ps in tl.fixDotPos[i]]
        fixPos = ((np.random.random(2)-0.5)*2)*8*tl.pxPerDeg[0]
        fixDot.pos = fixPos
        
        targPos = [ps* tl.pxPerDeg[0] for ps in tl[tl.endPos[i]+'FixPos'][i]]
        targDot.pos = targPos
        
        #======================================================================
        # Display fixdot and wait for fixation
        #======================================================================
        # Gaze contingent start
        corrFix = tracker.waitForFixation(fixDot, tl.hitDistance[0]*tl.pxPerDeg[0], 
                           tl.maxWaitForFix[0])
        tl.set_value(i, 'corrFix', corrFix)

        tracker.startTrial()
        # Keep track of trial information for the researcher
        block = tl.blockType[i]
        nCor = np.sum(tCor)
        nIncor = np.sum(tIncor)
        trLeft = tNr-(i)
        tracker.drawTrialInfo(block,i+1,nCor,nIncor,trLeft)
        tracker.drawFixBoundry(fixPos[0], fixPos[1], tl.hitDistance[0]*tl.pxPerDeg[0])
        tracker.drawFixBoundry(targPos[0], targPos[1], tl.hitDistance[0]*tl.pxPerDeg[0])
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
            
            # Check if target hit
            if targDist <= tl.hitDistance[0]:
                corTrial = True
                tCor[i] = True
                break
            
            # Check abort
            if tracker.checkAbort():
                break
            
            # flip 
            win.flip()
        
        # If timeout or break
        if corTrial == False:
            tIncor[i] = True
        else:
            wait = time.time()
            while time.time() - wait < 0.5:
                gazePos = tracker.getCurSamp()
                gazeDot.pos = gazePos
                win.flip()
                
        fixDot.setAutoDraw(False)
        targDot.setAutoDraw(False)
        gazeDot.setAutoDraw(False)
        win.flip()
        
        #======================================================================
        # Send all the data to the eyelink log
        #======================================================================
        # Log experiment settings to edf file 
        for ii in xrange(0,len(tl.logList[0])):
            tracker.sendMsg('var '+str(tl.logList[0][ii])+' '+ str(tl[tl.logList[0][ii]][i]))
        
        # Send stop message
        tracker.stopTrial()
        
        # Check abort
        if tracker.checkAbort():
            break
        
        if tracker.ABORTED:
            break
        
    return tl

# =============================================================================
# Run experiment
# =============================================================================
try:
    expList = runExp(expList)
    tracker.cleanUp()
except:
    tracker.cleanUp()
    traceback.format_exc()
    print 'ERROR'
    print traceback.format_exc() 





