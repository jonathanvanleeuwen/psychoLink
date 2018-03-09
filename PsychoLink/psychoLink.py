# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 16:00:17 2018

@author: Jonathan
"""
import pylink as pl
import time
import numpy as np
from psychopy import visual, core, event
import os
import sys
import pandas as pd
import Tkinter as tk
import tkFileDialog as filedialog
import scipy
from scipy import misc
import psychopy
import tempfile
import math

# =============================================================================
# To Do:
# =============================================================================#
# 1:    Test the code with different resolutions
#
# 2:    Run an experiment and parse the data to check that everything is 
#       logged correctly
#
# =============================================================================
# Print instructions
# =============================================================================
def aaPrintbasicInstructions():
    '''
    # =============================================================================\n
    # Important psycholink and tracker functions (everything is in pixel values)\n
    # \n
    # These are the most important functions when using psychoLink for \n
    # running and experiment    \n
    #    \n
    # It has additional functions, check the psycholink.py file or\n
    # type : 'tracker.' and then press "tab"\n
    # type : 'pl.' and then press "tab" \n
    # This should give you the additional options \n
    #    \n
    # =============================================================================\n
    # Initiate eyetracker\n
    tracker = pl.eyeLink(win) # win = psychopy window\n
    # Optional, set specific options for calibration\n
    tracker.setCalibrationOptions()\n
    # Start calibration\n
    tracker.calibrate()\n
    # Start eyetracker before each trial, optional you can add trial number\n
    tracker.startTrial()\n
    # Wait for fixation on fixation dot, additional options to make things pretty, \n
    # this part waits for any sample within boundry, if not fixation returns to calibration window\n
    tracker.waitForFixation(win, tracker, fixDot)\n
    # Draw info about fixation boundries on the eylink computer screen (square)\n
    tracker.drawFixBoundry(fixX,fixY, maxFixDist)\n
    tracker.drawFixBoundry(targX,targY, maxTargHitDist)\n
    # Draw trial info on eyelink computer screen\n
    tracker.drawTrialInfo(blockType,tNr,nCor,nIncor,trLeft)\n
    # Get current eyePosition\n
    tracker.getCurSamp()\n
    # Wait for end of saccade, specify how long to wait for the end of a saccade\n
    tracker.getEsacc(blockDuration)\n
    # Wait for a fixation to start (this waits for an actual fixation event, and \n
    # does not draw circles and reset to calibration)\n
    tracker.waitForFixStart(fixXY)\n
    # Get the euclidian distance between two points, e.g. gaze and fixation\n
    pl.distBetweenPoints(point1XY, point2XY)\n
    # Send a message to the EDF file (usefull for saving data, automatically waits 2 ms after sending info)\n
    tracker.sendMsg('var '+str(variable))\n
    win.callOnFlip(tracker.sendMsg, 'var '+str(variable)) # if message should be simultaniously with flip\n
    # Check if the escape button has been pressed\n
    pl.checkAbort()\n
    tracker.checkAbort() # This also draws "exit?"\n
    # Stop eyetracker, after each trial\n
    tracker.stopTrial()\n
    # After the experiment or when the experiment is aborted (transfers data and closes graphics)\n
    tracker.cleanUp(win, tracker)\n
    '''
    instructions = '''
    # =============================================================================\n
    # Important psycholink and tracker functions (everything is in pixel values)\n
    # \n
    # These are the most important functions when using psychoLink for \n
    # running and experiment    \n
    #    \n
    # It has additional functions, check the psycholink.py file or\n
    # type : 'tracker.' and then press "tab"\n
    # type : 'pl.' and then press "tab" \n
    # This should give you the additional options \n
    #    \n
    # =============================================================================\n
    # Initiate eyetracker\n
    tracker = pl.eyeLink(win) # win = psychopy window\n
    # Optional, set specific options for calibration\n
    tracker.setCalibrationOptions()\n
    # Start calibration\n
    tracker.calibrate()\n
    # Start eyetracker before each trial, optional you can add trial number\n
    tracker.startTrial()\n
    # Wait for fixation on fixation dot, additional options to make things pretty, \n
    # this part waits for any sample within boundry, if not fixation returns to calibration window\n
    tracker.waitForFixation(win, tracker, fixDot)\n
    # Draw info about fixation boundries on the eylink computer screen (square)\n
    tracker.drawFixBoundry(fixX,fixY, maxFixDist)\n
    tracker.drawFixBoundry(targX,targY, maxTargHitDist)\n
    # Draw trial info on eyelink computer screen\n
    tracker.drawTrialInfo(blockType,tNr,nCor,nIncor,trLeft)\n
    # Get current eyePosition\n
    tracker.getCurSamp()\n
    # Wait for end of saccade, specify how long to wait for the end of a saccade\n
    tracker.getEsacc(blockDuration)\n
    # Wait for a fixation to start (this waits for an actual fixation event, and \n
    # does not draw circles and reset to calibration)\n
    tracker.waitForFixStart(fixXY)\n
    # Get the euclidian distance between two points, e.g. gaze and fixation\n
    pl.distBetweenPoints(point1XY, point2XY)\n
    # Send a message to the EDF file (usefull for saving data, automatically waits 2 ms after sending info)\n
    tracker.sendMsg('var '+str(variable))\n
    win.callOnFlip(tracker.sendMsg, 'var '+str(variable)) # if message should be simultaniously with flip\n
    # Check if the escape button has been pressed\n
    pl.checkAbort()\n
    tracker.checkAbort() # This also draws "exit?"\n
    # Stop eyetracker, after each trial\n
    tracker.stopTrial()\n
    # After the experiment or when the experiment is aborted (transfers data and closes graphics)\n
    tracker.cleanUp()\n
    '''
    print instructions
# =============================================================================
# Required functions
# =============================================================================
def distBetweenPoints(point1, point2):
	'''
	'''
	dist = np.sqrt( (point1[0]-point2[0])**2 + (point1[1] - point2[1])**2 )
	return dist

def determineAngle(p1, p2):
	'''
	'''
	normx = ((p2[0] - p1[0]))
	normy = ((p2[1] - p1[1]))
	narcdeg = math.atan2(normy, normx)
	sdegree = ((narcdeg * 180)/math.pi)
	return sdegree

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def circLinePos(cx = 0, cy = 0, r = 10, setsize = 50):
    '''
    Returns, x1, y11, x2, y2, to make a circle with lines \n
    '''
    # Empty list to hold positions
    circPos = []
    # Segment definitions
    anglesegment = 2*np.pi/setsize
    # creates a tupple with x,y coordinates for each position.
    for i in range(0,setsize):
        x = r * np.cos(i*anglesegment) + cx
        y = r * np.sin(i*anglesegment) + cy
        circPos.append( (x,y) )
    arr1 = np.array(circPos)
    arr2 = np.roll(arr1,1, 0)
    return arr1[:,0], arr1[:,1], arr2[:,0], arr2[:,1]

def getKey(allowedKeys = ['left', 'right'], waitForKey = True, timeOut = 0):
    """ """
    if waitForKey:
        while True:
            # Get key
            if timeOut > 0:
                key_pressed = event.waitKeys(maxWait = timeOut, timeStamped=True)
                if key_pressed == None:
                    key_pressed = [['NoKey', 9999]]
                    break
            else:
                key_pressed = event.waitKeys(maxWait = float('inf'), timeStamped=True)
            # Check last key
            if key_pressed[-1][0] == 'escape':
                break
            if key_pressed[-1][0] in allowedKeys:
                break

    else:
        # Get key
        key_pressed = event.getKeys(timeStamped=True)
        if not key_pressed:
            key_pressed = [['NoKey']]

    return key_pressed[-1]

def drawText(win,\
			text = 'No text specified!',\
			textKey 	= ['space'],\
			wrapWidth = 900,\
			textSize 	= 25,\
			textColor = [0, 0, 0]):
    '''
    '''
    
    if np.sum(np.array(textColor) == 0) ==3 and np.sum(win.color < 100) == 3:
        textColor = [255,255,255]
    
    textDisp = visual.TextStim(win, text = text, wrapWidth = wrapWidth,
				    height = textSize, colorSpace = 'rgb255',
				    color = textColor)
    textDisp.draw()
    time = core.Clock()
    win.flip()
    if isNumber(textKey[0]):
        core.wait(textKey[0])
        key = ['NoKey']
    else:
        key = getKey(textKey)
    rt = time.getTime()
    return key[0], rt

def checkAbort():
	""" """
	keys = event.getKeys()
	if keys:
		if 'escape' in keys:
			return True
            
def angleToPixels(angle, screenDist, screenW, screenXY):
    '''
    Function which calculates viusal angle to pixels
    Input:
        angle       = visual angle in degrees
        screenDist  = distance from screen in cm
        screenW     = The width of the screen in cm
        sceenXY     = tuple with the xy resolution of the screen in pixels

    Output:
        pix         = The number of pixels (Horizontal) which is spanned by the angle
    '''
    pixSize     = screenW / float(screenXY[0])
    angle       = np.radians(angle/2.0)
    cmOnScreen  = np.tan(angle) * float(screenDist)
    pix         = (cmOnScreen/pixSize)*2

    return pix

def pixelsToAngle(pix, screenDist, screenW, screenXY):
    '''
    Function which calculates number of pixels on screen to visual degree
    Input:
        pix         = visual angle in degrees
        screenDist  = distance from screen in cm
        screenW     = The width of the screen in cm
        sceenXY     = tuple with the xy resolution of the screen in pixels

    Output:
        angle       = The angle spanned (Horizontal) by the number of pixels
    '''
    pixSize     = screenW / float(screenXY[0])
    cmOnScreen  = (pix/2.0) * pixSize
    angle       = np.rad2deg(np.arctan(cmOnScreen / screenDist))*2.0

    return angle

def makeTrialList(header, conditions, reps = 0, zeroPads = 0, shuffle = True):
	'''
	Returns a numpy array with a counterbalanced trialList. \n
	Rows are individual trials while columns are conditions. \n
	\t header    = List with strings for each column \n
	\t conds    = List of lists: [[1,2,3], range(1,10)]. \n
	\t reps     = How many times the counterbalanced trialList should be \
	repeated. \n
	\t zeroPads = How many empty columns added to the right of the trialList
	\n Empty columns can be used to store trial spesific information \
	like reaction times, responses etc.
	'''
	conds = conditions[:]
	if not any(isinstance(el, list) for el in conds):
		print('A list of lists is required')

	# Add zeroPads
	for i in range(0,zeroPads):
		conds.append([False])
	# Get number of conditions (including zeroPads)
	nConds = len(conds)

	for i in range(0,nConds):
		temp = np.array(conds[i])
		# Turn vector vertical
		temp = temp.reshape(len(temp),1)

		if i == 0:
			total = temp
		else:
			total =  np.tile(total,(len(temp),1))
			temp = np.repeat(temp,len(total)/len(temp))
			temp = temp.reshape(len(temp),1)
			total = np.concatenate((total, temp),1)

	if shuffle:
		trialList = np.random.permutation(total)
	else:
		trialList = total[:]

	# Add repeats
	for i in range(0,reps):
		if shuffle:
			total 	= np.random.permutation(total)
			trialList = np.concatenate((trialList, total))
		else:
			trialList = np.concatenate((trialList, total))

	# make it a pandas dataframe
	trialList = pd.DataFrame(trialList, columns = header)
	return trialList

def cleanUp(win, tracker):
    '''
    '''
    import warnings
    warn = '\n"cleanUp()" will be removed in future versions\nUse "tracker.cleanUp()" instead!'
    warnings.warn(warn, Warning)
    drawText(win, 'Experiment Finished!\n\nTransferring data!', textKey = [0])
    tracker.stopTrial()
    if tracker.mode != 'Dummy':
        time.sleep(0.2)
        tracker.stopRecording()
        tracker.cleanUpOld()
        time.sleep(0.2) # give the tracker time to stop
        try:
            os.rename(tracker.EDFDefaultName, tracker.EDFfileName)
            print '\nEDF file was saved as', tracker.EDFfileName
        except:
            print '\nError while renaming EDF file!!'
            print tracker.EDFfileName, 'Allready exists!!'
            print 'Manually rename the file!!'
            print 'Currently saved as', tracker.EDFDefaultName, '!!'
    if tracker.mouse != False:
        tracker.mouse.setVisible(1)
    win.close()
    
def makeSquareGrid(grid_dimXY = [10, 10], x = 0, y = 0, line_lengthXY = [10, 10]):
	'''

	Returns a list of tuples with gridpositions.\n
	\t Grid shape  	= grid_dimXY[0] * grid_dimXY[1] \n
 	\t x,y    	 	= coordinates for the middle of the grid \n
 	\t line_length 	= length between each intersection [0] = x,[1] = y \n
	'''
	# Left starting position
	start_x = x - 0.5*grid_dimXY[0]*line_lengthXY[0] + 0.5*line_lengthXY[0]
	# Top starting position
	start_y = y - 0.5*grid_dimXY[1]*line_lengthXY[1] + 0.5*line_lengthXY[1]
	# For loops for making grid
	gridpositions = []
	for x_count in range(0, grid_dimXY[0]):
		current_x = start_x + x_count*line_lengthXY[0]
		for y_count in range(0, grid_dimXY[1]):
			current_y = start_y + y_count*line_lengthXY[1]
			gridpositions.append( (current_x, current_y) )
	return gridpositions

def topLeftToCenter(pointXY, screenXY, flipY = False):
    '''
    Function for switching between screen coordinate systems
    Switches from (0,0) as top left to (0,0) as center
    '''
    newX = pointXY[0] - (screenXY[0]/2.0)
    newY = (screenXY[1]/2.0) - pointXY[1]
    if flipY:
        newY *=-1
    return (newX, newY)

def centerToTopLeft(pointXY, screenXY, flipY = True):
    '''
    Function for switching between screen coordinate systems
    Switches from (0,0) as center to (0,0) as top left
    Assumes negative y values are up and positve values are down
    if flip = True, assumes negative y values are down and positive up
    '''
    newX = pointXY[0] + (screenXY[0]/2)
    if flipY == False:
        newY = pointXY[1] + (screenXY[1]/2)
    else:
        newY = (pointXY[1]*-1) + (screenXY[1]/2)
    return (newX, newY)

def calibrationValidation(win, tracker, topLeft = False, nrPoints = 9, dotColor = [0,0,0], pxPerDegree = 47, saveFile = False):
    '''
    Function for determining the accuracy of a spatial signal
    Flips the screen empty before returning
    Background has the same color as the window which is supplied.
    The median values returned for validation accuracy are determined by taking the median
    of the x and y samples from 300ms after validation dot onset until 2000ms after validation
    dot onset (median of 1700ms of samples).
    Samples are collected every 0.5ms the median is determined based on the median of the unique x and y positions

    Inputs:
        win                 = Psychopy window to draw stimuli on
        xySamp              = Function to get (x,y) smaple from (xySamp is called: "(x,y) = xySamp()")
        topLeft             = Whethe rthe xySamp needs to be transformed from top left to centre
        nrPoints            = The number of points used for validation (9, 13, 15 or 25)
        dotColor            = RGB color value list to select the dot color
        pxPerDegree         = Number of pixels per degree of visual angle

    Returns:
        validationResults   = [3,nrPoints] list,
                                1st row returns the validation point coordinates (x,y)
                                2nd row returns (x,y) tuple with the median coordinates of xySamp()
                                3rd row returns list with the pixel distance between the 1st row and 2nd row
    '''
    # Get required information from the supplied window
    xSize, ySize        = win.size
    bgColor             = win.color
    escapeKey           = ['None']
    validationResults   = []
    sampDur             = 2000
    excludeTime         = 300
    lineColor           = [0,255,0]
    gazeColor           = [255,0,0]
    textColor           = [0,0,0]
    maxFeedPos          = (300, -50)
    meanFeedPos         = (-300, -50)


    if np.sum(np.array(textColor) == 0) ==3 and np.sum(win.color < 100) == 3:
        textColor = [255,255,255]
    if np.sum(np.array(dotColor) == 0) ==3 and np.sum(win.color < 100) == 3:
        dotColor = [255,255,255]
    
    # Initiate Dots (inner and outer dot for better fixation)
    OuterDot    = visual.Circle(win,\
                radius          = 10,\
                lineWidth       = 1,\
                fillColorSpace  = 'rgb255',\
                lineColorSpace  = 'rgb255',\
                lineColor       = bgColor,\
                fillColor       = dotColor,\
                edges           = 40,\
                pos             = [0,0])

    InnerDot    = visual.Circle(win,\
                radius          = 1,\
                lineWidth       = 1,\
                fillColorSpace  = 'rgb255',\
                lineColorSpace  = 'rgb255',\
                lineColor       = bgColor,\
                fillColor       = bgColor,\
                edges           = 40,\
                pos             = [0,0])

    # Initiate line
    errorLine   = visual.Line(win,\
                start=(-0.5, -0.5),\
                end=(0.5, 0.5),\
                lineWidth       = 1,\
                lineColorSpace  = 'rgb255',\
                lineColor       = lineColor,\
                )

    # Initiate text
    text        = visual.TextStim(win,\
                text        = '',\
                colorSpace  = 'rgb255',\
                color       = textColor)

    def drawDots(point):
        OuterDot.pos = point
        OuterDot.draw()
        InnerDot.pos = point
        InnerDot.draw()

    # Make the grid depending on the number of points for calibration
    if nrPoints == 9:
        xlineLength     = (xSize-150)/2
        yLineLength     = (ySize-150)/2
        gridPoints      = makeSquareGrid([3,3], 0,0, [xlineLength, yLineLength])

    elif nrPoints == 13:
        xlineLength     = (xSize-150)/2
        yLineLength     = (ySize-150)/2
        gridPoints      = makeSquareGrid([3,3], 0,0, [xlineLength, yLineLength])
        gridPoints      += makeSquareGrid([2,2], 0,0, [xSize/2, ySize/2])

    elif nrPoints == 15:
        xlineLength     = (xSize-150)/4
        yLineLength     = (ySize-150)/2
        gridPoints      = makeSquareGrid([5,3], 0,0, [xlineLength, yLineLength])

    elif nrPoints == 25:
        xlineLength     = (xSize-150)/4
        yLineLength     = (ySize-150)/4
        gridPoints      = makeSquareGrid([5,5], 0,0, [xlineLength, yLineLength])

    else:
        text.text           = 'Incorrect number of validation points,\n please try again with a different number'
        text.pos            = (0,0)
        text.draw()
        win.flip()
        time.sleep(3)
        return validationResults

    # start eyetracker
    tracker.startRecording()
    # Initiate an empty list to store the gaze positions and shuffle points
    gazePositions   = []
    errorDistance   = []
    np.random.shuffle(gridPoints)

    # remove the fixation posiiton from the gridpoints and add it as the last point
    gridPoints  = [i for i in gridPoints if i != (0.0,0.0)]
    gridPoints.append((0,0))

    # Draw the first fixation dot and wait for spacepress to start validation
    drawDots((0,0))
    win.flip()
    startKey = getKey(['space', 'escape'])
    if startKey[0] == 'escape':
        escapeKey[0] = 'escape'
        return validationResults

    # Draw the Dots dot and wait for 1 second between each dot
    for i in range(0,len(gridPoints)):
        drawDots(gridPoints[i])
        win.flip()
        xSamples  = []
        ySamples  = []
        sampStart = time.time()
        # While loop to run for a second to determine gaze position
        while (time.time() - sampStart)*1000 < sampDur:
            # Only get time points later than excludeTime
            if (time.time() - sampStart)*1000 > excludeTime:
                x, y = tracker.getCurSamp()
                xSamples.append(x)
                ySamples.append(y)
                drawDots(gridPoints[i])
                win.flip()

        # Calculate the median gaze position and distance from point
        medianXPosition = np.median(xSamples)
        medianYPosition = np.median(ySamples)
        if topLeft == True:
            medianXY        = topLeftToCenter((medianXPosition, medianYPosition), (xSize, ySize))
        else:
            medianXY        = (medianXPosition, medianYPosition)
        gazePositions.append(medianXY)
        errorDistance.append(distBetweenPoints(medianXY, gridPoints[i]))

        # Check abort
        escapeKey = getKey(['escape'], waitForKey = False)
        if escapeKey[0] == 'escape':
            break

    # Make the return value empty if escape was pressed during validation else draw results
    if escapeKey[0] == 'escape' :
        validationResults = []
    else:
        # Draw the results to the screen
        for i in range(0,len(gridPoints)):
            OuterDot.fillColor  = dotColor
            drawDots(gridPoints[i])
            OuterDot.fillColor  = gazeColor
            drawDots(gazePositions[i])
            errorLine.start     = gridPoints[i]
            errorLine.end       = gazePositions[i]
            errorLine.draw()
            # Draw the error values
            errorDeg            = errorDistance[i]/float(pxPerDegree)
            text.text           = str(np.round(errorDeg, 2)) + ' deg'
            text.pos            = (gridPoints[i][0], gridPoints[i][1] - 20)
            text.draw()

        # Draw Average and max values on screen
        maxError    = np.round(np.max(errorDistance)/float(pxPerDegree), 2)
        meanError   = np.round(np.average(errorDistance)/float(pxPerDegree), 2)
        text.text           = 'mean error: ' + str(meanError) + ' deg'
        text.pos            = meanFeedPos
        text.draw()
        text.text           = 'max error: ' + str(maxError) + ' deg'
        text.pos            = maxFeedPos
        text.draw()

        # Show Calibration screen
        win.flip()
        runAgain = getKey(['space', 'escape', 'v'])
        if runAgain[0] == 'v':
            validationResults = calibrationValidation(win, tracker, nrPoints = nrPoints, dotColor = dotColor, pxPerDegree = pxPerDegree)
        else:
            # Make the results
            validationResults = np.array([gridPoints, gazePositions, errorDistance])
            validationResults = pd.DataFrame(validationResults)
            # Save results
            if saveFile != False:
                itt = 1
                while itt < 100:
                    saveFileName = saveFile + 'Validation' + str(itt) + '.p'
                    fileFound = os.path.isfile(saveFileName)
                    if fileFound == False:
                        validationResults.to_pickle(saveFileName)
                        break
                    itt += 1
    win.flip()
    tracker.stopRecording()
    return validationResults

def waitForFixation(win, tracker, fixDot, maxDist = 0, maxWait = 4, nRings=3):
    '''
    '''
    import warnings
    warn = '\n"waitForFixation()" will be removed in future versions\nUse "tracker.waitForFixation()" instead!'
    warnings.warn(warn, Warning)
    incorrectFixationText = 'Either you are not fixating on the target or ' +\
    'the eyetracker needs to be recalibrated.\n\nPleas notify the experimenter.\n\n'+\
    'SPACE \t: Try again\n'+\
    'C \t\t: Re-calibrate\n'+\
    'V \t\t: Validate\n'+\
    'Q \t\t: Continue without fixation control'
    
    # get refreshRate of screen
    hz = win.getActualFrameRate()    
    tracker.startRecording()
    correctFixation = False
    trStart = time.time()
    if np.sum(fixDot.fillColor == win.color) == 3:
        lineColor = fixDot.lineColor
    else:
        lineColor = fixDot.fillColor
    
    # Detrmine the moving ring properties
    if  maxDist == 0:
        maxDist = tracker.pxPerDeg*2
    perimMaxRad = (maxDist)
    rad = perimMaxRad
    tracker.drawFixBoundry(fixDot.pos[0], fixDot.pos[1], rad)
    radList= []
    for i in range(int(hz/0.5)):
        rad = rad-(perimMaxRad/(hz/0.5))*(2-(rad/perimMaxRad))
        if rad >= 0:
            radList.append(rad)
    radList = np.array(radList)
    rIdx = [np.floor((len(radList)/nRings)*(i+1))-1 for i in range(nRings)]
    
    # Make the circ stim    
    concCirc = visual.Circle(win,radius=perimMaxRad,fillColorSpace='rgb255',\
                    lineColorSpace='rgb255',lineColor=lineColor,\
                    fillColor=win.color,edges=50,pos=fixDot.pos)
    
    while (time.time() - trStart) < maxWait:
        if tracker.mode != 'Dummy':
            fixation = tracker.getCurSamp()
            whatToDo = getKey(['c'], waitForKey = False)
            distance = distBetweenPoints(fixation,fixDot.pos)
            if distance < maxDist:
                correctFixation = True
                break
            if whatToDo[0] == 'c':
                break
        else:
            avgXY = tracker.getCurSamp()
            distance = distBetweenPoints(avgXY,fixDot.pos)
            if distance < maxDist:
                correctFixation = True
                break
                
        # Draw animated fix boundry                
        if time.time() - trStart > 1:
            # Get the stim radius
            radList = np.roll(radList,-1)
            rads = [radList[int(i)] for i in rIdx]
            # Draw the larger circle first
            for rad in np.sort(rads)[::-1]:
                concCirc.radius = rad
                concCirc.draw()
                if nRings == 1 and rad == np.min(radList):
                    if np.sum(concCirc.lineColor == win.color)==3:
                        concCirc.lineColor = fixDot.fillColor
                    elif np.sum(concCirc.lineColor == fixDot.fillColor) ==3:
                        concCirc.lineColor = win.color
            
        fixDot.draw()            
        win.flip()
        
        if checkAbort():
            break
    
    # only draw fixDot
    fixDot.draw()
    win.flip()
    
    # If no fixation detected
    if correctFixation == False:
        drawText(win, incorrectFixationText, textKey = [0])
        whatToDo = getKey(['c', 'space', 'q', 'v'])
        if whatToDo[0] == 'c':
            tracker.calibrate()
            correctFixation = waitForFixation(win, tracker, fixDot, maxDist, maxWait, nRings)
        elif whatToDo[0] == 'space':
            correctFixation     = waitForFixation(win, tracker, fixDot, maxDist, maxWait, nRings)
        elif whatToDo[0] == 'q' or whatToDo[0] == 'escape':
            correctFixation = False
        elif whatToDo[0] == 'v':
            calibrationValidation(win,\
                                  tracker, \
                                  nrPoints        = 9, \
                                  dotColor        = tracker.foreCol,\
                                  pxPerDegree     = tracker.pxPerDeg,\
                                  saveFile        = False)
            correctFixation = waitForFixation(win, tracker, fixDot, maxDist, maxWait, nRings)
    tracker.stopRecording()
    return correctFixation


#==============================================================================
#  TO DO:
# 	Test Code
# 	Make a calibration screen so users know what to do
#==============================================================================
class eyeLink:
    '''
    This class is intended as a handy wrapper for the pylink module.
    It has easy to use code for the most basic functionality.

    \nCurrently it supports:
    Initiating\t -\t Connects to eyeLink, or goes into dummyMode\n
    sendMsg\t -\t Sends a message to the eyeLink\n
    getCurSamp\t -\t Gets the current (x,y) coordinate\n


    \nDummy mode:
    Dummy mode uses absolute mouse (x,y) position, with (0,0) being top
    left corner. If you suply a mouse from psychopy then the screen is
    taken into account and (0,0) = middle of the psychopy window, in the
    units of the window.
    '''

    #=========================================================================
    # Initiate Eyetracker or use mouse if no eyetracker found
    #=========================================================================
    def __init__(self, win, address = "100.1.1.1", fileName = 'XX.EDF'):
        '''
        Initiates the eyetracker\n
        If no eyetracker found it initiates mouse and goes into dummy mode\n
        '''
        self.win = win
        address = str(address)
        self.EDFfileName = str(fileName)
        self.EDFDefaultName = 'XX.EDF'
        self.mouse = event.Mouse(win = win)
        self.activeState = True
        self.ABORTED = False

        try:
            # Real connection to tracker
            self.eyeLinkTracker = pl.EyeLink(address)
            self.eyeLinkTracker.openDataFile(self.EDFDefaultName)
            pl.flushGetkeyQueue()
            self.mode = 'Real'
            self.mouse.setVisible(0)
            print '\nTracker found!'
            print 'Mouse set to invissible'
            drawText(self.win, 'Press "SPACE" to setup EyeTracker!')
            self.win.flip()

        except:
            #or for dummy mode connection
            self.eyeLinkTracker = pl.EyeLink(None)
            self.mode = 'Dummy'
            error = '\n\tNo eye-tracker found at: "' + address + \
                '"\n\tEntering DummyMode\n' +\
                '\tUsing Mouse Position\n\n\tPress "Space" to start'
            print( "\nError: %s" % error )
            self.mouse.setVisible(1)
            drawText(self.win, error)
            self.win.flip()
            
            # For testing intro screen settings in dummy mode
            #introscreen = IntroScreen(self.win)
            #introscreen.draw()
            #self.win.flip()
            
        self.setEyeLinkSettings(screenW = win.size[0], screenH = win.size[1])
        self.setCalibrationOptions(backCol = win.color)
        self.pxPerDeg = angleToPixels(1, win.scrDistCM, win.scrWidthCM, win.size)
        
    #=========================================================================
    # Set settings for eyetracker
    #=========================================================================
    # Set recording parameters
    def setEyeLinkSettings(self, \
                vel = 35, \
                acc = 9500, \
                screenW = 1680, \
                screenH = 1050):
        '''
        Sets the settings for the eyeTracker\n
        '''
        self.screenW = screenW
        self.screenH = screenH
        if self.mode == 'Real':
            # Send screen info to eyelink
            self.eyeLinkTracker.sendCommand("screen_pixel_coords = 0 0 %d %d" %(screenW, screenH))
            self.eyeLinkTracker.sendMessage("DISPLAY_COORDS 0 0 %d %d" %(screenW, screenH))

            # Set saccade velocity settings
            if (self.eyeLinkTracker.getTrackerVersion()== 2):
                self.eyeLinkTracker.sendCommand("select_parser_configuration 0")
            else:
                self.eyeLinkTracker.sendCommand("saccade_velocity_threshold = "+str(vel))
                self.eyeLinkTracker.sendCommand("saccade_acceleration_threshold = "+str(acc))

            # Send events to filter to eyelink
            # Also try to record some data with HREF in the sample and link filter
            # And then try to look at the ascii file for parsing the data
            
            self.eyeLinkTracker.setFileEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
            self.eyeLinkTracker.setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
            self.eyeLinkTracker.setLinkEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
            self.eyeLinkTracker.setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")
            self.eyeLinkTracker.sendCommand("button_function 5 'accept_target_fixation'")

    #=========================================================================
    # Running drift correct and calibration procedure (make psychopy screen)
    #=========================================================================
    def setCalibrationOptions(self,\
                foreCol     = [0,0,0],\
                backCol     = [150, 150, 150],\
                calDiam     = 10,\
                holeDiam    = 2,\
                colorDepth  = 32,\
                targSound   = "on",\
                corrSound   = "on",\
                incSound    = "on",\
                caltype     = 'HV9',\
                calTime     = 1000):
        
        # Set the options
        if np.sum(np.array(backCol) < 100) == 3 and np.sum(np.array(foreCol) == 0) ==3:
            foreCol = (255,255,255)
        self.foreCol = [int(i) for i in (foreCol)]
        self.backCol = [int(i) for i in (backCol)]
        self.calDiam = int(calDiam)
        self.holeDiam = int(holeDiam)
        self.colorDepth = int(colorDepth)
        self.targSound = targSound
        self.corrSound = corrSound
        self.incSound = incSound
        self.caltype = caltype
        self.calTime = int(calTime)
        
    # Run calibration
    def calibrate(self):
        '''
        Runs the calibration
        '''
        if self.mode == 'Real':
            genv=EyeLinkCoreGraphicsPsychopy(self.win, self,
                                             targetForegroundColor=self.foreCol,
                                             targetBackgroundColor=self.backCol,
                                             screenColor=self.backCol,
                                             targetOuterDiameter=self.calDiam,
                                             targetInnerDiameter=self.holeDiam)
            pl.openGraphicsEx(genv)
            # Set number of calibration points
            self.eyeLinkTracker.sendCommand("calibration_type=%s"%self.caltype)
            # Set calibration point duration
            self.eyeLinkTracker.sendCommand("automatic_calibration_pacing=%d"%(self.calTime))
            # Set sounds
            pl.setCalibrationSounds(self.targSound, self.corrSound,self.incSound)
            self.eyeLinkTracker.doTrackerSetup()
            genv.clear_cal_display()
            self.win.flip()
            drawText(self.win, 'Press "Space" to start!')
            self.eyeLinkTracker.startRecording(1,1,1,1)
    
    # Run drift correct
    def driftCorrect(self, x,y):
        '''
        Runs  drift correction
        '''
        if self.mode == 'Real':
            genv=EyeLinkCoreGraphicsPsychopy(self.win, self,
                                             targetForegroundColor=self.foreCol,
                                             targetBackgroundColor=self.backCol,
                                             screenColor=self.backCol,
                                             targetOuterDiameter=self.calDiam,
                                             targetInnerDiameter=self.holeDiam)
            pl.openGraphicsEx(genv)
            # Set number of calibration points
            self.eyeLinkTracker.sendCommand("calibration_type=%s"%self.caltype)
            # Set calibration point duration
            self.eyeLinkTracker.sendCommand("automatic_calibration_pacing=%d"%(self.calTime))
            # Set sounds
            pl.setDriftCorrectSounds(self.targSound, self.corrSound, self.incSound)
            self.eyeLinkTracker.doDriftCorrect(x, y,1,1)
            genv.clear_cal_display()
            
    #=========================================================================
    # Methods for talking to the eytracker
    #=========================================================================
    def startTrial(self, trialNr=False):
        '''
        Starts eyetracker and sends start trial message
        '''
        self.startRecording()
        time.sleep(10/1000.0)
        self.sendMsg('start_trial')
        if trialNr != False:
            self.eyeLinkTracker.sendCommand("record_status_message=trialNr_%d"%(int(trialNr)))
        else:
            self.eyeLinkTracker.sendCommand("record_status_message=trialNr_XX")
        
    def stopTrial(self):
        '''
        Stops eyetracker and sends stop trial message
        '''
        self.sendMsg('stop_trial')
        time.sleep(10/1000.0)
        self.stopRecording()
    
    # start recording
    def startRecording(self):
        '''
        Starts recording\n
        '''
        if self.mode == 'Real':
            self.eyeLinkTracker.clearScreen(0)
            time.sleep(0.1)
            # Start Recording
            self.eyeLinkTracker.startRecording(1,1,1,1)            
            time.sleep(0.1)
            #begin the realtime mode
            #pl.pylink.beginRealTimeMode(200)

    # Stop recording
    def stopRecording(self):
        '''
        Stops recording\n
        '''
        if self.mode == 'Real':
            #pl.pylink.endRealTimeMode()
            self.eyeLinkTracker.clearScreen(0)
            self.eyeLinkTracker.stopRecording()

    # Send message to pyLinkLog
    def sendMsg(self,msg = ''):
        '''
        msg = string\n
        Sends a string (msg) to the eyeTracker log\n
        '''
        if self.mode == 'Real':
            self.eyeLinkTracker.sendMessage(str(msg))
            time.sleep(2/1000.0)
        elif self.mode == 'Dummy':
            msg = 'PsychoLink Log (Dummy): '+str(msg)
            print msg

    def getTime(self):
        '''
        Get the timestamp of the newest sample

        Returns:
            timeStamp
        '''
        timeStamp = False
        if self.mode == 'Real':
            curSamp = self.eyeLinkTracker.getNewestSample()
            timeStamp = curSamp.getTime()
        return timeStamp

    def drawFixBoundry(self, x, y, rad, bType = 'circle', color = [2,4]):
        '''
        Draws cross and fixation boundry (square)
        rad = radius
        bType = 'square' or 'circle', default = 'circle'
        color = [2,4], 2 item list, values 0-15 
        '''
        if self.mode == 'Real':
            x,y = centerToTopLeft((x,y), (self.screenW, self.screenH))
            if bType == 'square':
                rad *=2
                xL, yL = (x-rad/2, y-rad/2)
                self.eyeLinkTracker.drawBox(xL,yL,rad,rad, color[0])
            elif bType == 'circle':
                x1,y1,x2,y2 = circLinePos(x, y, rad)
                for idx, (x1,y1,x2,y2) in enumerate(zip(x1,y1,x2,y2)):
                    self.eyeLinkTracker.drawLine((x1,y1),(x2,y2),color[0])
            self.eyeLinkTracker.drawCross(x,y, color[1])
            
    def drawEyeText(self, text, pos = False):
        '''
        Draw text on the eyelink screen (no spaces for some reason)
        '''
        if self.mode == 'Real':
            if pos == False:
                x,y = centerToTopLeft((self.screenW/2, self.screenH-30), (self.screenW, self.screenH))
                self.eyeLinkTracker.drawText(text, (x,y))
            else:
                pos = centerToTopLeft(pos, (self.screenW, self.screenH))
                self.eyeLinkTracker.drawText(text, pos)
        else:
            print text
            
    def drawTrialInfo(self, block='NA', tNr=999, tCor=999, tInc=999, tLeft=999):
        '''
        Draws the trial information
        
        # Try:
            .echo(text)
            setting the pos to (column, row) e.g (10,15)
            self.eyeLinkTracker.sendCommand("draw_text=%d %d %d %s "%(0, 0, 3, text)
        '''
        block = str(block)
        text = ['block__%s'%(block),'tNr____%s'%(tNr),'tCor___%s'%(tCor),
                'tInc___%s'%(tInc),'tLeft__%s'%(tLeft)]
        if self.mode == 'Real':
            for txt in text:    
                self.eyeLinkTracker.drawText(txt)
                self.eyeLinkTracker.drawText('')
        else:
            print text
        
    # Get the newest data sample
    def getCurSamp(self):
        '''
        Returns the current (x,y) gaze position\n
        If running in dummy mode it returns mouse position\n
        '''
        if self.mode == 'Real':
            curSamp = self.eyeLinkTracker.getNewestSample()
            if curSamp != None:
                if curSamp.isRightSample():
                    gazePos = curSamp.getRightEye().getGaze()
                if curSamp.isLeftSample():
                    gazePos = curSamp.getLeftEye().getGaze()

                newGazePos = [0,0]
                newGazePos[0] = gazePos[0] - self.screenW/2
                newGazePos[1] = -(gazePos[1] - self.screenH/2)
                curSamp = newGazePos
        elif self.mode == 'Dummy':
            curSamp = tuple(self.mouse.getPos())
        return curSamp

    # Get next event
    def getEsacc(self, timeout = 4):
        '''
        Waits for the end of the next saccade (is bussy while waiting)

        Important:
            Blocks code until endsaccade is found (or timeout).
            Press escape to exit manually.

        Input:
            timeout: 4 (int), the duration to wait before code exits (seconds)

        Returns the esacc data for the last saccade in a list:
            index0: start saccade timestamp
            index1: end saccade timestamp
            index2: start saccade X
            index3: start saccade Y
            index4: end saccade X
            index5: end saccade Y

        If dummy mode or timeout:
            Returns a list of False values and does not block code
            execution.
        '''
        esacc = [False, False, False, False, False, False]
        if self.mode == 'Real':
            start = time.time()
            while True and (time.time() - start) <= timeout:
                event = self.eyeLinkTracker.getNextData()
                event = self.eyeLinkTracker.getFloatData()
                if event != None:
                    if event.getType() == 6 or checkAbort() == False:
                        esacc[0] = event.getStartTime()
                        esacc[1] = event.getEndTime()
                        esacc[2], esacc[3] = event.getStartGaze()
                        esacc[4], esacc[5] = event.getEndGaze()
                        esacc[2] -= (self.screenW/2)
                        esacc[3] = -(esacc[3] -(self.screenH/2))
                        esacc[4] -= (self.screenW/2)
                        esacc[5] = -(esacc[5] - (self.screenH/2))
                        break
        return esacc



    # Wait for fixation
    def waitForFixStart(self, fixXY = None, offset = 50, timeout = 4):
        '''
        Wait for the start of the next fixation.
        Blocks the execution of code until the start of a fixation.

        Important:
            Blocks code until startfixation is found (or timeout).
            Press escape to exit manually.
            If running dummy mode then "win" input is required

        Input:
            fixXY: None or (x,y, offset)  (int, int, int)
                  if None then it continues after a fixation is detected.
                  if (x,y) continues when start fixation is detected
                  at (x,y) coordinates with a tollerane of offset pixels.
            offset: The number of pixels offset a gaze can be from (x,y)
            timeout: 4 (int), the duration to wait before code exits (seconds)

        Returns a list:
            index0: Fixation start timestamp
            index1: Fixation start X
            index2: Fixation start Y

        If Dummy mode:
            if fixXY = None
                Returns (None, mouseX, mouseY)
            if fixXY = (x,y,offset)
                Waits until a mouse sample is within the boundry, then returns
                a list with (None, mouseX, mouseY).
                samples at refresh rate of screen

        If timeout returns [None, None, None]
        
        '''
        fix = [None, None, None]
        if self.mode == 'Real':
            start = time.time()
            while True and (time.time() - start) <= timeout:
                event = self.eyeLinkTracker.getNextData()
                event = self.eyeLinkTracker.getFloatData()
                if event != None:
                    if event.getType() == 7:
                        fixStart = event.getStartTime()
                        fixX, fixY = self.getCurSamp()
                        if fixXY == None:
                            fix[0] = fixStart
                            fix[1] = fixX-self.window.size[0]/2
                            fix[2] = -(fixY-self.window.size[1]/2)
                            break
                        dist = distBetweenPoints((fixX, fixY), fixXY)
                        if dist <= offset:
                            fix[0] = fixStart
                            fix[1] = fixX-self.window.size[0]/2
                            fix[2] = -(fixY-self.window.size[1]/2)
                            break
                if checkAbort() == True:
                    break

        elif self.mode == 'Dummy':
            if fixXY == None:
                fix[1], fix[2] = self.getCurSamp()
            else:
                start = time.time()
                while True and (time.time() - start) <= timeout:
                    mousePos = self.getCurSamp()
                    dist = distBetweenPoints(mousePos, fixXY)
                    if dist <= offset or checkAbort == True:
                        fix[1], fix[2] = mousePos
                        break
                    self.window.flip()
        return fix

    def waitForFixation(self, fixDot, maxDist = 0, maxWait = 4, nRings=3):
        '''
        '''
        incorrectFixationText = 'Either you are not fixating on the target or ' +\
        'the eyetracker needs to be recalibrated.\n\nPleas notify the experimenter.\n\n'+\
        'SPACE \t: Try again\n'+\
        'C \t\t: Re-calibrate\n'+\
        'V \t\t: Validate\n'+\
        'Q \t\t: Continue without fixation control'
        
        # get refreshRate of screen
        hz = self.win.getActualFrameRate()    
        self.startRecording()
        correctFixation = False
        trStart = time.time()
        if np.sum(fixDot.fillColor == self.win.color) == 3:
            lineColor = fixDot.lineColor
        else:
            lineColor = fixDot.fillColor
        
        # Detrmine the moving ring properties
        if  maxDist == 0:
            maxDist = self.pxPerDeg*2
        perimMaxRad = (maxDist)
        rad = perimMaxRad
        self.drawFixBoundry(fixDot.pos[0], fixDot.pos[1], rad)
        radList= []
        for i in range(int(hz/0.5)):
            rad = rad-(perimMaxRad/(hz/0.5))*(2-(rad/perimMaxRad))
            if rad >= 0:
                radList.append(rad)
        radList = np.array(radList)
        rIdx = [np.floor((len(radList)/nRings)*(i+1))-1 for i in range(nRings)]
        
        # Make the circ stim    
        concCirc = visual.Circle(self.win,radius=perimMaxRad,fillColorSpace='rgb255',\
                        lineColorSpace='rgb255',lineColor=lineColor,\
                        fillColor=self.win.color,edges=50,pos=fixDot.pos)
        
        while (time.time() - trStart) < maxWait:
            if self.mode != 'Dummy':
                fixation = self.getCurSamp()
                whatToDo = getKey(['c'], waitForKey = False)
                distance = distBetweenPoints(fixation,fixDot.pos)
                if distance < maxDist:
                    correctFixation = True
                    break
                if whatToDo[0] == 'c':
                    break
            else:
                avgXY = self.getCurSamp()
                distance = distBetweenPoints(avgXY,fixDot.pos)
                if distance < maxDist:
                    correctFixation = True
                    break
                    
            # Draw animated fix boundry                
            if time.time() - trStart > 1:
                # Get the stim radius
                radList = np.roll(radList,-1)
                rads = [radList[int(i)] for i in rIdx]
                # Draw the larger circle first
                for rad in np.sort(rads)[::-1]:
                    concCirc.radius = rad
                    concCirc.draw()
                    if nRings == 1 and rad == np.min(radList):
                        if np.sum(concCirc.lineColor == self.win.color)==3:
                            concCirc.lineColor = fixDot.fillColor
                        elif np.sum(concCirc.lineColor == fixDot.fillColor) ==3:
                            concCirc.lineColor = self.win.color
                
            fixDot.draw()            
            self.win.flip()
            
            if checkAbort():
                break
        
        # only draw fixDot
        fixDot.draw()
        self.win.flip()
        
        # If no fixation detected
        if correctFixation == False:
            drawText(self.win, incorrectFixationText, textKey = [0])
            whatToDo = getKey(['c', 'space', 'q', 'v'])
            if whatToDo[0] == 'c':
                self.calibrate()
                correctFixation = self.waitForFixation(fixDot, maxDist, maxWait, nRings)
            elif whatToDo[0] == 'space':
                correctFixation = self.waitForFixation(fixDot, maxDist, maxWait, nRings)
            elif whatToDo[0] == 'q' or whatToDo[0] == 'escape':
                correctFixation = False
            elif whatToDo[0] == 'v':
                calibrationValidation(self.win,\
                                      self, \
                                      nrPoints = 9, \
                                      dotColor = self.foreCol,\
                                      pxPerDegree = self.pxPerDeg,\
                                      saveFile = False)
                correctFixation = self.waitForFixation( fixDot, maxDist, maxWait, nRings)
        self.stopRecording()
        return correctFixation
    
    # Check abort
    def checkAbort(self):
        """ """
        keys = event.getKeys()
        if keys:
            if 'escape' in keys:
                key , rt = drawText(self.win, 'Stop Experiment?\n\nYes \t= Y \nNo \t\t= N', ['y', 'n'])
                if key == 'y' or key == 'escape':
                    self.ABORTED = True
                    return True

    # Clean up
    def cleanUp(self):
        '''
        Sets eyetracker into offline mode\n
        Closes data file\n
        Closes eyetracker conection\n
        Closes eyetracker Graphics\n
        Retrieves data file to current working directory\n
        '''
        drawText(self.win, 'Experiment Finished!\n\nTransferring data!', textKey = [0])
        self.stopTrial()
        self.activeState = False
        if self.mode == 'Real':
            if pl.tracker != None:
                time.sleep(0.2)
                self.stopRecording()
                
                # File transfer and cleanup!
                self.eyeLinkTracker.setOfflineMode()
                pl.msecDelay(500);
                #Close the file and transfer it to Display PC
                self.eyeLinkTracker.closeDataFile()
                # Suppress output printing
                _out = sys.stdout
                with open(os.devnull, 'w') as fd:
                    sys.stdout = fd
                    self.eyeLinkTracker.receiveDataFile(self.EDFDefaultName, self.EDFDefaultName)
                    sys.stdout = _out
                self.eyeLinkTracker.close()
                
                 # give the tracker time to stop
                time.sleep(0.2)
                try:
                    os.rename(self.EDFDefaultName, self.EDFfileName)
                    print '\nEDF file was saved as', self.EDFfileName
                except:
                    print '\nError while renaming EDF file!!'
                    print self.EDFfileName, 'Allready exists!!'
                    print 'Manually rename the file!!'
                    print 'Currently saved as', self.EDFDefaultName, '!!'
        if self.mouse != False:
            self.mouse.setVisible(1)
        self.win.close()
    
    def cleanUpOld(self):
        '''
        Sets eyetracker into offline mode\n
        Closes data file\n
        Closes eyetracker conection\n
        Closes eyetracker Graphics\n
        Retrieves data file to current working directory\n
        '''
        import warnings
        warn = '\n"tracker.cleanUpOld()" be removed in future versions\nUse "tracker.cleanUp()" instead!'
        warnings.warn(warn, Warning)
        
        self.activeState = False
        if self.mode == 'Real':
            if pl.tracker != None:                
                # File transfer and cleanup!
                self.eyeLinkTracker.setOfflineMode()
                pl.msecDelay(500);
                #Close the file and transfer it to Display PC
                self.eyeLinkTracker.closeDataFile()
                # Suppress output printing
                _out = sys.stdout
                with open(os.devnull, 'w') as fd:
                    sys.stdout = fd
                    self.eyeLinkTracker.receiveDataFile(self.EDFDefaultName, self.EDFDefaultName)
                    sys.stdout = _out
                self.eyeLinkTracker.close()
                
#==============================================================================
#  Make class for getting experiment info from user (incomplete)
#==============================================================================
#==============================================================================
# Enter a save filename
#==============================================================================
def giveFileName(windowName = 'Please enter Filename'):
	fileGui = tk.Tk()
	fileGui.withdraw()
	fileGui.lift()
	fileGui.attributes('-topmost', True)
	fileDir  = filedialog.asksaveasfilename(title = windowName)
	fileGui.destroy()
	return fileDir                

                
class getParticipantInfo(tk.Tk):
	'''
     Class for getting participant information
	'''
	def __init__(self):
		tk.Tk.__init__(self)
		# Set default values with the data type required
		self.title('Get participant info')
		self.xSize = 600
		self.ySize = 600
		self.padx = 10
		self.pady = 5
		self.topDist = 20
		self.borderWidth = 5
		self.textFont = ('Helvetica', 12)
		self.groupFount = ('Helvetica', 9)
		self.instruct = 'Please enter information'
		self.addToTrialParse = tk.StringVar()
		self.currentDate = time.strftime("%d/%m/%Y")
		self.saveAs = ''

	# We want to put some instructions in the GUI
	def makeInstructions(self):
		self.dispInstruct= tk.StringVar()
		self.dispInstruct.set(self.instruct)
		instr = tk.Label(self, \
			textvariable 	= self.dispInstruct, \
			font  		= self.textFont)
		instr.pack(pady = self.topDist)

	def makeExperimentInfo(self):
		subGroup= tk.LabelFrame(self, \
			text 		= 'Experiment info', \
			padx 		= self.padx, \
			pady 		= self.pady, \
			borderwidth 	= self.borderWidth,\
			font 		= self.textFont)
		subGroup.grid(row=0, columnspan=7, sticky='W', \
                 padx=5, pady=5, ipadx=5, ipady=5)
		subGroup.pack()

		# Subject nr entry
		subjectNrLabel			= tk.Label(subGroup, text="Participant Nr:")
		sessionNrLabel			= tk.Label(subGroup, text="Session Nr:")
		subjectNrLabel.grid(row=0, column=0)
		sessionNrLabel.grid(row=1, column=0)

		subjectNr 			= range(1,51)
		sessionNr 		 	= range(1,11)
		self.subjectNrOptions 	= tk.StringVar()
		self.sessionNrOptions 	= tk.StringVar()
		self.subjectNrOptions.set(subjectNr[0])
		self.sessionNrOptions.set(sessionNr[0])
		self.subjectNrEntry		= tk.OptionMenu(subGroup, self.subjectNrOptions, *subjectNr)
		self.sessionNrEntry		= tk.OptionMenu(subGroup, self.sessionNrOptions, *sessionNr)
		self.subjectNrEntry.grid(row = 0, column = 1)
		self.sessionNrEntry.grid(row = 1, column = 1)

		saveAsButton = tk.Button(subGroup, \
			text 	= "Save as", \
			command 	= self.saveFileName)
		saveAsButton.grid(row = 2, column = 1)

	def makeDemoGraph(self):
		demoGroup= tk.LabelFrame(self, \
			text 		= 'Demographics', \
			padx 		= self.padx, \
			pady 		= self.pady, \
			borderwidth 	= self.borderWidth,\
			font 		= self.textFont)
		demoGroup.grid(row=0, columnspan=7, sticky='W', \
                 padx=5, pady=5, ipadx=5, ipady=5)
		demoGroup.pack()

		# Age entry
		ageLabel 				= tk.Label(demoGroup, text="Date of birth:")
		dayLabel 				= tk.Label(demoGroup, text="day")
		monthLabel 			= tk.Label(demoGroup, text="month")
		yearLabel 			= tk.Label(demoGroup, text="year")
		ageLabel.grid(row=1, column=0)
		dayLabel.grid(row=0, column=1)
		monthLabel.grid(row=0, column=2)
		yearLabel.grid(row=0, column=3)

		day 				= range(1,32)
		month			= range(1,13)
		year 		 	= range(1960,2020)
		self.dayOptions 	= tk.StringVar()
		self.dayOptions.set(day[0])
		self.monthOptions 	= tk.StringVar()
		self.monthOptions.set(month[0])
		self.yearOptions 	= tk.StringVar()
		self.yearOptions.set(year[0])
		self.ageEntryDay	= tk.OptionMenu(demoGroup,self.dayOptions, *day)
		self.ageEntryMonth	= tk.OptionMenu(demoGroup,self.monthOptions, *month)
		self.ageEntryYear	= tk.OptionMenu(demoGroup,self.yearOptions, *year)

		self.ageEntryDay.grid(row = 1, column = 1)
		self.ageEntryMonth.grid(row = 1, column = 2)
		self.ageEntryYear.grid(row = 1, column = 3)

		# Eye entry
		eyeLabel               = tk.Label(demoGroup, text="Occular correction")
		rightEyeLabel 		= tk.Label(demoGroup, text="Right eye")
		leftEyeLabel 		= tk.Label(demoGroup, text="Left eye")
		eyeLabel.grid(row=3, column=0)
		rightEyeLabel.grid(row=2, column=2)
		leftEyeLabel.grid(row=2, column=3)

		correction 		= ['No', 'Glasses','Contacts: Soft','Contacts: Hard']
		right			= np.round(np.arange(-5,5, 0.1),2)
		left 		 	= np.round(np.arange(-5,5, 0.1),2)
		self.correctionOptions 	= tk.StringVar()
		self.correctionOptions.set(correction[0])
		self.rightOptions = tk.StringVar()
		self.rightOptions.set(0)
		self.leftOptions 	= tk.StringVar()
		self.leftOptions.set(0)
		self.correctionEntry	= tk.OptionMenu(demoGroup,self.correctionOptions, *correction)
		self.rightEntry	= tk.OptionMenu(demoGroup,self.rightOptions, *right)
		self.leftEntry	= tk.OptionMenu(demoGroup,self.leftOptions, *left)

		self.correctionEntry.grid(row = 3, column = 1)
		self.rightEntry.grid(row = 3, column = 2)
		self.leftEntry.grid(row = 3, column = 3)

		# handedness entry
		handOptions 			= ['Right', 'Left', 'Ambidextrous']
		handLabel 			= tk.Label(demoGroup, text="Handedness:")
		self.handOptions = tk.StringVar()
		self.handOptions.set(handOptions[0])
		self.handEntry 		= tk.OptionMenu(demoGroup, self.handOptions, *handOptions)
		handLabel.grid(row=4, column=0)
		self.handEntry.grid(row = 4, column = 1)

		# Gender entry
		genderOptions 			= ['Male', 'Female', 'Other']
		genderLabel 			= tk.Label(demoGroup, text="Gender:")
		self.genderOptions = tk.StringVar()
		self.genderOptions.set(genderOptions[0])
		self.genderEntry 		= tk.OptionMenu(demoGroup, self.genderOptions, *genderOptions)
		genderLabel.grid(row=5, column=0)
		self.genderEntry.grid(row = 5, column = 1)

	# make the button which closes everything
	def makeStartButton(self):
		closeButton = tk.Button(self, \
			text 	= "Start!", \
			command 	= self.start)
		closeButton.pack(side = tk.BOTTOM)

	# Here we make and then run the classifier GUI
	def classRun(self):
		self.makeInstructions()

		self.makeExperimentInfo()

		self.makeDemoGraph()

		self.makeStartButton()

		# This starts the GUI
		self.geometry('{}x{}'.format(self.xSize, self.ySize))
		self.attributes('-topmost', True)
		tk.Tk.mainloop(self)

	#=========================================================================
	# Define what happens when buttons are pressed
	#=========================================================================
	# This stops and destroys the GUI
	def start(self):
		self.ppNr 	 	= int(self.subjectNrOptions.get())
		self.sessionNr 	= int(self.sessionNrOptions.get())
		self.handedness  = self.handOptions.get()
		self.gender 	= self.genderOptions.get()
		self.birthDay 	= str(self.dayOptions.get()) + '/' + \
							str(self.monthOptions.get()) + '/' +  \
							str(self.yearOptions.get())
		self.occularCorrection	   = self.correctionOptions.get()
		self.rightEyeCorrection   = float(self.rightOptions.get())
		self.leftEyeCorrection    = float(self.leftOptions.get())

		if len(self.saveAs) == 0:
			self.saveAs 	= 'PP' + str(self.ppNr) + 'S' + str(self.sessionNr)
		self.destroy()

	def saveFileName(self):
		self.saveAs 	 	= giveFileName()
        
        
# =============================================================================
# Eyelink core graphics
# =============================================================================
class FixationTarget(object):
    def __init__(self, psychopy_eyelink_graphics):
        self.calibrationPointOuter = visual.Circle(
                                psychopy_eyelink_graphics.window,
                                pos=(0,0),
                                lineWidth=1.0,
                                lineColor=psychopy_eyelink_graphics.CALIBRATION_POINT_OUTER_COLOR,
                                lineColorSpace='rgb255',
                                fillColor=psychopy_eyelink_graphics.CALIBRATION_POINT_OUTER_COLOR,
                                fillColorSpace='rgb255',
                                radius=psychopy_eyelink_graphics.CALIBRATION_POINT_OUTER_RADIUS,
                                name='CP_OUTER',
                                units='pix',
                                opacity=1.0,
                                interpolate=False)
        self.calibrationPointInner = visual.Circle(
                                psychopy_eyelink_graphics.window,
                                pos=(0,0),lineWidth=1.0,
                                lineColor=psychopy_eyelink_graphics.CALIBRATION_POINT_INNER_COLOR,
                                lineColorSpace='rgb255',
                                fillColor=psychopy_eyelink_graphics.CALIBRATION_POINT_INNER_COLOR,
                                fillColorSpace='rgb255',
                                radius=psychopy_eyelink_graphics.CALIBRATION_POINT_INNER_RADIUS,
                                name='CP_INNER',
                                units='pix',
                                opacity=1.0,
                                interpolate=False)
    def draw(self, pos = None):
        if pos:
            self.calibrationPointOuter.pos = pos
            self.calibrationPointInner.pos = pos
        self.calibrationPointOuter.draw()
        self.calibrationPointInner.draw()


# Intro Screen
class BlankScreen(object):
    def __init__(self, psychopy_win, color):
        self.display_size = psychopy_win.size
        w,h = self.display_size
        self.win = psychopy_win
        self.color = color
        self.background = visual.Rect(self.win, w, h,
                                                   lineColor=self.color,
                                                   lineColorSpace='rgb255',
                                                   fillColor=self.color,
                                                   fillColorSpace='rgb255',
                                                   units='pix',
                                                   name='BACKGROUND',
                                                   opacity=1.0,
                                                   interpolate=False)
    def draw(self):
        self.background.draw()


# Intro Screen
class TextLine(object):
    def __init__(self,psychopy_win):
        self.display_size = psychopy_win.size
        self.win = psychopy_win
        
        color = (0,0,0)
        if np.sum(psychopy_win.color < 100) == 3:
            color = (255,255,255)

        self.textLine = visual.TextStim(self.win,
            text="***********************",
            pos=(0,0),
            height = 30,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='center',
            alignVert='center', wrapWidth=self.display_size[0]*.8)
    def draw(self, text=None):
        if text:
            self.textLine.text = text
        self.textLine.draw()


# Intro Screen
class IntroScreen(object):
    def __init__(self,psychopy_win):
        self.display_size = psychopy_win.size
        self.window = psychopy_win
        line_count = 25
        font_height = self.display_size[1]/50
        space_per_lines = int(font_height*2.5)
        total_line_height = space_per_lines*line_count
        topline_y = int(min(total_line_height/1.5, self.display_size[1]/2-self.display_size[1]/5.5))
        left_margin = -self.display_size[0]/2.1
        color = (0,0,0)
        
        # Make sure that the text can be read
        if np.sum(psychopy_win.color < 100) == 3:
            color = (255,255,255)
        
        # Draw psycholink image
        self.im = None
        try:
            imLoc = os.path.dirname(os.path.realpath(__file__))+'\\psychoLink.png'
            im = visual.ImageStim(self.window, imLoc)
            self.im = im
            scaleFactor = self.display_size[0]/1920.0
            self.im.setSize([scaleFactor*i for i in self.im.size])
            yUpper = topline_y-space_per_lines + (self.im.size[1]/2)
            xLeft = left_margin+(self.im.size[0]/2)
            self.im.pos = (xLeft, yUpper)            
        except:
            pass
        
        self.introlines = []

        self.introlines.append(visual.TextStim(self.window,
            text="PsychoLink",
            pos=(left_margin, topline_y-space_per_lines*2),
            height = int(font_height*1.66),
            color=color,
            colorSpace='rgb255',
            opacity=1.0,
            contrast=1.0,
            units='pix',
            ori=0.0,
            antialias=True,
            bold=True,
            italic=False,
            alignHoriz='left',
            alignVert='center',
            wrapWidth=self.display_size[0]*.8))

        self.introlines.append(visual.TextStim(self.window,
            text="ENTER: Show eye image",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)), 
            height = font_height,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='left',
            alignVert='center', wrapWidth=self.display_size[0]*.8))

        self.introlines.append(visual.TextStim(self.window,
            text="C: Start Calibration",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)),
            height = font_height,
            color=color,
            colorSpace='rgb255',
            opacity=1.0,
            contrast=1.0,
            units='pix',
            ori=0.0,
            antialias=True,
            bold=False,
            italic=False,
            alignHoriz='left',
            alignVert='center',
            wrapWidth=self.display_size[0]*.8))

        self.introlines.append(visual.TextStim(self.window,
            text="V: Start Validation",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)),
            height = font_height,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='left',
            alignVert='center', wrapWidth=self.display_size[0]*.8))

        self.introlines.append(visual.TextStim(self.window,
            text="ESCAPE: Return to Experiment",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)),
            height = font_height,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='left',
            alignVert='center', wrapWidth=self.display_size[0]*.8))

        self.introlines.append(visual.TextStim(self.window,
            text="Left / Right Arrow: Switch Camera Views",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)), height = font_height,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='left',
            alignVert='center', wrapWidth=self.display_size[0]*.8))

        self.introlines.append(visual.TextStim(self.window,
            text="A: Auto-Threshold",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)), height = font_height,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='left',
            alignVert='center', wrapWidth=self.display_size[0]*.8))

        self.introlines.append(visual.TextStim(self.window,
            text="Up / Down Arrow: Adjust Pupil Threshold",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)),
            height = font_height,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='left',
            alignVert='center', wrapWidth=self.display_size[0]*.8))

        self.introlines.append(visual.TextStim(self.window,
            text="+ or -: Adjust CR Threshold.",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)),
            height = font_height,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='left',
            alignVert='center', wrapWidth=self.display_size[0]*.8))
        self.introlines.append(visual.TextStim(self.window,
            text="I: Toggle extra information.",
            pos=(left_margin,topline_y-space_per_lines*(len(self.introlines)+2)),
            height = font_height,
            color=color, colorSpace='rgb255',
            opacity=1.0, contrast=1.0, units='pix',
            ori=0.0, antialias=True,
            bold=False, italic=False, alignHoriz='left',
            alignVert='center', wrapWidth=self.display_size[0]*.8))

    def draw(self):
        if self.im != None:
            self.im.draw()
        for s in self.introlines:
            s.draw()

class EyeLinkCoreGraphicsPsychopy(pl.EyeLinkCustomDisplay):
    WINDOW_BACKGROUND_COLOR = (128,128,128)
    CALIBRATION_POINT_OUTER_RADIUS = 15.0,15.0
    CALIBRATION_POINT_OUTER_EDGE_COUNT = 64
    CALIBRATION_POINT_OUTER_COLOR = (255,255,255)
    CALIBRATION_POINT_INNER_RADIUS = 3.0,3.0
    CALIBRATION_POINT_INNER_EDGE_COUNT = 32
    CALIBRATION_POINT_INNER_COLOR = (25,25,25)

    def __init__(self, window, tracker, targetForegroundColor=None,
                 targetBackgroundColor=None, screenColor=None,
                 targetOuterDiameter=None, targetInnerDiameter=None):
        pl.EyeLinkCustomDisplay.__init__(self)

        self.window = window
        window.winHandle.maximize()
        window.winHandle.activate()
        self.tracker = tracker
        self.imgstim_size = None
        self.rgb_index_array = None

        self.keys = []
        self.mouse_pos = []
        self.mouse_button_state = 0
        self.width, self.height= self.window.size
        self.size = self.window.size
        self.image_scale = 1
        self.image_size = None
        
        if sys.byteorder == 'little':
            self.byteorder = 1
        else:
            self.byteorder = 0

        EyeLinkCoreGraphicsPsychopy.CALIBRATION_POINT_OUTER_COLOR=targetForegroundColor
        EyeLinkCoreGraphicsPsychopy.CALIBRATION_POINT_INNER_COLOR=targetBackgroundColor
        EyeLinkCoreGraphicsPsychopy.WINDOW_BACKGROUND_COLOR=screenColor
        EyeLinkCoreGraphicsPsychopy.CALIBRATION_POINT_OUTER_RADIUS=targetOuterDiameter/2.0,targetOuterDiameter/2.0
        EyeLinkCoreGraphicsPsychopy.CALIBRATION_POINT_INNER_RADIUS=targetInnerDiameter/2.0,targetInnerDiameter/2.0

        self.tmp_file = os.path.join(tempfile.gettempdir(),'_eleye.png')

        self.blankdisplay = BlankScreen(self.window,self.WINDOW_BACKGROUND_COLOR)
        self.textmsg = TextLine(self.window)
        self.introscreen = IntroScreen(self.window)
        self.fixationpoint = FixationTarget(self)
        self.imagetitlestim = None
        self.eye_image = None
        self.state = None
        self.size = (0, 0)
        self.extra_info = True
        self.setup_cal_display()

    def setMousStart(self):
        mousStart = (-(self.win.size[0]/2),self.win.size[1]/2)
        if self.image_size:
            mousStart = ((self.image_size[0]/2)-(self.win.size[0]/2),  (self.win.size[1]/2)-(self.image_size[1]/2))
        else:
            mousStart = (100-self.win.size[0]/2, (self.win.size[1]/2)-100)
        self.tracker.mouse.setPos(mousStart)
    
    def get_input_key(self):
        if self.tracker.activeState != False:             
            allowedKeys = ['up','down','left','right', 'return', 'escape',
                           'space', 'c', 'v', 'a', 'i', 'num_add', 
                           'num_subtract']
            keycode = 0
            key = getKey(allowedKeys, False)[0]
            if key != 'NoKey':
                keycode = key 
                if keycode == 'up':	keycode = pl.CURS_UP
                elif keycode == 'down':  keycode = pl.CURS_DOWN
                elif keycode == 'left':  keycode = pl.CURS_LEFT; self.setMousStart()
                elif keycode == 'right': keycode = pl.CURS_RIGHT; self.setMousStart()
                elif keycode == 'return':  keycode = pl.ENTER_KEY; self.setMousStart()
                elif keycode == 'escape':  keycode = pl.ESC_KEY
                elif keycode == 'space':  keycode = ord(" ")
                elif keycode == 'c':  keycode = ord("c")
                elif keycode == 'v':  keycode = ord("v")
                elif keycode == 'a':  keycode = ord("a")       
                elif keycode == 'i':  keycode = self.extra_info = not self.extra_info 
                elif keycode == 'num_add':  keycode = ord("+")
                elif keycode == 'num_subtract':  keycode = ord("-")  
                else:  keycode = 0
        else:
            return None      
        return [pl.KeyInput(keycode, 0)]

    def setup_cal_display(self):
        """
        Sets up the initial calibration display, which contains a menu with
        instructions.
        """
        self.blankdisplay.draw()
        self.introscreen.draw()
        self.window.flip()

    def exit_cal_display(self):
        """Exits calibration display."""
        self.clear_cal_display()

    def clear_cal_display(self):
        """Clears the calibration display"""
        self.blankdisplay.draw()
        self.window.flip()

    def erase_cal_target(self):
        """Removes any visible calibration target graphic from display."""
        self.clear_cal_display()

    def draw_cal_target(self, x, y):
        """
        Draws calibration target.
        """
        # convert to psychopy pix coords
        x = x-self.window.size[0]/2
        y = -(y-self.window.size[1]/2)
        self.blankdisplay.draw()
        self.fixationpoint.draw((x,y))
        self.window.flip()

    def setup_image_display(self, width, height):
        """
        Initialize the index array that will contain camera image data.
        """

        self.size = (width,height)
        self.clear_cal_display()
        self.last_mouse_state = -1
        if self.rgb_index_array is None:
            self.rgb_index_array =  np.zeros((height, width), dtype = np.uint8)

    def exit_image_display(self):
        """Exits the image display."""
        self.clear_cal_display()
        self.setup_cal_display()

    def image_title(self, text):
        """
        Display the current camera, Pupil, and CR thresholds above
        the camera image when in Camera Setup Mode.
        """
        color = (0,0,0)
        if np.sum(self.window.color < 100) == 3:
            color = (255,255,255)
        if self.imagetitlestim is None:
           self.imagetitlestim = visual.TextStim(self.window,
                text=text,
                pos=(0,self.window.size[1]/2-15), height = 28,
                color=color, colorSpace='rgb255',
                opacity=1.0, contrast=1.0, units='pix',
                ori=0.0, antialias=True,
                bold=False, italic=False, alignHoriz='center',
                alignVert='top', wrapWidth=self.window.size[0]*.8)
        else:
            self.imagetitlestim.setText(text)
        #self.imagetitlestim.draw()

    def draw_image_line(self, width, line, totlines, buff):
        """
        Collects all lines for an eye image, saves the image,
        then creates a psychopy imagestim from it.
        """
        for i in range(width):
            try:
                self.rgb_index_array[line-1, i] = buff[i]
            except Exception, e:
                print e

        # Once all lines have been collected, go through the hoops needed
        # to display the frame as an image; scaled to fit the display resolution.
        if line == totlines:
            try:
                # Remove the black edges
                imW, imH = self.rgb_index_array.shape
                frameRSide = self.rgb_index_array[:, imW/2:]
                frameLhalf = self.rgb_index_array[imH/2:,:]
                if np.median(frameRSide) == 0 and np.median(frameLhalf) == 0:
                    im = self.rgb_index_array[:imW/2, :imH/2]
                    self.image_scale = 2
                else:
                    im = self.rgb_index_array
                image = scipy.misc.toimage(im, pal=self.rgb_pallete, mode='P')
                if self.imgstim_size is None:
                    maxsz = self.width/2
                    mx = 1.0
                    while (mx+1) * self.size[0] <= maxsz:
                        mx += 1.0
                    self.imgstim_size = int(self.size[0]*mx), int(self.size[1]*mx)
                image = image.resize(self.imgstim_size)
                self.image_size = image.size
                # Does not require saveing to temp file
                if self.eye_image is None:
                    self.eye_image = visual.ImageStim(self.window, image)
                else:
                    self.eye_image.setImage(image)
                    
                # Redraw the Camera Setup Mode graphics
                self.blankdisplay.draw()
                self.introscreen.draw()
                self.eye_image.draw()
                if self.extra_info:
                    self.draw_cross_hair()
                    if self.imagetitlestim:
                        self.imagetitlestim.draw()
                self.window.flip()

            except Exception, err:
                print err

    def set_image_palette(self, r, g, b):
        """
        Set color palette ued by host pc when sending images.
        Saves the different r,g,b values provided by the eyelink host palette.
        When building up each eye image frame, eyelink sends the palette
        index for each pixel; so an eyelink eye image frame can be a 2D lookup
        array into this palette.
        """
        self.clear_cal_display()
        sz = len(r)
        self.rgb_pallete = np.zeros((sz, 3), dtype=np.uint8)
        i = 0
        while i < sz:
            self.rgb_pallete[i:] = int(r[i]), int(g[i]), int(b[i])
            i += 1

    def alert_printf(self, msg):
        """
        Prints alert message to psychopy stderr.
        """
        print msg

    def play_beep(self, pylink_sound_index):
        """
        TODO: Plays a sound.
        """
        #if pylink_sound_index == pl.CAL_TARG_BEEP:
        #    pass
        if pylink_sound_index == pl.CAL_ERR_BEEP or pylink_sound_index == pl.DC_ERR_BEEP:
            self.textmsg.draw('Calibration Failed or Incomplete.\nPress "Enter" to return')
            self.window.flip()
        elif pylink_sound_index == pl.CAL_GOOD_BEEP:
            if self.state == "calibration":
                txt = 'Calibration Passed.'
                txt += '\nPress "Enter" to return'
            elif self.state == "validation":
                txt = 'Validation Passed.' 
                txt += '\nPress "Enter" to return'
            else: 
                txt = ' '
            self.textmsg.draw(txt)
            self.window.flip()


    def draw_line(self, x1, y1, x2, y2, color_index):
        """ Used to draw crosshair, color does not work """     
        if self.image_size: 
            # It asumes the image is in the top left       
            x1,y1 = topLeftToCenter((x1*self.image_scale,y1*self.image_scale), self.image_size)
            x2,y2 = topLeftToCenter((x2*self.image_scale,y2*self.image_scale), self.image_size)
    
            line   = visual.Line(self.window,\
                        start=(x1, y1),\
                        end=(x2, y2),\
                        lineWidth       = 1,\
                        lineColorSpace  = 'rgb255',\
                        lineColor       = [255,0,0],\
                        )
            line.draw()
        
    def draw_lozenge(self, x, y, width, height, color_index):
        """ Color does not work, Do not know what this does"""
        x1,y1 = topLeftToCenter((x,y), self.window.size)
        line   = visual.Line(self.window,\
                    start=(0, 0),\
                    end=(0, 0),\
                    lineWidth       = 1,\
                    lineColorSpace  = 'rgb255',\
                    lineColor       = [0,255,0],\
                    )
        # Draw line 1
        line.start = (x-(width/2), y)
        line.end = (x, y+(width/2))
        line.draw()
        # Draw line 2
        line.start = (x+(width/2), y)
        line.end = (x, y+(height/2))
        line.draw()
        # Draw line 3
        line.start = (x-(width/2), y)
        line.end = (x, y-(height/2))
        line.draw()
        # Draw line 4
        line.start = (x+(width/2), y)
        line.end = (x, y-(height/2))
        line.draw()

    def record_abort_hide(self):
        """ No idea what this is """
        pass

    def get_mouse_state(self):
        """  """
        state = self.tracker.mouse.getPressed()
        pos = centerToTopLeft(self.tracker.mouse.getPos(), self.window.size)
        return (pos, state[0])
        
