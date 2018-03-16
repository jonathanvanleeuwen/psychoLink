# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 11:05:10 2018

@author: Jonathan van Leeuwen, 2018
"""
#==============================================================================
# Import modules
#==============================================================================
from psychopy import visual, monitors
import sys
import os
import numpy as np
import time
import ntpath
psychoLinkDir =['D:\Git Code\psychoLink\PsychoLink']
psychoLinkDir.append('C:\Git Code\psychoLink\PsychoLink')
[sys.path.append(d) for d in psychoLinkDir]
import psychoLink as pl
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#==============================================================================
# Initiate settings and get pp info
#==============================================================================
par = {}
par['expName'] = 'PredictingMovementExp1_targetJump'
# Get participant information
info = pl.getParticipantInfo()
info.classRun()
par['ppNr'] = info.ppNr
par['sessionNr'] = info.sessionNr
par['ppGender'] = info.gender
par['ppHandedness'] = info.handedness
par['ppOccCorrection'] = info.occularCorrection
par['ppLeftEye'] = info.leftEyeCorrection
par['ppRightEye'] = info.rightEyeCorrection
par['ppBirthDay'] = info.birthDay
par['curDate'] = info.currentDate
saveAs = info.saveAs
saveExpFile = saveAs + 'expData.p'
eFile = path_leaf(saveAs) + '.EDF'

# Define save directory
dDir = os.path.split(os.path.split(os.path.abspath(saveExpFile))[0])[0]                    
dDir += '\\Data\\'            
saveExpFile  = dDir+saveExpFile   

# Check if file exists
if os.path.isfile(saveExpFile) or os.path.isfile(dDir+eFile):
    itt = 1
    while itt < 100:
        saveExpFile = dDir+saveAs + 'expData' +  str(itt) + '.p'
        eFile = path_leaf(saveAs) +  '_' +str(itt) + '.EDF'
        fileFound = os.path.isfile(saveExpFile) or os.path.isfile(dDir+eFile)
        itt += 1
        if fileFound == False:
            break 
    
#==============================================================================
# Define settings
#==============================================================================
# Monitor
par['widthCm'] = 47.5
par['screenDistCm'] = 70.0
par['units'] = 'pix'

# window
par['resolution'] = (1920,1080) #(1680 , 1050)
par['bgColor'] = [150, 150, 150]
par['screenNr'] = 0
par['fullscreen'] = False
par['pxPerDeg'] = pl.angleToPixels(1,
                    par['screenDistCm'], par['widthCm'], par['resolution'])

# fixDot settings
par['fixDotColor'] = [0, 0, 0]
par['fixDotPos'] = [0,0]
par['fixDotSize'] = 0.1 # Deg
par['edges'] = 50 # number of lines to use for circle
   
# Search circles settings
par['circColor'] = [0, 0, 255]
par['circSize'] = 0.5 # Deg
par['circLineWidth'] = 0.05# Deg
par['searchRad'] = 6 #deg

# targCirc settings
par['targCircColor'] = [255, 0, 0]
   
# distrCirc settings
par['distrCircColor'] = [0, 255, 0]

# Experiment settings 
par['hitDistance'] = 0.5 # Deg
par['maxWaitForFix'] = 4 # Seconds
par['targetOnset'] = [250, 750] # Interval for target onset (ms)
par['maxTrialTime'] = 3 # Aborts after XX seconds
par['shuffleCircPos'] = True # circle pattern shifts

#==============================================================================
# Define block  
#==============================================================================
par['reps'] = 0 # 0 = no repetitions
par['shuffleConds'] = True
cond1 = [3,4,5,6,7,8]
cond2 = ['yes', 'no']
conds = [cond1, cond2]
header = ['nrCircs','distrPresent']

# Extra header names (will be filled with zeros, use this for logging data)
zeroHeaders = ['trialNr', 'targXPos', 'targYPos', 'distXPos', 'distYPos',
               'corrFix', 'blockType', 'tCor', 'tIncor', 'hitTime']
zeroPads = len(zeroHeaders)
header = header + zeroHeaders

blockList = pl.makeTrialList(header, conds, par['reps'], zeroPads, 
                             par['shuffleConds'])
blockList['trialNr'] = range(1,len(blockList)+1)   
blockList['block'] = 'Exp'
   
#==============================================================================
# Define which variables/settings to log to .EDF
#==============================================================================
par['logList'] = ['trialNr', 'targXPos', 'targYPos', 'distXPos', 'distYPos',
               'corrFix', 'nrCircs', 'distrPresent', 'blockType', 'tCor', 
               'tIncor', 'hitTime']
   
#==============================================================================
# Initiate screen and monitor
#==============================================================================
# Create monitor
mon = monitors.Monitor('testMonitor',width = par['widthCm'], 
                       distance = par['screenDistCm'])
# Create the window with the specified settings, giving mon as the monitor
win = visual.Window(units = par['units'],\
                monitor = mon,\
                size = par['resolution'],\
                colorSpace = 'rgb255',\
                color = par['bgColor'],\
                fullscr = par['fullscreen'],\
                screen = par['screenNr'])
   
#==============================================================================
# Initiate eye-Tracker
#==============================================================================
tracker = pl.eyeLink(win,fileName = eFile)
tracker.fileDest = dDir
tracker.setCalibrationOptions(foreCol=par['fixDotColor'], backCol=win.color)
tracker.calibrate() 

#==============================================================================
# initiate fixation dot and circles
#==============================================================================
fixDot = visual.Circle(win,\
                radius = par['fixDotSize']*par['pxPerDeg'],\
                fillColorSpace = 'rgb255',
                lineColorSpace = 'rgb255',\
                lineColor = par['fixDotColor'],
                fillColor = par['fixDotColor'],\
                edges = par['edges'],\
                pos = [0,0])   

circ = visual.Circle(win,\
                radius = par['circSize']*par['pxPerDeg'],\
                lineWidth = par['circLineWidth']*par['pxPerDeg'],\
                fillColorSpace = 'rgb255',
                lineColorSpace = 'rgb255',\
                lineColor = par['circColor'],
                fillColor = win.color,\
                edges = par['edges'],\
                pos = [0,0])   

#==============================================================================
# Append all settings to the block dataframe 
#==============================================================================
for key in par.keys():
    blockList[key] = [par[key] for x in range(0,len(blockList))]
  
    
#==============================================================================
# Function for drawing the stimulus display
#==============================================================================
def drawStim(fixPos, targPos, distrPos, circPositions, i, tl):
    fixDot.setPos(fixPos)
    fixDot.draw()
    # Draw circles
    circ.setLineColor(tl.circColor[i])
    for x,y in circPositions:
        circ.setPos((x,y))
        circ.draw()
        fixDot.setPos((x,y))
        fixDot.draw()
    # Draw target circle
    circ.setLineColor(tl.targCircColor[i])
    circ.setPos(targPos)
    circ.draw()
    fixDot.setPos(targPos)
    fixDot.draw()
    # Draw distractor
    if tl.distrPresent[i] == 'yes':
        circ.setLineColor(tl.distrCircColor[i])
        circ.setPos(distrPos)
        circ.draw()
        fixDot.setPos(distrPos)
        fixDot.draw()

#==============================================================================
#==============================================================================
# # Function for running each trial in the blocklist
#==============================================================================
#==============================================================================
def runBlock(tl): # tl = trialList
    # Set tCor and tIncor to int instead of string
    tl.tCor = 0
    tl.tIncor = 0
            
    #==========================================================================
    # Run each trial
    #==========================================================================
    for i in range(len(tl)):
        #======================================================================
        # Prep trial
        #======================================================================
        circPositions = pl.makeCircleGrid(0,0,
                                          tl.searchRad[i]*tl.pxPerDeg[i],
                                          int(tl.nrCircs[i]),
                                          tl.shuffleCircPos[i])
        # Shuffle circle positions in place
        np.random.shuffle(circPositions)
        
        # Get fixation dot pos
        fixX, fixY = tl.fixDotPos[i]
        fixDot.setPos((fixX, fixY))
        
        # Get target position
        targXPos, targYPos = circPositions.pop()
        
        # Get distractor position 
        if tl.distrPresent[i] == 'yes':
            distXPos, distYPos = circPositions.pop()
        else:
            distXPos, distYPos = (999,999) # If no distractor
        
        # Get start duration
        sDur = np.random.randint(tl.targetOnset[i][0], tl.targetOnset[i][1])
        
        #======================================================================
        # Gaze contingent start of the trial
        #======================================================================
        # Waits for gaze sample within boundry 
        corrFix = tracker.waitForFixation(fixDot, 
                                          tl.hitDistance[0]*tl.pxPerDeg[0], 
                                          tl.maxWaitForFix[0])
        
        # Initiate eyetracker and start recording 
        tracker.startTrial(i+1)
        
        #======================================================================
        # Keep track of trial information for the researcher
        #======================================================================
        # Get trial info
        block = tl.blockType[i]
        nCor = np.sum(tl.tCor)
        nIncor = np.sum(tl.tIncor)
        trLeft = len(tl)-(i)
        
        # Draw trial info
        tracker.drawTrialInfo(block,i+1,nCor,nIncor,trLeft)
        
        # Draw fixation dot on Host PC
        tracker.drawFixBoundry(fixDot.pos[0], fixDot.pos[1], 
                               tl.hitDistance[0]*tl.pxPerDeg[0])
        
        # Draw target circle  on Host PC
        tracker.drawFixBoundry(targXPos, targYPos, 
                               tl.circSize[0]*tl.pxPerDeg[0], [1,4])
        
        # Draw distractor dot on Host PC
        tracker.drawFixBoundry(distXPos, distYPos, 
                               tl.circSize[0]*tl.pxPerDeg[0], [3,4])
    
        #======================================================================
        # Now we actually run the trial
        #======================================================================
        # Draw and display fixDot
        fixDot.setPos((fixX, fixY))
        fixDot.draw()
        win.flip()
        
        ###
        # Draw stimulus display
        drawStim((fixX, fixY), (targXPos, targYPos), (distXPos, distYPos), 
                 circPositions, i, tl)
            
        # Wait before we display target onset
        time.sleep(sDur/1000.0)
        
        # Send message to the eyetracker when we display the search display
        win.callOnFlip(tracker.sendMsg, 'searchOnset')
        onsetT = win.flip()
        
        # Run gaze contingent code 
        searchOnset = time.time()
        while time.time() - searchOnset < tl.maxTrialTime[i]:
            # Get gaze position and distance from fixation, target and distr
            gazePos = tracker.getCurSamp()
            fixDist = pl.distBetweenPoints((fixX, fixY), gazePos)
            fixDist /= tl.pxPerDeg[i]
            targDist = pl.distBetweenPoints((targXPos, targYPos), gazePos)
            targDist /= tl.pxPerDeg[i] 
            distrDist = pl.distBetweenPoints((distXPos, distYPos), gazePos)
            distrDist /= tl.pxPerDeg[i] 
            circleDists = [pl.distBetweenPoints(xy, gazePos) for xy in \
                           circPositions]
            circleDists = [dist/tl.pxPerDeg[i] for dist in circleDists]
            
            # Check that the gaze is still on the fixation dot 30ms after onset
            searchTime = ((time.time()-searchOnset)*1000.0)
            if fixDist > tl.hitDistance[i] and searchTime < 30:
                tl.set_value(i, 'tIncor', 1)
                win.callOnFlip(tracker.sendMsg, 'searchOffset')
                offsetT = win.flip()
                break
            
            # Check if gaze is on target
            if targDist < tl.hitDistance[i]:
                tl.set_value(i, 'tCor', 1)
                win.callOnFlip(tracker.sendMsg, 'searchOffset')
                offsetT = win.flip()
                break
            
            # Check if gaze is on distractor
            if distrDist < tl.hitDistance[i]:
                tl.set_value(i, 'tIncor', 1)
                win.callOnFlip(tracker.sendMsg, 'searchOffset')
                offsetT = win.flip()
                break
            
            # Check if gaze is on any of the circles
            if np.sum(np.array(circleDists) < tl.hitDistance[i]) > 0:
                tl.set_value(i, 'tIncor', 1)
                win.callOnFlip(tracker.sendMsg, 'searchOffset')
                offsetT = win.flip()
                break
            
            # If running in dummy mode mouse sampling needs flips
            if tracker.mode == 'Dummy':
                # Dont clear the buffer
                drawStim((fixX, fixY), (targXPos, targYPos), 
                         (distXPos, distYPos), circPositions, i, tl)
                win.flip()
        else:
            win.callOnFlip(tracker.sendMsg, 'searchOffset')
            tl.set_value(i, 'tIncor', 1)
            offsetT = win.flip()
        
        # Set incorrect trial if not correct trial
        if tl.tCor[i] == 0:
            tl.set_value(i, 'tIncor', 1)
        
        #======================================================================
        # Log all the data to the blocklist (which are not allready set)
        #======================================================================
        tl.set_value(i, 'corrFix', corrFix)
        tl.set_value(i, 'targXPos', targXPos)
        tl.set_value(i, 'targYPos', targYPos)
        tl.set_value(i, 'distXPos', distXPos)
        tl.set_value(i, 'distYPos', distYPos)
        tl.set_value(i, 'hitTime', offsetT-onsetT)
        
        #======================================================================
        # Send all the data to the eyelink log
        #======================================================================
        # Log experiment settings to edf file 
        for ii in xrange(0,len(tl.logList[0])):
            varName = tl.logList[0][ii]
            value = tl[varName][i]
            tracker.logVar(varName,value)
            
        #======================================================================
        # Trial cleanup
        #======================================================================
        # Send stop message
        tracker.stopTrial()
        
        # Check if user has aborted 
        if tracker.checkAbort():
            break
        
    #==========================================================================
    # Truncate the trial List if it was aborted (removes the remaining rows)
    #==========================================================================
    if tracker.ABORTED:
        tl = tl.loc[:i]
        
    return tl

#==============================================================================
# Display some instructions
#==============================================================================
pl.drawText(win, 'Look at the red dot!\n\nPress "SPACE" to start')

#==============================================================================
# Run the block
#==============================================================================
blockList = runBlock(blockList)

#==============================================================================
# Save the experiment data
#==============================================================================
blockList.to_pickle(saveExpFile)
   
#==============================================================================
# Exit eyetracker, get .edf and cleanup pyshcopy + eyelink
#==============================================================================
tracker.cleanUp()
   
   