# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 16:00:17 2018

@author: Jonathan
"""
try:
    import pylink as pl
except:
    import warnings

    pl = False
    warnings.warn('Pylink not found, running dummy mode', Warning)
import time
import numpy as np
from psychopy import visual, core, event
import os
import sys

try:
    import pandas as pd
except:
    import warnings

    pd = False
    warn = 'Pandas not imported!\nmakeTrialList will return array and not dataframe!\nSaving calibration will not work!'
    warnings.warn(warn, Warning)
import Tkinter as tk
import tkFileDialog as filedialog
import scipy
from scipy import misc
import math
import matplotlib.pyplot as plt


# =============================================================================
# Required functions
# =============================================================================
def distBetweenPoints(p1, p2):
    """
    Calculates the distance between two points in a grid

    Parameters
    ----------
    p1 : tuple
        A tuple containing the (x,y) coordinates of the first point
    p2 : tuple
        A tuple containing the (x,y) coordinates of the second point

    Returns
    -------
    dist : float
        The Euclidian distance between the two points, the function assumes
        that the y-scaling and x-scaling are the same

    Examples
    --------
    >>> dist = distBetweenPoints((0,0), (10,10))
    >>> dist
    14.142135623730951
    """
    dist = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    return dist


def determineAngle(p1, p2):
    """
    Determines the angle in degrees between two points

    Parameters
    ----------
    p1 : tuple
        A tuple containing the (x,y) coordinates of the first point
    p2 : tuple
        A tuple containing the (x,y) coordinates of the second point

    Returns
    -------
    degree : float
        The angle between two points
        Returns values between -180 and 180.
        Positive values reflect the top half of a circle.
        Negative values reflect the bottom half of a circle.

    Examples
    --------
    >>> degree = determineAngle((0,0),(10,10))
    >>> degree
    45.0

    >>> degree = determineAngle((0,0),(-10,-10))
    >>> degree
    -135.0

    """
    normx = (p2[0] - p1[0])
    normy = (p2[1] - p1[1])
    narcdeg = math.atan2(normy, normx)
    degree = ((narcdeg * 180) / math.pi)
    return degree


def isNumber(s):
    """
    Tests whether an input is a number

    Parameters
    ----------
    s : string or a number
        Any string or number which needs to be type-checked as a number

    Returns
    -------
    isNum : Bool
        Returns True if 's' can be converted to a float
        Returns False if converting 's' results in an error

    Examples
    --------
    >>> isNum = isNumber('5')
    >>> isNum
    True

    >>> isNum = isNumber('s')
    >>> isNum
    False
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def circLinePos(cx=0, cy=0, r=10, setsize=50):
    """
    Returns a list of 4 arrays which contain the line start and endpoints
    from which a circle can be drawn

    Parameters
    ----------
    cx : int or float
        The center X coordinate of the circle
    cy : int or float
        The center Y coordinate of the circle
    r : int or float
        The radius of the circle
    setsize : int
        The number of lines to use for drawing the circle

    Returns
    -------
    x1,y1,x2,y2 : np.arrays with floats
        x1 = The start x position of each line\n
        y1 = The start y position of each line\n
        x2 = The end x position of each line\n
        y2 = the end y position of each line

    Examples
    --------
    >>> x1,y1,x2,y2 = circLinePos(0, 0, 10, 5)
    >>> x1,y1,x2,y2
    (array([ 10.        ,   3.09016994,  -8.09016994,  -8.09016994,   3.09016994]),
     array([ 0.        ,  9.51056516,  5.87785252, -5.87785252, -9.51056516]),
     array([  3.09016994,  10.        ,   3.09016994,  -8.09016994,  -8.09016994]),
     array([-9.51056516,  0.        ,  9.51056516,  5.87785252, -5.87785252]))

    """
    # Empty list to hold positions
    circPos = []
    # Segment definitions
    anglesegment = 2 * np.pi / setsize
    # creates a tupple with x,y coordinates for each position.
    for i in range(0, setsize):
        x = r * np.cos(i * anglesegment) + cx
        y = r * np.sin(i * anglesegment) + cy
        circPos.append((x, y))
    arr1 = np.array(circPos)
    arr2 = np.roll(arr1, 1, 0)
    return arr1[:, 0], arr1[:, 1], arr2[:, 0], arr2[:, 1]


def getKey(allowedKeys=['left', 'right'], waitForKey=True, timeOut=0):
    """
    Gets a keypress by using the event.waitKeys or event.getKeys from
    the psychopy module

    The escape key is always allowed.

    Parameters
    ----------
    allowedKeys : list, list fo strings
        The list should contain all allowed keys
    waitForKey : Bool
        If True, the code waits until one of the keys defined in allowedkeys
        or escape has been pressed
    timeOut : int or float, positive value
        Only has effect if waitForKey == True\n
        If set to 0, the function waits until an allowed key is pressed\n
        If set to any other positive value, breaks after timeOut seconds

    Returns
    -------
    key_pressed : tuple with two items
        The first index returns the Key\n
        The second index returns the timestamp\n
        The timestamp is in seconds after psychopy initialization and does not
        reflect the duration waited for the key press\n
        If timeOut or no key is pressed, returns ['NoKey', 9999]

    Note
    --------
    The function requires an active psychopy window

    Examples
    --------
    >>> key = getKey(allowedKeys = ['left', 'right'], waitForKey = True, timeOut = 0)
    >>> key # the 'left' key is pressed after 156 seconds'
    ('left', 156.5626505338878)
    """
    if waitForKey:
        while True:
            # Get key
            if timeOut > 0:
                key_pressed = event.waitKeys(maxWait=timeOut, timeStamped=True)
                if key_pressed is None:
                    key_pressed = [['NoKey', 9999]]
                    break
            else:
                key_pressed = event.waitKeys(maxWait=float('inf'), timeStamped=True)
            # Check last key
            if key_pressed[-1][0] == 'escape':
                break
            if key_pressed[-1][0] in allowedKeys:
                break

    else:
        # Get key
        key_pressed = event.getKeys(allowedKeys, timeStamped=True)
        if not key_pressed:
            key_pressed = [['NoKey', 9999]]

    return key_pressed[-1]


def drawText(win,
             text='No text specified!',
             textKey=['space'],
             wrapWidth=900,
             textSize=25,
             textColor=[0, 0, 0]):
    """
    Draw a string on a psychopy window and waits for a keypress, always tries
    to draw the text in the center of the screen.

    Parameters
    ----------
    win : psychopy window
        An instance of an active psychopy window on which to draw the text
    text : string
        The text to draw
    textKey : list
        A list of the allowed keys to press to exit the function. The function
        will block code execution until the specified key or escape is pressed
    wrapWidth : int
        The number of characters to display per line. If there are more
        characters on one line than specified in wrapWith the text will
        continue on the next line
    textSize : int
        The height of the text in pixels
    textColor : list of [R,G,B] values
        The color in which to draw the text, [R,G,B]

    Returns
    -------
    key : string
        The key pressed
    rt : float
        The time from text display onset until keypress in seconds

    Examples
    --------
    >>> key, rt = pl.drawText(win, 'Press "Space" to continue!')
    >>> key
    'space'
    >>> rt
    1.2606524216243997
    """

    if np.sum(np.array(textColor) == 0) == 3 and np.sum(win.color < 100) == 3:
        textColor = [255, 255, 255]

    textDisp = visual.TextStim(win, text=text, wrapWidth=wrapWidth,
                               height=textSize, colorSpace='rgb255',
                               color=textColor)
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
    """
    Checks whether the escape key has been pressed, does not block code

    Returns
    -------
    abort : Bool
        True if escape has been pressed
        False if escape has not been pressed

    Examples
    --------
    >>> abort = checkAbort
    >>> abort
    False
    """
    keys = event.getKeys(['escape'])
    if keys:
        if 'escape' in keys:
            return True
        else:
            return False
    else:
        return False


def angleToPixels(angle, screenDist, screenW, screenXY):
    """
    Calculate the number of pixels which equals a specified angle in visual
    degrees, given parameters. Calculates the pixels based on the width of
    the screen. If the pixels are not square, a separate conversion needs
    to be done with the height of the screen.\n
    "angleToPixelsWH" returns pixels for width and height.

    Parameters
    ----------
    angle : float or int
        The angle to convert in visual degrees
    screenDist : float or int
        Viewing distance in cm
    screenW : float or int
        The width of the screen in cm
    screenXY : tuple, ints
        The resolution of the screen (width - x, height - y), pixels

    Returns
    -------
    pix : float
        The number of pixels which corresponds to the visual degree in angle,
        horizontally

    Examples
    --------
    >>> pix = angleToPixels(1, 75, 47.5, (1920,1080))
    >>> pix
    52.912377341863817
    """
    pixSize = screenW / float(screenXY[0])
    angle = np.radians(angle / 2.0)
    cmOnScreen = np.tan(angle) * float(screenDist)
    pix = (cmOnScreen / pixSize) * 2

    return pix


def angleToPixelsWH(angle, screenDist, screenWH, screenXY):
    """
    Calculate the number of pixels which equals a specified angle in visual
    degrees, given parameters.

    Parameters
    ----------
    angle : float or int
        The angle to convert in visual degrees
    screenDist : float or int
        Viewing distance in cm
    screenWH : tuple, floats or ints
        The width and height of the screen in cm (width, height)
    screenXY : tuple, ints
        The resolution of the screen (width - x, height - y), pixels

    Returns
    -------
    pixW : float
        The number of pixels which corresponds to the visual degree in angle,
        horizontally (width)
    pixH : float
        The number of pixels which corresponds to the visual degree in angle,
        vertically (height)

    Examples
    --------
    >>> pixW, pixH = angleToPixelsWH(1, 75, (47.5, 30), (1920,1080))
    >>> pixW
    52.912377341863817
    >> pixH
    47.125086070097467

    """
    pixSizeW = screenWH[0] / float(screenXY[0])
    pixSizeH = screenWH[1] / float(screenXY[1])
    angle = np.radians(angle / 2.0)
    cmOnScreen = np.tan(angle) * float(screenDist)
    pixW = (cmOnScreen / pixSizeW) * 2
    pixH = (cmOnScreen / pixSizeH) * 2
    return pixW, pixH


def pixelsToAngle(pix, screenDist, screenW, screenXY):
    """
    Calculate the visual angle on the screen in degrees given a number of
    pixels. Calculates the distance based on the width of
    the screen. If the pixels are not square, a separate conversion needs
    to be done with the height of the screen.\n
    "pixelsToAngleWH" returns visual degrees for width and height.

    Parameters
    ----------
    pix : float or int
        The pixels to convert in number of pixels
    screenDist : float or int
        Viewing distance in cm
    screenW : float or int
        The width of the screen in cm
    screenXY : tuple, ints
        The resolution of the screen (width - x, height - y), pixels

    Returns
    -------
    angle : float
        The angle which spans the given number of pixels, horizontally

    Examples
    --------
    >>> deg = pixelsToAngle(55, 75, 47.5, (1920,1080))
    >>> deg
    1.0394522117965745

    """
    pixSize = screenW / float(screenXY[0])
    cmOnScreen = (pix / 2.0) * pixSize
    angle = np.rad2deg(np.arctan(cmOnScreen / screenDist)) * 2.0

    return angle


def pixelsToAngleWH(pix, screenDist, screenWH, screenXY):
    """
    Calculate the visual angle on the screen in degrees given a number of
    pixels.

    Parameters
    ----------
    pix : tuple, floats or ints
        The pixels to convert in nr of pixels. (horizontal, vertical)
    screenDist : float or int
        Viewing distance in cm
    screenWH : tuple, floats or ints
        The width and height of the screen in cm (width, height)
    screenXY : tuple, ints
        The resolution of the screen (width - x, height - y), pixels

    Returns
    -------
    degW : float
        The number of pixels which corresponds to the visual degree in angle,
        horizontally (width)
    degH : float
        The number of pixels which corresponds to the visual degree in angle,
        vertically (height)

    Examples
    --------
    >>> degW, degH = pixelsToAngleWH((55, 55), 75, (47.5, 30), (1920,1080))
    >>> degW
    1.0394522117965745
    >> degH
    1.1670958930600797

    """
    pixSizeW = screenWH[0] / float(screenXY[0])
    pixSizeH = screenWH[1] / float(screenXY[1])
    cmOnScreenW = (pix[0] / 2.0) * pixSizeW
    cmOnScreenH = (pix[1] / 2.0) * pixSizeH
    angleW = np.rad2deg(np.arctan(cmOnScreenW / screenDist)) * 2.0
    angleH = np.rad2deg(np.arctan(cmOnScreenH / screenDist)) * 2.0

    return angleW, angleH


def makeTrialList(header, conditions, reps=0, shuffle=True):
    """
    Create a counterbalanced trialList in a pandas dataframe.

    Parameters
    ----------
    header : list of strings
        Each string representing a column name. The names will be matched
        sequentially to the conditions in the conditions parameter. If there
        are more headers than conditions, the additional header columns will
        be filled with a bool - False
    conditions : list of list
        Each list should contain the different possibilities of that condition.
        They will be matched with the header parameter. The column with the
        first condition will get the string name in the first index of header
    reps : int
        The number of times the counterbalanced trialList is to be repeated.
        0 = no repeats, 1 = 1 repeat etc
    shuffle : Bool
        Indicate whether or not the counterbalanced trial list should be
        shuffled. If set to True and reps > 0, each counterbalanced list will
        be shuffled separately before being added to the output dataframe

    Returns
    -------
    trialList : pandas dataframe

    Examples
    --------
    >>> header = ['start', 'end']
    >>> conditions = [['left', 'right'],['up', 'down']]
    >>> trialList = makeTrialList(header, conditions)
    >>> trialList
       start   end
    0   left  down
    1   left    up
    2  right    up
    3  right  down

    >>> header = ['start', 'end', 'response', 'correct']
    >>> conditions = [['left', 'right'],['up', 'down']]
    >>> trialList = makeTrialList(header, conditions, 1, False)
    >>> trialList
       start   end response correct
    0   left    up    False   False
    1  right    up    False   False
    2   left  down    False   False
    3  right  down    False   False
    4   left    up    False   False
    5  right    up    False   False
    6   left  down    False   False
    7  right  down    False   False

    """
    conds = conditions[:]
    if not any(isinstance(el, list) for el in conds):
        print('A list of lists is required')

    # Add zeroPads
    zeroPads = len(header) - len(conds)
    for i in range(0, zeroPads):
        conds.append([False])
    # Get number of conditions (including zeroPads)
    nConds = len(conds)

    for i in range(0, nConds):
        temp = np.array(conds[i])
        # Turn vector vertical
        temp = temp.reshape(len(temp), 1)

        if i == 0:
            total = temp
        else:
            total = np.tile(total, (len(temp), 1))
            temp = np.repeat(temp, len(total) / len(temp))
            temp = temp.reshape(len(temp), 1)
            total = np.concatenate((total, temp), 1)

    if shuffle:
        trialList = np.random.permutation(total)
    else:
        trialList = total[:]

    # Add repeats
    for i in range(0, reps):
        if shuffle:
            total = np.random.permutation(total)
            trialList = np.concatenate((trialList, total))
        else:
            trialList = np.concatenate((trialList, total))

    # make it a pandas dataframe
    if pd:
        trialList = pd.DataFrame(trialList, columns=header)
    else:
        import warnings
        warn = '\nmakeTrialList\nPandas not found, returns np.array, not dataframe!'
        warnings.warn(warn, Warning)
    return trialList


def makeSquareGrid(x=0, y=0, grid_dimXY=[10, 10], line_lengthXY=[10, 10]):
    """
    Creates the coordinates for a square grid.

    Parameters
    ----------
    x : float or int
        The center x position of the grid
    y : float or int
        The center y position of the grid
    grid_dimXY : list, positive integers
        The size of the grid, e.g. the number of points in each direction
    line_lengthXY : list, positive floats or ints
        The length between each grid intersection, [width, height]

    Returns
    -------
    gridpositions : list of tuples
        Each tuple contains the (x,y) position of one of the grid intersections

    Examples
    --------
    >>> gridpositions = makeSquareGrid(0,0,[4,4],[10,10])
    >>> gridpositions
    [(-15.0, -15.0),
     (-15.0, -5.0),
     (-15.0, 5.0),
     (-15.0, 15.0),
     (-5.0, -15.0),
     (-5.0, -5.0),
     (-5.0, 5.0),
     (-5.0, 15.0),
     (5.0, -15.0),
     (5.0, -5.0),
     (5.0, 5.0),
     (5.0, 15.0),
     (15.0, -15.0),
     (15.0, -5.0),
     (15.0, 5.0),
     (15.0, 15.0)]

    """
    # Left starting position
    start_x = x - 0.5 * grid_dimXY[0] * line_lengthXY[0] + 0.5 * line_lengthXY[0]
    # Top starting position
    start_y = y - 0.5 * grid_dimXY[1] * line_lengthXY[1] + 0.5 * line_lengthXY[1]
    # For loops for making grid
    gridpositions = []
    for x_count in range(0, grid_dimXY[0]):
        current_x = start_x + x_count * line_lengthXY[0]
        for y_count in range(0, grid_dimXY[1]):
            current_y = start_y + y_count * line_lengthXY[1]
            gridpositions.append((current_x, current_y))
    return gridpositions


def makeCircleGrid(cx=0, cy=0, r=10, setsize=8, shuffle=True):
    """
    Returns a list of tuples with positions on an imaginary circle  around
    a point. All the points are equally spaced around the circle.

    Parameters
    ----------
    cx : float or int
        X coordinate of the imaginary circle
    cy : float or int
        Y coordinate of the imaginary circle
    r : float or int
        The radius of the imaginary circle
    setsize : int, positive
        The number of positions to be returned
    shuffle : Bool
        If True, the positions on the circle will be shuffled, the positions
        will be equally spaced on the grid, but everytime the function is
        called, it will return different points on the imaginary circle\n
        If False, similar to True, but the positions on the imaginary circle
        will always be the same

    Returns
    -------
    circPos : list of tuples
        Each tuple contains the (x,y) position of one of the circle positions

    Examples
    --------
    >>> circPos = makeCircleGrid(0,0, 10, 5, False)
    >>> circPos
    [(10.0, 0.0),
     (3.0901699437494745, 9.5105651629515346),
     (-8.0901699437494727, 5.8778525229247327),
     (-8.0901699437494745, -5.87785252292473),
     (3.0901699437494723, -9.5105651629515364)]

    >>> circPos = makeCircleGrid(0,0, 10, 5, True)
    >>> circPos
    [(-6.0636954133354148, -7.9518298481730012),
     (5.6888546621411695, -8.2241675951450972),
     (9.5796009515969587, 2.8690147451978461),
     (0.23166432460658745, 9.9973162219019844),
     (-9.4364245250092988, 3.3096664762182675)]

    """
    # Empty list to hold positions
    circPos = []
    # Segment definitions
    anglesegment = 2 * np.pi / setsize
    # Randomlly shift the orientation of the circle positions
    jitter = 0
    if shuffle: jitter = np.random.random_sample() * (2 * np.pi)
    # creates a tupple with x,y coordinates for each position.
    for i in range(0, setsize):
        x = r * np.cos(jitter + i * anglesegment) + cx
        y = r * np.sin(jitter + i * anglesegment) + cy
        circPos.append((x, y))
    return circPos


def topLeftToCenter(pointXY, screenXY, flipY=False):
    """
    Takes a coordinate given in topLeft reference frame and transforms it
    to center-based coordiantes. Switches from (0,0) as top left to
    (0,0) as center

    Parameters
    ----------
    pointXY : tuple
        The topLeft coordinate which is to be transformed
    screenXY : tuple, ints
        The (x,y) dimensions of the grid or screen
    flipY : Bool
        If True, flips the y coordinates

    Returns
    -------
    newPos : tuple
        The (x,y) position in center-based coordinates

    Examples
    --------
    >>> newPos = topLeftToCenter((100,100), (1920,1080), False)
    >>> newPos
    (-860.0, 440.0)

    """
    newX = pointXY[0] - (screenXY[0] / 2.0)
    newY = (screenXY[1] / 2.0) - pointXY[1]
    if flipY:
        newY *= -1
    return newX, newY


def centerToTopLeft(pointXY, screenXY, flipY=True):
    """
    Takes a coordinate given in a centered reference frame and transforms it
    to topLeft based coordiantes. Switches from (0,0) as center to
    (0,0) as topLeft

    Parameters
    ----------
    pointXY : tuple
        The center-based coordinate which is to be transformed
    screenXY : tuple, ints
        The (x,y) dimensions of the grid or screen
    flipY : Bool
        If True, flips the y coordinates

    Returns
    -------
    newPos : tuple
        The (x,y) position in topLeft based coordinates

    Examples
    --------
    >>> newPos = centerToTopLeft((100,100), (1920,1080), False)
    >>> newPos
    (1060, 640)

    """
    newX = pointXY[0] + (screenXY[0] / 2)
    if not flipY:
        newY = pointXY[1] + (screenXY[1] / 2)
    else:
        newY = (pointXY[1] * -1) + (screenXY[1] / 2)
    return newX, newY


def calibrationValidation(win, tracker, topLeft=False, nrPoints=9, dotColor=[0, 0, 0], pxPerDegree=47, saveFile=False):
    """
    Custom calibration validation using psychoLink. It uses the background
    color which is set in win. Flips the screen empty before returning.
    The median values returned for validation accuracy are determined by
    taking the median of the x and y samples from 300ms after validation dot
    onset until 2000ms after validation dot onset (median of 1700ms of
    samples). Samples are collected every 0.5ms the median is determined based
    on the median of the unique x and y positions

    Waits for a space press before starting and before exiting the
    feedback screen

    Parameters
    ----------
    win : psychopy window
        An instance of an active psychopy window on which to draw the text
    tracker :
        An active version of the psychoLink tracker class
    topLeft : Bool
        If True, assumes topLeft coordinate system\n
        If False, assumes center based coordinates
    nrPoints : int
        The number of calibration points to use, allowed input:\n
        9,13,15 or 25
    dotColor : list, [R,G,B]
        The RGB color of the validation dot
    pxPerDegree : float
        The number of pixels that equal 1 visual degree
    saveFile : Bool
        If True, saves the results to pandas dataframe in working directory\n
        If False, does not save results

    Returns
    -------
    validationResults : 3 X nrPoints, np.array
        1st row returns the validation point coordinates (x,y)\n
        2nd row returns (x,y) tuple with the median coordinates of xySamp()\n
        3rd row returns list with the pixel distance between the 1st row
        and 2nd row

    Examples
    --------
    >>> validationResults = calibrationValidation(win, tracker)
    >>> validationResults.loc[:,:2] # Only Showing the first three points
                      0                1                2
    0  (-765.0, -450.0)  (765.0, -450.0)  (-765.0, 450.0)
    1  (-760.5, -446.0)  (756.0, -450.0)  (-765.0, 449.0)
    2            6.0208                9                1
    """
    # Get required information from the supplied window
    xSize, ySize = win.size
    bgColor = win.color
    escapeKey = ['None']
    validationResults = []
    sampDur = 2000
    excludeTime = 300
    lineColor = [0, 255, 0]
    gazeColor = [255, 0, 0]
    textColor = [0, 0, 0]
    maxFeedPos = (300, -50)
    meanFeedPos = (-300, -50)

    if np.sum(np.array(textColor) == 0) == 3 and np.sum(win.color < 100) == 3:
        textColor = [255, 255, 255]
    if np.sum(np.array(dotColor) == 0) == 3 and np.sum(win.color < 100) == 3:
        dotColor = [255, 255, 255]

    # Initiate Dots (inner and outer dot for better fixation)
    OuterDot = visual.Circle(win,
                             radius=10,
                             lineWidth=1,
                             fillColorSpace='rgb255',
                             lineColorSpace='rgb255',
                             lineColor=bgColor,
                             fillColor=dotColor,
                             edges=40,
                             pos=[0, 0])

    InnerDot = visual.Circle(win,
                             radius=1,
                             lineWidth=1,
                             fillColorSpace='rgb255',
                             lineColorSpace='rgb255',
                             lineColor=bgColor,
                             fillColor=bgColor,
                             edges=40,
                             pos=[0, 0])

    # Initiate line
    errorLine = visual.Line(win,
                            start=(-0.5, -0.5),
                            end=(0.5, 0.5),
                            lineWidth=1,
                            lineColorSpace='rgb255',
                            lineColor=lineColor,
                            )

    # Initiate text
    text = visual.TextStim(win,
                           text='',
                           colorSpace='rgb255',
                           color=textColor)

    def drawDots(point):
        OuterDot.pos = point
        OuterDot.draw()
        InnerDot.pos = point
        InnerDot.draw()

    # Make the grid depending on the number of points for calibration
    if nrPoints == 9:
        xlineLength = (xSize - 150) / 2
        yLineLength = (ySize - 150) / 2
        gridPoints = makeSquareGrid(0, 0, [3, 3], [xlineLength, yLineLength])

    elif nrPoints == 13:
        xlineLength = (xSize - 150) / 2
        yLineLength = (ySize - 150) / 2
        gridPoints = makeSquareGrid(0, 0, [3, 3], [xlineLength, yLineLength])
        gridPoints += makeSquareGrid(0, 0, [2, 2], [xSize / 2, ySize / 2])

    elif nrPoints == 15:
        xlineLength = (xSize - 150) / 4
        yLineLength = (ySize - 150) / 2
        gridPoints = makeSquareGrid(0, 0, [5, 3], [xlineLength, yLineLength])

    elif nrPoints == 25:
        xlineLength = (xSize - 150) / 4
        yLineLength = (ySize - 150) / 4
        gridPoints = makeSquareGrid(0, 0, [5, 5], [xlineLength, yLineLength])

    else:
        text.text = 'Incorrect number of validation points,\n please try again with a different number'
        text.setText('Incorrect number of validation points,\n please try again with a different number')
        text.pos = (0, 0)
        text.draw()
        win.flip()
        time.sleep(3)
        return validationResults

    # start eyetracker
    tracker.startRecording()
    # Initiate an empty list to store the gaze positions and shuffle points
    gazePositions = []
    errorDistance = []
    np.random.shuffle(gridPoints)

    # remove the fixation posiiton from the gridpoints and add it as the last point
    gridPoints = [i for i in gridPoints if i != (0.0, 0.0)]
    gridPoints.append((0, 0))

    # Draw the first fixation dot and wait for spacepress to start validation
    drawDots((0, 0))
    win.flip()
    startKey = getKey(['space', 'escape'])
    if startKey[0] == 'escape':
        escapeKey[0] = 'escape'
        return validationResults

    # Draw the Dots dot and wait for 1 second between each dot
    for i in range(0, len(gridPoints)):
        drawDots(gridPoints[i])
        tracker.drawFixBoundary(gridPoints[i][0], gridPoints[i][1], pxPerDegree)
        win.flip()
        xSamples = []
        ySamples = []
        sampStart = time.time()
        # While loop to run for a second to determine gaze position
        while (time.time() - sampStart) * 1000 < sampDur:
            # Only get time points later than excludeTime
            if (time.time() - sampStart) * 1000 > excludeTime:
                x, y = tracker.getCurSamp()
                xSamples.append(x)
                ySamples.append(y)
                drawDots(gridPoints[i])
                win.flip()

        # Calculate the median gaze position and distance from point
        medianXPosition = np.median(xSamples)
        medianYPosition = np.median(ySamples)
        if topLeft:
            medianXY = topLeftToCenter((medianXPosition, medianYPosition), (xSize, ySize))
        else:
            medianXY = (medianXPosition, medianYPosition)
        gazePositions.append(medianXY)
        errorDistance.append(distBetweenPoints(medianXY, gridPoints[i]))

        # Check abort
        escapeKey = getKey(['escape'], waitForKey=False)
        if escapeKey[0] == 'escape':
            break

    # Make the return value empty if escape was pressed during validation else draw results
    if escapeKey[0] == 'escape':
        validationResults = []
    else:
        # Draw the results to the screen
        for i in range(0, len(gridPoints)):
            OuterDot.fillColor = dotColor
            drawDots(gridPoints[i])
            OuterDot.fillColor = gazeColor
            drawDots(gazePositions[i])
            errorLine.start = gridPoints[i]
            errorLine.end = gazePositions[i]
            errorLine.draw()
            # Draw the error values
            errorDeg = errorDistance[i] / float(pxPerDegree)
            text.text = str(np.round(errorDeg, 2)) + ' deg'
            text.setText(str(np.round(errorDeg, 2)) + ' deg')
            text.pos = (gridPoints[i][0], gridPoints[i][1] - 20)
            text.draw()

        # Draw Average and max values on screen
        maxError = np.round(np.max(errorDistance) / float(pxPerDegree), 2)
        meanError = np.round(np.average(errorDistance) / float(pxPerDegree), 2)
        text.text = 'mean error: ' + str(meanError) + ' deg'
        text.setText('mean error: ' + str(meanError) + ' deg')
        text.pos = meanFeedPos
        text.draw()
        text.text = 'max error: ' + str(maxError) + ' deg'
        text.setText('max error: ' + str(maxError) + ' deg')
        text.pos = maxFeedPos
        text.draw()

        # Show Calibration screen
        win.flip()
        runAgain = getKey(['space', 'escape', 'v'])
        if runAgain[0] == 'v':
            validationResults = calibrationValidation(win, tracker, nrPoints=nrPoints, dotColor=dotColor,
                                                      pxPerDegree=pxPerDegree)
        else:
            # Make the results
            validationResults = np.array([gridPoints, gazePositions, errorDistance])
            if pd:
                validationResults = pd.DataFrame(validationResults)
                # Save results
                if saveFile:
                    itt = 1
                    while itt < 100:
                        saveFileName = saveFile + 'Validation' + str(itt) + '.p'
                        fileFound = os.path.isfile(saveFileName)
                        if not fileFound:
                            validationResults.to_pickle(saveFileName)
                            break
                        itt += 1
            else:
                import warnings
                warn = '\nSave validation results\nPandas not found, Does not save results!'
                warnings.warn(warn, Warning)
    win.flip()
    tracker.stopRecording()
    return validationResults


# ==============================================================================
# Port code class
# ==============================================================================
class sendPortCode:
    """
    Class for sending port codes:
        Automatically goes to dummy mode if no parallel port

    Requires dlportio.dll !!!

    Never send codes directly after one another, they will be skipped!!
    Wait for the resetInterval + 2ms between codes

    Is automatically initiated when using the psychoLink eyetracking class.
    Initiates to: tracker.PPort

    """

    def __init__(self):
        self.setSettings()
        try:
            from ctypes import windll
            self.io = windll.dlportio
            self.dummy = False
            print '\nThe parallel port was initiated!'
            print 'Sending port codes!\n'
        except:
            print '\nThe parallel port couldn\'t be opened'
            print 'Set to dummy mode!\n'
            self.dummy = True
            self.io = False

    def setSettings(self, resetValue=0, resetInterval=0.001, port=0x378):
        """
        Sets the settings for sendPort code class

        Parameters
        ----------
        resetValue : int: 0-255
            The value to which the parallel port will be reset when using
            "sendCodeAndReset"
        resetInterval : float, positive
            The time to block code execution after setting the parallel port
            before resetting the parallel port, when using "sendCodeAndReset".
            Time interval is in seconds
        port : hexadecimal
            The parallel port address

        Examples
        --------
        Initiate the class and set the resetvalue to 10 and wait time to
        10ms
        >>> PPort = sendPortCode()
        >>> PPort.setSettings(10, 0.01, 0x378)
        """
        self.resetValue = resetValue
        self.resetInterval = resetInterval
        self.port = port

    def sendCodeAndReset(self, code, resetInterval=0):
        """
        Set the parallel port code. Then waits for a set time and then
        finaly resets the parallelport.

        Prints to console if it is unable to connect with the parallel port

        Parameters
        ----------
        code : int, 0-255
            The value to set the parallel port
        resetInterval : float or int, positive
            If set to 0, then the resetinterval set in "setSettings" is used.
            If not 0, waits for the given float or int in seconds

        Examples
        --------
        Initiates and sends code (output is dummy mode)\n
        Resets the portcode after approx 10ms
        >>> PPort = sendPortCode()
        >>> PPort.sendCodeAndReset(200, 0.01)
        portCode: 200
        portreset: 0
        PortOpen for 9.99999046326ms
        """
        if resetInterval == 0:
            waitTime = self.resetInterval
        else:
            waitTime = resetInterval
        if code != self.resetValue:
            # Send port to console
            if self.dummy:
                print 'portCode: ' + str(code)
                portSend = time.time()
                core.wait(waitTime, hogCPUperiod=waitTime)
                portReset = time.time()
                print 'portreset: ' + str(self.resetValue)
                print 'PortOpen for ' + str((portReset - portSend) * 1000) + 'ms'

            # Actually send port codes
            elif not self.dummy:
                # Send port code
                try:
                    self.io.DlPortWritePortUchar(self.port, int(code))
                except:
                    print 'Failed to send trigger!'
                # wait for a set time
                core.wait(waitTime, hogCPUperiod=waitTime)
                # Reset the port
                try:
                    self.io.DlPortWritePortUchar(self.port, int(self.resetValue))
                except:
                    print 'Failed to reset trigger!'

    def sendCode(self, code):
        """
        Set the parallel port code.
        Prints to console if it is unable to connect with the parallel port

        Parameters
        ----------
        code : int, 0-255
            The value to set the parallel port

        Examples
        --------
        Initiates and sends code (output is dummy mode)
        >>> PPort = sendPortCode()
        >>> PPort.sendCode(200)
        portCode: 200
        """
        # Send port to console
        if self.dummy:
            print 'portCode: ' + str(int(code))

        # Actually send port codes
        elif not self.dummy:
            # Send port code
            try:
                self.io.DlPortWritePortUchar(self.port, int(code))
            except:
                print 'Failed to send trigger!'


# ==============================================================================
# PsychoLink
# ==============================================================================
class eyeLink:
    """
    Initiates the eyetracker. If no eyetracker is found or pylink is not
    installed, it enters dummy mode. Is called when the eyeLink class
    is initiated. It always prints whether or not the eyetracker was
    initiated or if dummy mode was initiated.

    See : https://github.com/jonathanvanleeuwen/psychoLink/wiki
    for more documentation and examples.

    All function documentation assumes that the class is initiated as 'tracker'.
    See the example below for how to correctly initiate the class.

    The class for sending parallel port codes is automatically initiated as
    tracker.PPort

    All eyelink API code can be accessed using tracker.pylink

    To initiate the eyetracker the window units has to be
    set to pix

    Parameters
    ----------
    win : psychopy window
        An instance of an active psychopy window on which to draw the text
    fileName : string
        The name of the eyedata file. Remeber that it should always end
        with .EDF
    fileDest : string
        The directory to save the eyedata file. Defaults to False. If False
        the data will be saved in the working directory
    screenWidth : float or int
        The with of the screen, in cm. Only works if the psychopy window
        was initiated without a psychopy monitor object, else uses the psychopy
        monitor values.
    screenDist : float or int
        The distance between the participant and the screen, in cm. Only
        works if the psychopy window was initiated without a psychopy
        monitor object, else uses the psychopy monitor values.
    address : string
        The network address that is connected to the eyelink. By default
        this should be "100.1.1.1"
    dummyMode : Bool
        If set to True, forces psychoLink into dummy mode

    Returns
    -------
    tracker : psychoLink eyetracker class
        The class used to talk to the eyelink eyetracker\n
        See: https://github.com/jonathanvanleeuwen/psychoLink/wiki for
        all included functions. See documentation for each function in this
        code.

    Examples
    --------
    The examples assume that the psychoLink module is imported from a
    different script. To initiate the eyetracker the window units has to be
    set to pix

    >>> import psychoLink as pl
    >>> from psychopy import visual, monitors
    >>> mon = monitors.Monitor('testMonitor',width=47,distance=75)
    >>> win = visual.Window(units='pix',monitor=mon,size=(1680,1050),
    colorSpace='rgb255',color = (255,255,255), screen = 0, fullscr=False)
    >>> tracker = pl.eyeLink(win, fileName='someName.EDF', fileDest = "C:\Users\User1\Desktop\\")

    The absolute minimum of inputs required to initiate the eyetracker. Keep in
    mind that to get correct distances etc, the values for distance and width
    should be set for each eyetracker setup, but it is not required. It is not
    a good idea to only use the default settings

    >>> import psychoLink as pl
    >>> from psychopy import visual
    >>> win = visual.Window(units='pix')
    >>> tracker = pl.eyeLink(win)
    """

    # =========================================================================
    # Initiate Eyetracker or use mouse if no eyetracker found
    # =========================================================================
    def __init__(self, win, fileName='XX.EDF', fileDest=False,
                 screenWidth=47.5, screenDist=75, address="100.1.1.1",
                 dummyMode=False):
        """
        see pl.tracker documentation
        """
        self.win = win
        address = str(address)
        self.EDFfileName = str(fileName)
        self.EDFDefaultName = 'XX.EDF'
        self.mouse = event.Mouse(win=win)
        self.activeState = True
        self.ABORTED = False
        self.fileDest = fileDest
        self.PPort = sendPortCode()

        try:
            if not dummyMode:
                # Real connection to tracker
                self.pylink = pl.EyeLink(address)
                self.pylink.openDataFile(self.EDFDefaultName)
                pl.flushGetkeyQueue()
                self.mode = 'Real'
                self.mouse.setVisible(0)
                print '\nTracker found!'
                print 'Mouse set to invissible'
                drawText(self.win, 'Press "SPACE" to setup EyeTracker!')
                self.win.flip()
            else:
                2/0
        except:
            # or for dummy mode connection
            self.mode = 'Dummy'
            if pl:
                try:
                    self.pylink = pl.EyeLink(None)
                    error = '\n\tNo eye-tracker found at: "' + address + \
                            '\n\tEntering DummyMode\n' + \
                            '\tUsing Mouse Position\n\n\tPress "Space" to start'
                except:
                    self.pylink = False
                    error = '\n\tPylink module not found!' + \
                            '\n\tCheck for correct pylink installation' + \
                            '\n\tEntering DummyMode\n' + \
                            '\tUsing Mouse Position\n\n\tPress "Space" to start'
            else:
                self.pylink = False
                error = '\n\tPylink module not found!' + \
                        '\n\tCheck for correct pylink installation' + \
                        '\n\tEntering DummyMode\n' + \
                        '\tUsing Mouse Position\n\n\tPress "Space" to start'
            print("\nError: %s" % error)
            self.mouse.setVisible(1)
            drawText(self.win, error)
            self.win.flip()

        self.setEyeLinkSettings(screenW=win.size[0], screenH=win.size[1])
        self.setCalibrationOptions(backCol=win.color)
        try:
            screenD = win.scrDistCM
            screenW = win.scrWidthCM
            self.pxPerDeg = angleToPixels(1, screenD, screenW, win.size)
        except:
            self.pxPerDeg = angleToPixels(1, screenDist, screenWidth, win.size)

    # =========================================================================
    # Set settings for eyetracker
    # =========================================================================
    # Set recording parameters
    def setEyeLinkSettings(self, vel=35, acc=9500, screenW=1680, screenH=1050):
        """
        Manually set eyelink saccade detection parameters.

        Parameters
        ----------
        vel : int
            The velocity threshold for saccade detection, degrees per second
        acc : int
            The acceleration threshold for saccade detection
        screenW : int
            The with of the screen in pixels (automatically sets when
            initiating the eyetracker)
        screenH : int
            The height of the screen in pixels (automatically sets when
            initiating the eyetracker)
        """
        self.screenW = screenW
        self.screenH = screenH
        if self.mode == 'Real':
            # Send screen info to eyelink
            self.pylink.sendCommand("screen_pixel_coords = 0 0 %d %d" % (screenW, screenH))
            self.pylink.sendMessage("DISPLAY_COORDS 0 0 %d %d" % (screenW, screenH))

            # Set saccade velocity settings
            if self.pylink.getTrackerVersion() == 2:
                self.pylink.sendCommand("select_parser_configuration 0")
            else:
                self.pylink.sendCommand("saccade_velocity_threshold = " + str(vel))
                self.pylink.sendCommand("saccade_acceleration_threshold = " + str(acc))

            # Send events to filter to eyelink
            # Also try to record some data with HREF in the sample and link filter
            # And then try to look at the ascii file for parsing the data

            self.pylink.setFileEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
            self.pylink.setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
            self.pylink.setLinkEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
            self.pylink.setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")
            self.pylink.sendCommand("button_function 5 'accept_target_fixation'")

    # =========================================================================
    # Running drift correct and calibration procedure (make psychopy screen)
    # =========================================================================
    def setCalibrationOptions(self, foreCol=[0, 0, 0], backCol=[150, 150, 150], calDiam=10, holeDiam=2, colorDepth=32, targSound="on", corrSound="on", incSound="on", caltype='HV9', calTime=1000):
        """
        Set the calibration options for the eyetracker calibration.
        Is automatically set when initiating the eyetracker. When auto
        initiating it uses the background color of the psychopy window object.


        Parameters
        ----------
            foreCol : list, [R,G,B]
                The RGB values of the calibration dot
            backCol : list, [R,G,B]
                The RGB values of the background color
            calDiam : int
                The diameter of the calibration dot in pixels
            holeDiam : list, [R,G,B]
                The diameter of the hole in the calibration dot in pixels. This
                facilitates fixation.
            colorDepth : int
                The colorDepth of the screen, defaults to 32bit
            targSound : string
                Whether or not to play a sound when looking at calibration
                dots. options: 'on' or 'off'. Does not currently work.
            corrSound : string
                Whether or not to play a sound when calibration is succesfull.
                options: 'on' or 'off'. Does not currently work.
            incSound : string
                Whether or not to play a sound when calibration is unsuccesfull.
                options: 'on' or 'off'. Does not currently work.
            caltype : string
                The type of calibration to run, e.g. numbe rof dots. The
                options are: "H3", "HV3", "HV5", "HV9".
            calTime : int
                The automatic calibration pacing in milliseconds
        """
        # Set the options
        if np.sum(np.array(backCol) < 100) == 3 and np.sum(np.array(foreCol) == 0) == 3:
            foreCol = (255, 255, 255)
        self.foreCol = [int(i) for i in foreCol]
        self.backCol = [int(i) for i in backCol]
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
        """
        Starts eyetracker calibration screen.\n
        Press escape to exit calibration

        Examples
        --------
        >>> tracker.calibrate()
        """
        if self.mode == 'Real':
            genv = EyeLinkCoreGraphicsPsychopy(self.win, self,
                                               targetForegroundColor=self.foreCol,
                                               targetBackgroundColor=self.backCol,
                                               screenColor=self.backCol,
                                               targetOuterDiameter=self.calDiam,
                                               targetInnerDiameter=self.holeDiam)
            pl.openGraphicsEx(genv)
            # Set number of calibration points
            self.pylink.sendCommand("calibration_type=%s" % self.caltype)
            # Set calibration point duration
            self.pylink.sendCommand("automatic_calibration_pacing=%d" % self.calTime)
            # Set sounds
            pl.setCalibrationSounds(self.targSound, self.corrSound, self.incSound)
            self.pylink.doTrackerSetup()
            genv.clear_cal_display()
            self.win.flip()
            drawText(self.win, 'Press "Space" to start!')
            self.pylink.startRecording(1, 1, 1, 1)

    # Run drift correct
    def driftCorrect(self, fixDot):
        """
        Performs drift correct.\n
        Requires the spacebar to be pressed when fixating the fixation dot.
        Does not yet support gaze or saccade trigger driftCorrect.

        Parameters
        ----------
        fixDot : psychopy visual shapestim
            The stimulus to use for drift correct

        Examples
        --------
        >>> fixDot = visual.Circle(win,radius=10,edges=50)
        >>> tracker.driftCorrect(fixDot)
        """
        if self.mode == 'Real':
            xx, yy = fixDot.pos
            x, y = centerToTopLeft((xx, yy), (self.screenW, self.screenH))
            # Set sounds (does not work)
            pl.setDriftCorrectSounds(self.targSound, self.corrSound, self.incSound)
            fixDot.draw()
            self.win.flip()
            time.sleep(0.5)
            self.pylink.doDriftCorrect(int(x), int(y), 0, 1)

    # =========================================================================
    # Methods for talking to the eytracker
    # =========================================================================
    def startTrial(self, trialNr=False):
        """
        Starts the eyetracker recording mode and also sends a message to the
        eyelink log that the trial is starting. The message sent is
        'start_trial'. Use this function before the trial starts.
        If dummy mode, prints the message to the console.

        tracker.startTrial() and tracker.stopTrial() should be used at the
        absolute beginning of a trial and at the absolute end of the trial,
        respectively. All data logging and gaze contingent code should be
        done between tracker.startTrial() and tracker.stopTrial()

        Examples
        --------
        >>> tracker.startTrial(10)
        """
        self.startRecording()
        time.sleep(10 / 1000.0)
        self.sendMsg('start_trial')
        if self.mode == 'Real':
            if trialNr:
                self.pylink.sendCommand("record_status_message=trialNr_%d" % (int(trialNr)))
            else:
                self.pylink.sendCommand("record_status_message=trialNr_XX")

    def stopTrial(self):
        """
        Stops the eyetracker recording mode and also sends a message to the
        eyelink log that the trial is stoped. The message sent is
        'stop_trial'. Use this function before the trial starts.
        If dummy mode, prints the message to the console.

        Examples
        --------
        >>> tracker.stopTrial()
        """
        self.sendMsg('stop_trial')
        time.sleep(10 / 1000.0)
        self.stopRecording()

    # start recording
    def startRecording(self):
        """
        This sets the eyetracker to recording mode. Does not send any
        messages. If starting a trial, use tracker.startTrial() instead.

        Examples
        --------
        >>> tracker.startRecording()
        """
        if self.mode == 'Real':
            self.pylink.clearScreen(0)
            time.sleep(0.1)
            # Start Recording
            self.pylink.startRecording(1, 1, 1, 1)
            time.sleep(0.1)
            # begin the realtime mode
            # pl.pylink.beginRealTimeMode(200)

    # Stop recording
    def stopRecording(self):
        """
        This stops the eyetracker recording mode. Does not send any
        messages. If stopping a trial, use tracker.stopTrial() instead.

        Examples
        --------
        >>> tracker.stopRecording()
        """
        if self.mode == 'Real':
            # pl.pylink.endRealTimeMode()
            self.pylink.sendCommand("record_status_message=NoTitle")
            self.pylink.clearScreen(0)
            self.pylink.stopRecording()

    # Send message to pyLinkLog
    def sendMsg(self, msg=''):
        """
        Send a message to the eyetracker data file. If logging variables
        use tracker.logVar() instead. This function is better to use if
        there are timing crucial messages to be sent to the eyetracker log
        file. Be sure to wait at least 2ms between each call to this function.
        The eyelink system needs a minimum of 2ms between each message to
        to keep stable performance. If dummy mode, prints the message to
        the console.
        The eyetracker needs to be in recording mode for this to work.

        Parameters
        ----------
        msg : string
            The string message to send to the eyetracker log file

        Examples
        --------
        Sending a message

        >>> tracker.sendMsg('targetOnset')

        Sending a message at the same time as flipping a window, this should
        give you better timing.

        >>> win.callOnFlip(tracker.sendMsg, 'targetOnset')
        >>> win.flip()

        """
        if self.mode == 'Real':
            self.pylink.sendMessage(str(msg))
        elif self.mode == 'Dummy':
            msg = 'PsychoLink Log (Dummy): ' + str(msg)
            print msg

    # Log variable to pyLinkLog
    def logVar(self, varName='noName', value='noValue'):
        """
        Log a variable to the eyelink log. Automatically waits atleast 2ms
        after each call to give teh eyelink system time to catch up.
        It is important that there are no spaces in "varName" and no
        space in "value"

        Sends  "'var '+varName+' '+value" to the eyeTracker log\n

        If dummy mode, prints the message to the console.
        The eyetracker needs to be in recording mode for this to work.

        Parameters
        ----------
        varName : str, int or float
            The name of the variable you are logging in the eyelink data
            file. The value passed will be turned into a string before sending
            the message
        value : str, int or float
            The value corresponding to the "varName". The value will be turned
            into a string before the message is sent.

        Examples
        --------
        >>> tracker.logVar('response', 'left')
        >>> tracker.logVar('rt', 100.0)

        """
        msg = 'var ' + str(varName) + ' ' + str(value)
        if self.mode == 'Real':
            self.pylink.sendMessage(msg)
            time.sleep(2 / 1000.0)
        elif self.mode == 'Dummy':
            msg = 'PsychoLink Log (Dummy): ' + msg
            print msg
            time.sleep(2 / 1000.0)

    def getTime(self):
        """
        Gets the eyelink timestamp of the newest gaze sample.
        The eyetracker needs to be in recording mode for this to work.

        Returns
        -------
        timeStamp : float or int
            The timestamp of the newest sample. In eyelink timeframe

        Examples
        --------
        >>> timestamp = tracker.getTime()
        >>> timeStamp
        1820231
        """
        timeStamp = False
        if self.mode == 'Real':
            curSamp = self.pylink.getNewestSample()
            timeStamp = curSamp.getTime()
        return timeStamp

    def drawFixBoundary(self, x, y, rad, bType='circle', color=[2, 4]):
        """
        Draws a cross and a boundary on the eyelink host PC screen. The boundary
        is useful for the experimenter to determine if the participant is
        looking at the target, or whether the calibration is still good.

        The eyetracker needs to be in recording mode for this to work.

        Parameters
        ----------
        x : int or float
            The x center of the cross, center-based coordinates
        y : int or float
            The y center of the cross, center-based coordinates
        rad : int or float
            If bType == 'circle', it is the radius of the circle boundary\n
            If bType == 'square', it is the width and height of the square
            boundary. The radius is in pixels
        bType : string
            The type of shape used to draw the boundary. Options: 'circle'
            or 'square'.
        color : list, 2 ints
            The first value is the color of the fixation cross, the second
            color is the color of the boundary. Color values can be 0-15,
            inclusive.

        Examples
        --------
        Draw a fixdot and boundary in the center of the host Pc screen.

        >>> tracker.drawFixBoundary(0, 0, 100)

        """
        if self.mode == 'Real':
            x, y = centerToTopLeft((x, y), (self.screenW, self.screenH))
            if bType == 'square':
                rad *= 2
                xL, yL = (x - rad / 2, y - rad / 2)
                self.pylink.drawBox(xL, yL, rad, rad, color[0])
            elif bType == 'circle':
                x1, y1, x2, y2 = circLinePos(x, y, rad)
                for idx, (x1, y1, x2, y2) in enumerate(zip(x1, y1, x2, y2)):
                    self.pylink.drawLine((x1, y1), (x2, y2), color[0])

            # Draw Cross
            self.pylink.drawLine((x - 15, y), (x + 15, y), color[1])
            self.pylink.drawLine((x, y + 15), (x, y - 15), color[1])
            # self.pylink.drawCross(x,y, color[1])

    def drawEyeText(self, text, pos=False):
        """
        Draw text to the eylink host PC screen.

        If dummy mode, prints the message to the console.
        The eyetracker needs to be in recording mode for this to work.

        Parameters
        ----------
        text : string
            The string of text to display on the host pc

        pos : tuple
            The (x,y) position to draw the text, in center-based coordinates\n
            If no pos given, then draws along the bottom of the screen

        Examples
        --------
        >>> tracker.drawText('Instructions')
        """
        if self.mode == 'Real':
            if not pos:
                x, y = centerToTopLeft((self.screenW / 2, self.screenH - 30), (self.screenW, self.screenH))
                self.pylink.sendCommand("draw_text=%d %d %d %s " % (x, y, 3, text))
            else:
                x, y = centerToTopLeft(pos, (self.screenW, self.screenH))
                self.pylink.sendCommand("draw_text=%d %d %d %s " % (x, y, 3, text))
        else:
            print text

    def drawTrialInfo(self, block='NA', tNr=999, tCor=999, tInc=999, tLeft=999):
        """
        Draws trial information to the eyelink host PC screen. It
        automatically draws the text on the bottom of the screen. This is
        very usefull for the experimenter to track the performance and
        progress of the experiment.

        If dummy mode, prints the message to the console.
        The eyetracker needs to be in recording mode for this to work.

        Parameters
        ----------
        block : string
            The experiment block, e.g. "Pract" or "Exp"
        tNr : int
            The current trial number
        tCor : int
            The number of correct trials
        tInc : int
            The number of incorrect trials
        tLeft : int
            The number of remaining trials

        Examples
        --------
        >>> tracker.drawTrialInfo('Exp', 100, 95, 5, 900)
        """
        block = str(block)
        text = 'Block = %s | tNr = %s | tCor = %s | tInc = %s | tLeft = %s' \
               % (block, tNr, tCor, tInc, tLeft)
        if self.mode == 'Real':
            x = self.screenW / 2
            y = self.screenH - 30
            self.pylink.sendCommand("draw_text=%d %d %d %s " % (x, y, 3, text))
        else:
            print text

    def drawHostImage(self, im):
        """
        Draws an image to the eyelink host computer. It assumes that the
        image is displayed fullsceen.
        Rescales the image to half size and turns it into 4 color grayscale.

        The code will/should be updated to be more flexible in image inputs.
        E.g. change in size and position

        Note that the code is quite slow, it also clears the screen before
        drawing.

        Parameters
        ----------
        im : str
            The path to the image we want to display

        Examples
        --------
        >>> im = 'picture1.jpg'
        >>> tracker.drawHostImage(im)
        """
        if self.mode == 'Real':
            def im2GrayReshape(im, screenShape, newShape, nColors=4):
                im = plt.imread(im)
                grayIm = np.dot(np.array(im)[..., :3], [0.299, 0.587, 0.114])
                grayIm = scipy.misc.imresize(grayIm, screenShape)
                rscIm = scipy.misc.imresize(grayIm, newShape)
                if nColors > 2:
                    dscIm = np.array(rscIm.copy(), dtype=np.float64)
                    dscIm = np.array((dscIm / np.max(dscIm)) * (nColors - 1), dtype=np.uint8)
                else:
                    dscIm = rscIm.copy()
                    av = np.mean(dscIm)
                    dscIm[dscIm <= av] = 1
                    dscIm[dscIm > av] = 0
                return dscIm

            def getEyelinkIm(im, screenShape, newShape):
                # Code 0 = Black
                # Code 8 = Dark Gray
                # Code 7 = Light Gray
                # Code 15 = Bright White
                newIm = im2GrayReshape(im, screenShape, newShape)
                newIm[newIm == 1] = 8
                newIm[newIm == 2] = 7
                newIm[newIm == 3] = 15
                return newIm

            screenShape = (int(self.screenH), int(self.screenW))
            newShape = (int(self.screenH / 2), int(self.screenW / 2))
            xCoords = np.arange(0, self.screenW - 2, 2)
            yCoords = np.arange(0, self.screenH - 2, 2)
            eyeIm = getEyelinkIm(im, screenShape, newShape)
            self.pylink.clearScreen(0)
            # draw each pixel sepperatly
            for xIdx, x in enumerate(xCoords):
                sCol = 100
                sY = 0
                drawY = 2
                drawLong = False
                for yIdx, y in enumerate(yCoords):
                    if eyeIm[yIdx, xIdx] == sCol:
                        drawY += 2
                        drawLong = True
                    else:
                        if drawLong:
                            if sCol != 0:
                                self.pylink.drawLine((x, sY), (x, sY + drawY), sCol)
                                # self.pylink.drawLine((x+1, sY),(x+1, sY+drawY),sCol)
                            drawLong = False
                        else:
                            sY = y
                            if eyeIm[yIdx, xIdx] != 0:
                                self.pylink.drawLine((x, sY), (x, sY + drawY), eyeIm[yIdx, xIdx])
                                # self.pylink.drawLine((x+1, sY),(x+1, sY+drawY),eyeIm[yIdx,xIdx])
                        drawY = 2
                        sCol = eyeIm[yIdx, xIdx]
                        sY = y

                        # Get the newest data sample

    def getCurSamp(self):
        """
        Gets the most recent gaze position sample from the eyelink. This
        sample might be a couple of ms delayed, depending on the eyelink
        settings used.

        If in dummy mode returns the mouse position instead.
        The eyetracker needs to be in recording mode for this to work.

        Returns
        -------
        curSamp : tuple
            The (x,y) gaze position on the screen. In center-based coordinates.

        Examples
        --------
        >>> curSamp = tracker.getCurSamp()
        >>> curSamp
        (100,250)

        Note
        --------
        If running in dummy mode the cursor positon only updates
        if there is a psychopy event, e.g. every win.flip()
        If running a while loop without a win.flip(), it will return
        the same mouse position everytime.\n
        This is not the case if the eytracker is connected, then the samples
        will be updated every ms (if eyelink at 1000hz).
        """
        if self.mode == 'Real':
            curSamp = self.pylink.getNewestSample()
            if curSamp is not None:
                if curSamp.isRightSample():
                    gazePos = curSamp.getRightEye().getGaze()
                if curSamp.isLeftSample():
                    gazePos = curSamp.getLeftEye().getGaze()

                newGazePos = [0, 0]
                newGazePos[0] = gazePos[0] - self.screenW / 2
                newGazePos[1] = -(gazePos[1] - self.screenH / 2)
                curSamp = newGazePos
        elif self.mode == 'Dummy':
            curSamp = tuple(self.mouse.getPos())
        return curSamp

    # Get next event
    def getEsacc(self, timeout=4):
        """
        Waits for the end of the next saccade (is bussy while waiting) and
        then returns the esacc information.

        If running in dummy mode the function returns a list with False and
        does not block code execution. In other words, don't use this
        function if you are running in dummy mode, as it always returns a
        list with false values
        The eyetracker needs to be in recording mode for this to work.
        By pressing escape you can manually exit the function. This is
        useful if timeout is set to a very long interval.

        Parameters
        ----------
        timeout : int or float
            The duration to block code execution and look for the end of a
            saccade, in seconds. If no end saccade detected during the interval
            the function will return a list with False.

        Returns
        -------
        esacc : list
            index0: start saccade timestamp\n
            index1: end saccade timestamp\n
            index2: start saccade X\n
            index3: start saccade Y\n
            index4: end saccade X\n
            index5: end saccade Y

        Examples
        --------
        >>> esacc = tracker.getEsacc()
        >>> esacc
        [1820247, 1820291, 437.2, 465.0, 810.8, 454.4]

        Note
        --------
        This blocks code execution for the duration of timeout. Don't use this
        function if you are simultaneously updating the window or running any
        other code in the background.
        """
        esacc = [False, False, False, False, False, False]
        if self.mode == 'Real':
            start = time.time()
            while True and (time.time() - start) <= timeout:
                event = self.pylink.getNextData()
                event = self.pylink.getFloatData()
                if event is not None:
                    if event.getType() == 6 and checkAbort() == False:
                        esacc[0] = event.getStartTime()
                        esacc[1] = event.getEndTime()
                        esacc[2], esacc[3] = event.getStartGaze()
                        esacc[4], esacc[5] = event.getEndGaze()
                        esacc[2] -= (self.screenW / 2)
                        esacc[3] = -(esacc[3] - (self.screenH / 2))
                        esacc[4] -= (self.screenW / 2)
                        esacc[5] = -(esacc[5] - (self.screenH / 2))
                        break
        return esacc

    # Wait for fixation
    def waitForFixStart(self, fixXY=None, offset=50, timeout=4):
        """
        Wait for the start of the next fixation.
        Blocks the execution of code until the start of a fixation

        If running in dummy mode, returns the mouse position. It flips
        the window every refresh rate, any stimulus not set to
        autodraw = True, will be removed if running in dummy mode.
        By pressing escape you can manually exit the function. This is
        useful if timeout is set to a very long interval.
        The eyetracker needs to be in recording mode for this to work.

        Parameters
        ----------
        fixXY : tuple, two ints or floats
            If none, waits for the first fixation start, else the function
            returns the first fixation that starts within a certain distance
            (dist) of the given x and y coordinates. Assumes center-based
            coordinates. The input should be (x,y).
        offset :  float or int
            The maximum distance from fixXY which is acceptable, the radius
            in pixels.
            If fixXY is given, then waits until the start of a fixation that
            is a maximum of "offset" number of pixels away from the fixXY
        timeout : int or float
            The duration to block code execution and look for the start of a
            fixation, in seconds. If no start fixation detected during the
            interval the function will return a list with False.

        Returns
        -------
        fix : list
            index0: Start fixation timestamp\n
            index1: Fixation start X\n
            index2: Fixation start Y\n

            If dummy mode
            index0: None\n
            index1: Fixation start X\n
            index2: Fixation start Y\n


        Examples
        --------
        Wait for a fixation start in the center, with a radius of 50px

        >>> fix = tracker.waitForFixStart((0,0), 50, 5)
        >>> fix
        [1820292, 10,25]

        Note
        --------
        This function has not been extensively tested, consider using
        tracker.waitForFixation() instead.
        """
        fix = [None, None, None]
        if self.mode == 'Real':
            start = time.time()
            while True and (time.time() - start) <= timeout:
                event = self.pylink.getNextData()
                event = self.pylink.getFloatData()
                if event is not None:
                    if event.getType() == 7:
                        fixStart = event.getStartTime()
                        fixX, fixY = self.getCurSamp()
                        if fixXY is None:
                            fix[0] = fixStart
                            fix[1] = fixX - self.window.size[0] / 2
                            fix[2] = -(fixY - self.window.size[1] / 2)
                            break
                        dist = distBetweenPoints((fixX, fixY), fixXY)
                        if dist <= offset:
                            fix[0] = fixStart
                            fix[1] = fixX - self.window.size[0] / 2
                            fix[2] = -(fixY - self.window.size[1] / 2)
                            break
                if checkAbort():
                    break

        elif self.mode == 'Dummy':
            if fixXY is None:
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

    def waitForFixation(self, fixDot, maxDist=0, maxWait=4, nRings=3, fixTime=200):
        """
        Wait for the start of a fixation in the area around a fixDot.
        The function does not use eyelink events, but rather waits until
        a certain number of gaze samples are all within the boundary.
        If after a second there still has not been enough contiguous samples
        within the boundary, contracting circles will be shown around the
        fixDot. If after the set maximum time not enough contiguous samples
        have been detected, it will prompt the user for recalibration or
        validation.

        Press escape to prematurely exit.

        If running in dummy mode it uses the mouse position.
        This function clears the psychopy window and only draws the fixDot.

        Parameters
        ----------
        fixDot : psychopy visual shapestim
            The stimulus to use for fixation detection. usually this will be
            a psychopy visual.Circle.
        maxDist : int or float
            The maximum allowed distance from the center of the fixDot. In
            pixels. If set to 0, it uses two degrees of visual angle. The
            degrees of visual angle are determined based on the psychopy
            monitor width and distance properties.
        maxWait : int or float
            The maximum time to wait for a correct fixation before
            prompting the user about recalibration. In seconds.
        nRings : int
            The number of rings to use for constricting circles
        fixTime : int
            The duration of contiguous samples within the boundary that are
            required for successful fixation.

        Returns
        -------
        correctFixation : Bool
            True if the fixation was correct
            False if the fixation was incorrect

        Examples
        --------
        >>> fixDot = visual.Circle(win,radius=10,edges=50)
        >>> waitForFixation = tracker.waitForFixation(fixDot, 100)
        >>> waitForFixation
        True

        """
        incorrectFixationText = 'Either you are not fixating on the target or ' + \
                                'the eyetracker needs to be recalibrated.\n\nPleas notify the experimenter.\n\n' + \
                                'SPACE \t: Try again\n' + \
                                'C \t\t: Re-calibrate\n' + \
                                'V \t\t: Validate\n' + \
                                'Q \t\t: Continue without fixation control'

        # get refreshRate of screen
        hz = self.win.getActualFrameRate()
        self.startRecording()
        if self.mode == 'Real':
            self.pylink.sendCommand("record_status_message=Fixation_control")
        correctFixation = False
        trStart = time.time()
        if np.sum(fixDot.fillColor == self.win.color) == 3:
            lineColor = fixDot.lineColor
        else:
            lineColor = fixDot.fillColor

        # Detrmine the moving ring properties
        if maxDist == 0:
            maxDist = self.pxPerDeg * 2
        perimMaxRad = maxDist
        rad = perimMaxRad
        self.drawFixBoundary(fixDot.pos[0], fixDot.pos[1], rad)
        radList = []
        for i in range(int(hz / 0.5)):
            rad = rad - (perimMaxRad / (hz / 0.5)) * (2 - (rad / perimMaxRad))
            if rad >= 0:
                radList.append(rad)
        radList = np.array(radList)
        rIdx = [np.floor((len(radList) / nRings) * (i + 1)) - 1 for i in range(nRings)]

        # Make the circ stim    
        concCirc = visual.Circle(self.win, radius=perimMaxRad, fillColorSpace='rgb255',
                                 lineColorSpace='rgb255', lineColor=lineColor,
                                 fillColor=self.win.color, edges=50, pos=fixDot.pos)
        sampCount = 0
        stopCount = fixTime / (1000.0 / hz)  # stops after approx 200 ms
        while (time.time() - trStart) < maxWait:
            if self.mode != 'Dummy':
                fixation = self.getCurSamp()
                whatToDo = getKey(['c'], waitForKey=False)
                distance = distBetweenPoints(fixation, fixDot.pos)

                # Check if sample is within boundary
                if distance < maxDist:
                    sampCount += 1
                else:
                    sampCount = 0

                if whatToDo[0] == 'c':
                    break

                # If enough samples within boundary
                if sampCount >= stopCount:
                    correctFixation = True
                    break
            else:
                avgXY = self.getCurSamp()
                distance = distBetweenPoints(avgXY, fixDot.pos)

                # Check if sample is within boundary
                if distance < maxDist:
                    sampCount += 1
                else:
                    sampCount = 0

                # If enough samples within boundary
                if sampCount >= stopCount:
                    correctFixation = True
                    break

            # Draw animated fix boundary                
            if time.time() - trStart > 1:
                # Get the stim radius
                radList = np.roll(radList, -1)
                rads = [radList[int(i)] for i in rIdx]
                # Draw the larger circle first
                for rad in np.sort(rads)[::-1]:
                    concCirc.radius = rad
                    concCirc.setRadius(rad)
                    concCirc.draw()
                    if nRings == 1 and rad == np.min(radList):
                        if np.sum(concCirc.lineColor == self.win.color) == 3:
                            concCirc.lineColor = fixDot.fillColor
                        elif np.sum(concCirc.lineColor == fixDot.fillColor) == 3:
                            concCirc.lineColor = self.win.color

            fixDot.draw()
            self.win.flip()

            if checkAbort():
                break

        # only draw fixDot
        fixDot.draw()
        self.win.flip()

        # If no fixation detected
        if not correctFixation:
            drawText(self.win, incorrectFixationText, textKey=[0])
            whatToDo = getKey(['c', 'space', 'q', 'v'])
            if whatToDo[0] == 'c':
                self.calibrate()
                correctFixation = self.waitForFixation(fixDot, maxDist, maxWait, nRings)
            elif whatToDo[0] == 'space':
                correctFixation = self.waitForFixation(fixDot, maxDist, maxWait, nRings)
            elif whatToDo[0] == 'q' or whatToDo[0] == 'escape':
                correctFixation = False
            elif whatToDo[0] == 'v':
                calibrationValidation(self.win,
                                      self,
                                      nrPoints=9,
                                      dotColor=self.foreCol,
                                      pxPerDegree=self.pxPerDeg,
                                      saveFile=False)
                correctFixation = self.waitForFixation(fixDot, maxDist, maxWait, nRings)
        self.stopRecording()
        return correctFixation

    # Check abort
    def checkAbort(self):
        """
        Checks whether escape has been pressed. If escape has been pressed
        it prompts the user of it should really abort. If abort is selected
        then it sets the tracker.ABORT flag to True

        It does not actually exit any of the remaining code, you have to
        make sure the experiments stops if the escape key has been pressed.
        This function only detects the escape key press.

        Returns
        -------
        escape : True, none
            Only returns True if the escape key has been pressed. If escape was
            not pressed it does not return anything.

        Examples
        --------
        Break out of a trial loop and then out of block loop.

        >>> if tracker.checkAbort(): break
        >>> if tracker.ABORTED: break
        """
        keys = event.getKeys(['escape'])
        if keys:
            if 'escape' in keys:
                key, rt = drawText(self.win, 'Stop Experiment?\n\n"Y" \ "N"', ['y', 'n'])
                if key == 'y' or key == 'escape':
                    self.ABORTED = True
                    return True

    # Clean up
    def cleanUp(self):
        """
        Cleans up the experiment. this should be the very last function
        called in the experiment code.

        Sets eyetracker into offline mode\n
        Closes data file\n
        Closes eyetracker conection\n
        Closes eyetracker Graphics\n
        Retrieves data file to current working directory\n
        Closes psychopy window instance.

        Examples
        --------
        At the very end of the experiment code

        >>> tracker.cleanUp()
        """
        drawText(self.win, 'Experiment Finished!\n\nTransferring data!', textKey=[0])
        self.stopTrial()
        self.activeState = False
        if self.mode == 'Real':
            if pl.tracker is not None:
                time.sleep(0.2)
                self.stopRecording()

                # File transfer and cleanup!
                self.pylink.setOfflineMode()
                pl.msecDelay(500)
                # Close the file and transfer it to Display PC
                self.pylink.closeDataFile()
                # Suppress output printing
                _out = sys.stdout
                with open(os.devnull, 'w') as fd:
                    sys.stdout = fd
                    self.pylink.receiveDataFile(self.EDFDefaultName, self.EDFDefaultName)
                    sys.stdout = _out
                self.pylink.close()

                # give the tracker time to stop
                time.sleep(0.2)
                try:
                    os.rename(self.EDFDefaultName, self.EDFfileName)
                    print '\nEDF file was saved as', self.EDFfileName
                    # move the file
                    if self.fileDest:
                        try:
                            os.rename(os.path.abspath(self.EDFfileName),
                                      self.fileDest + self.EDFfileName)
                            print 'EDF file was moved to\n', self.fileDest + self.EDFfileName
                        except:
                            print '\nError while moving EDF file!!'
                            print 'Manually move the file!!'
                            print 'Currently saved as', os.path.abspath(self.EDFfileName), '!!'
                except:
                    print '\nError while renaming EDF file!!'
                    print self.EDFfileName, 'Allready exists!!'
                    print 'Manually rename the file!!'
                    print 'Currently saved as', self.EDFDefaultName, '!!'
        if self.mouse:
            self.mouse.setVisible(1)
        self.win.close()


# ==============================================================================
#  Make class for getting experiment info from user (incomplete)
# ==============================================================================
# ==============================================================================
# Enter a save filename
# ==============================================================================
def giveFileName(windowName='Please enter Filename'):
    fileGui = tk.Tk()
    fileGui.withdraw()
    fileGui.lift()
    fileGui.attributes('-topmost', True)
    fileDir = filedialog.asksaveasfilename(title=windowName)
    fileGui.destroy()
    return fileDir


class getParticipantInfo(tk.Tk):
    """
    This class is useful for getting participant and session information.
    Use this at the start of each experiment to get the participant number,
    date of birth etc

    Returns
    -------
    info.info : OrderedDict
        A dictionary with participant information

    Examples
    --------
    >>> import psychoLink as pl
    >>> info = pl.getParticipantInfo() # initiate
    >>> info.classRun() # Run
    >>> ppInfo = info.info #Save information to dict
    >>> ppInfo
    OrderedDict([('ppNr', 1),
                 ('sessionNr', 1),
                 ('ppGender', 'Male'),
                 ('ppHandedness', 'Right'),
                 ('ppOccCorrection', 'No'),
                 ('ppLeftEye', 0.0),
                 ('ppRightEye', 0.0),
                 ('ppBirthDay', '1/1/1960'),
                 ('curDate', '27/03/2018'),
                 ('saveAs', 'PP1S1')])
    """

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
        self.dispInstruct = tk.StringVar()
        self.dispInstruct.set(self.instruct)
        instr = tk.Label(self,
                         textvariable=self.dispInstruct,
                         font=self.textFont)
        instr.pack(pady=self.topDist)

    def makeExperimentInfo(self):
        subGroup = tk.LabelFrame(self,
                                 text='Experiment info',
                                 padx=self.padx,
                                 pady=self.pady,
                                 borderwidth=self.borderWidth,
                                 font=self.textFont)
        subGroup.grid(row=0, columnspan=7, sticky='W',
                      padx=5, pady=5, ipadx=5, ipady=5)
        subGroup.pack()

        # Subject nr entry
        subjectNrLabel = tk.Label(subGroup, text="Participant Nr:")
        sessionNrLabel = tk.Label(subGroup, text="Session Nr:")
        subjectNrLabel.grid(row=0, column=0)
        sessionNrLabel.grid(row=1, column=0)

        subjectNr = range(1, 51)
        sessionNr = range(1, 11)
        self.subjectNrOptions = tk.StringVar()
        self.sessionNrOptions = tk.StringVar()
        self.subjectNrOptions.set(subjectNr[0])
        self.sessionNrOptions.set(sessionNr[0])
        self.subjectNrEntry = tk.OptionMenu(subGroup, self.subjectNrOptions, *subjectNr)
        self.sessionNrEntry = tk.OptionMenu(subGroup, self.sessionNrOptions, *sessionNr)
        self.subjectNrEntry.grid(row=0, column=1)
        self.sessionNrEntry.grid(row=1, column=1)

        saveAsButton = tk.Button(subGroup,
                                 text="Save as",
                                 command=self.saveFileName)
        saveAsButton.grid(row=2, column=1)

    def makeDemoGraph(self):
        demoGroup = tk.LabelFrame(self,
                                  text='Demographics',
                                  padx=self.padx,
                                  pady=self.pady,
                                  borderwidth=self.borderWidth,
                                  font=self.textFont)
        demoGroup.grid(row=0, columnspan=7, sticky='W',
                       padx=5, pady=5, ipadx=5, ipady=5)
        demoGroup.pack()

        # Age entry
        ageLabel = tk.Label(demoGroup, text="Date of birth:")
        dayLabel = tk.Label(demoGroup, text="day")
        monthLabel = tk.Label(demoGroup, text="month")
        yearLabel = tk.Label(demoGroup, text="year")
        ageLabel.grid(row=1, column=0)
        dayLabel.grid(row=0, column=1)
        monthLabel.grid(row=0, column=2)
        yearLabel.grid(row=0, column=3)

        day = range(1, 32)
        month = range(1, 13)
        year = range(1960, 2020)
        self.dayOptions = tk.StringVar()
        self.dayOptions.set(day[0])
        self.monthOptions = tk.StringVar()
        self.monthOptions.set(month[0])
        self.yearOptions = tk.StringVar()
        self.yearOptions.set(year[0])
        self.ageEntryDay = tk.OptionMenu(demoGroup, self.dayOptions, *day)
        self.ageEntryMonth = tk.OptionMenu(demoGroup, self.monthOptions, *month)
        self.ageEntryYear = tk.OptionMenu(demoGroup, self.yearOptions, *year)

        self.ageEntryDay.grid(row=1, column=1)
        self.ageEntryMonth.grid(row=1, column=2)
        self.ageEntryYear.grid(row=1, column=3)

        # Eye entry
        eyeLabel = tk.Label(demoGroup, text="Occular correction")
        rightEyeLabel = tk.Label(demoGroup, text="Right eye")
        leftEyeLabel = tk.Label(demoGroup, text="Left eye")
        eyeLabel.grid(row=3, column=0)
        rightEyeLabel.grid(row=2, column=2)
        leftEyeLabel.grid(row=2, column=3)

        correction = ['No', 'Glasses', 'Contacts: Soft', 'Contacts: Hard']
        right = np.round(np.arange(-5, 5, 0.1), 2)
        left = np.round(np.arange(-5, 5, 0.1), 2)
        self.correctionOptions = tk.StringVar()
        self.correctionOptions.set(correction[0])
        self.rightOptions = tk.StringVar()
        self.rightOptions.set(0)
        self.leftOptions = tk.StringVar()
        self.leftOptions.set(0)
        self.correctionEntry = tk.OptionMenu(demoGroup, self.correctionOptions, *correction)
        self.rightEntry = tk.OptionMenu(demoGroup, self.rightOptions, *right)
        self.leftEntry = tk.OptionMenu(demoGroup, self.leftOptions, *left)

        self.correctionEntry.grid(row=3, column=1)
        self.rightEntry.grid(row=3, column=2)
        self.leftEntry.grid(row=3, column=3)

        # handedness entry
        handOptions = ['Right', 'Left', 'Ambidextrous']
        handLabel = tk.Label(demoGroup, text="Handedness:")
        self.handOptions = tk.StringVar()
        self.handOptions.set(handOptions[0])
        self.handEntry = tk.OptionMenu(demoGroup, self.handOptions, *handOptions)
        handLabel.grid(row=4, column=0)
        self.handEntry.grid(row=4, column=1)

        # Gender entry
        genderOptions = ['Male', 'Female', 'Other']
        genderLabel = tk.Label(demoGroup, text="Gender:")
        self.genderOptions = tk.StringVar()
        self.genderOptions.set(genderOptions[0])
        self.genderEntry = tk.OptionMenu(demoGroup, self.genderOptions, *genderOptions)
        genderLabel.grid(row=5, column=0)
        self.genderEntry.grid(row=5, column=1)

    # make the button which closes everything
    def makeStartButton(self):
        closeButton = tk.Button(self,
                                text="Start!",
                                command=self.start)
        closeButton.pack(side=tk.BOTTOM)

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

    def getAge(self):
        currDate = [int(i) for i in self.currentDate.split('/')]
        birthDay = [int(i) for i in self.birthDay.split('/')]
        del self.birthDay
        return currDate[-1] - birthDay[-1] - ((currDate[-2], currDate[-3]) < (birthDay[-2], birthDay[-3]))
    
    def saveInfo(self):
        from collections import OrderedDict
        par = OrderedDict()
        par['ppNr'] = self.ppNr
        par['sessionNr'] = self.sessionNr
        par['ppGender'] = self.gender
        par['ppHandedness'] = self.handedness
        par['ppOccCorrection'] = self.occularCorrection
        par['ppLeftEye'] = self.leftEyeCorrection
        par['ppRightEye'] = self.rightEyeCorrection
        par['ppAge'] = self.getAge()
        par['curDate'] = self.currentDate
        par['saveAs'] = self.saveAs
        self.info = par

    # =========================================================================
    # Define what happens when buttons are pressed
    # =========================================================================
    # This stops and destroys the GUI
    def start(self):
        self.ppNr = int(self.subjectNrOptions.get())
        self.sessionNr = int(self.sessionNrOptions.get())
        self.handedness = self.handOptions.get()
        self.gender = self.genderOptions.get()
        self.birthDay = str(self.dayOptions.get()) + '/' + \
                        str(self.monthOptions.get()) + '/' + \
                        str(self.yearOptions.get())
        self.occularCorrection = self.correctionOptions.get()
        self.rightEyeCorrection = float(self.rightOptions.get())
        self.leftEyeCorrection = float(self.leftOptions.get())

        if len(self.saveAs) == 0:
            self.saveAs = 'PP' + str(self.ppNr) + 'S' + str(self.sessionNr)

        self.saveInfo()
        self.destroy()

    def saveFileName(self):
        self.saveAs = giveFileName()


# =============================================================================
# Eyelink core graphics
# =============================================================================
class FixationTarget(object):
    def __init__(self, psychopy_eyelink_graphics):
        self.calibrationPointOuter = visual.Circle(
            psychopy_eyelink_graphics.window,
            pos=(0, 0),
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
            pos=(0, 0), lineWidth=1.0,
            lineColor=psychopy_eyelink_graphics.CALIBRATION_POINT_INNER_COLOR,
            lineColorSpace='rgb255',
            fillColor=psychopy_eyelink_graphics.CALIBRATION_POINT_INNER_COLOR,
            fillColorSpace='rgb255',
            radius=psychopy_eyelink_graphics.CALIBRATION_POINT_INNER_RADIUS,
            name='CP_INNER',
            units='pix',
            opacity=1.0,
            interpolate=False)

    def draw(self, pos=None):
        if pos:
            self.calibrationPointOuter.pos = pos
            self.calibrationPointInner.pos = pos
        self.calibrationPointOuter.draw()
        self.calibrationPointInner.draw()


# Intro Screen
class BlankScreen(object):
    def __init__(self, psychopy_win, color):
        self.display_size = psychopy_win.size
        w, h = self.display_size
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
    def __init__(self, psychopy_win):
        self.display_size = psychopy_win.size
        self.win = psychopy_win

        color = (0, 0, 0)
        if np.sum(psychopy_win.color < 100) == 3:
            color = (255, 255, 255)

        self.textLine = visual.TextStim(self.win,
                                        text="****************",
                                        pos=(0, 0),
                                        height=30,
                                        color=color, colorSpace='rgb255',
                                        opacity=1.0, contrast=1.0, units='pix',
                                        ori=0.0, antialias=True,
                                        bold=False, italic=False, alignHoriz='center',
                                        alignVert='center', wrapWidth=self.display_size[0] * .8)

    def draw(self, text=None):
        if text:
            self.textLine.text = text
            self.textLine.setText(text)
        self.textLine.draw()


# Intro Screen
class IntroScreen(object):
    def __init__(self, psychopy_win):
        self.display_size = psychopy_win.size
        self.window = psychopy_win
        line_count = 25
        font_height = self.display_size[1] / 50
        space_per_lines = int(font_height * 2.5)
        total_line_height = space_per_lines * line_count
        topline_y = int(min(total_line_height / 1.5, self.display_size[1] / 2 - self.display_size[1] / 5.5))
        left_margin = -self.display_size[0] / 2.1
        color = (0, 0, 0)

        # Make sure that the text can be read
        if np.sum(psychopy_win.color < 100) == 3:
            color = (255, 255, 255)

        # Draw psycholink image
        self.im = None
        try:
            imLoc = os.path.dirname(os.path.realpath(__file__)) + '\\psychoLink.png'
            im = visual.ImageStim(self.window, imLoc)
            self.im = im
            scaleFactor = self.display_size[0] / 1920.0
            self.im.setSize([scaleFactor * i for i in self.im.size])
            yUpper = topline_y - space_per_lines + (self.im.size[1] / 2)
            xLeft = left_margin + (self.im.size[0] / 2)
            self.im.pos = (xLeft, yUpper)
        except:
            pass

        self.introlines = []

        self.introlines.append(visual.TextStim(self.window,
                                               text="PsychoLink",
                                               pos=(left_margin, topline_y - space_per_lines * 2),
                                               height=int(font_height * 1.66),
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
                                               wrapWidth=self.display_size[0] * .8))

        self.introlines.append(visual.TextStim(self.window,
                                               text="ENTER: Show eye image",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
                                               color=color, colorSpace='rgb255',
                                               opacity=1.0, contrast=1.0, units='pix',
                                               ori=0.0, antialias=True,
                                               bold=False, italic=False, alignHoriz='left',
                                               alignVert='center', wrapWidth=self.display_size[0] * .8))

        self.introlines.append(visual.TextStim(self.window,
                                               text="C: Start Calibration",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
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
                                               wrapWidth=self.display_size[0] * .8))

        self.introlines.append(visual.TextStim(self.window,
                                               text="V: Start Validation",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
                                               color=color, colorSpace='rgb255',
                                               opacity=1.0, contrast=1.0, units='pix',
                                               ori=0.0, antialias=True,
                                               bold=False, italic=False, alignHoriz='left',
                                               alignVert='center', wrapWidth=self.display_size[0] * .8))

        self.introlines.append(visual.TextStim(self.window,
                                               text="ESCAPE: Return to Experiment",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
                                               color=color, colorSpace='rgb255',
                                               opacity=1.0, contrast=1.0, units='pix',
                                               ori=0.0, antialias=True,
                                               bold=False, italic=False, alignHoriz='left',
                                               alignVert='center', wrapWidth=self.display_size[0] * .8))

        self.introlines.append(visual.TextStim(self.window,
                                               text="Left / Right Arrow: Switch Camera Views",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
                                               color=color, colorSpace='rgb255',
                                               opacity=1.0, contrast=1.0, units='pix',
                                               ori=0.0, antialias=True,
                                               bold=False, italic=False, alignHoriz='left',
                                               alignVert='center', wrapWidth=self.display_size[0] * .8))

        self.introlines.append(visual.TextStim(self.window,
                                               text="A: Auto-Threshold",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
                                               color=color, colorSpace='rgb255',
                                               opacity=1.0, contrast=1.0, units='pix',
                                               ori=0.0, antialias=True,
                                               bold=False, italic=False, alignHoriz='left',
                                               alignVert='center', wrapWidth=self.display_size[0] * .8))

        self.introlines.append(visual.TextStim(self.window,
                                               text="Up / Down Arrow: Adjust Pupil Threshold",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
                                               color=color, colorSpace='rgb255',
                                               opacity=1.0, contrast=1.0, units='pix',
                                               ori=0.0, antialias=True,
                                               bold=False, italic=False, alignHoriz='left',
                                               alignVert='center', wrapWidth=self.display_size[0] * .8))

        self.introlines.append(visual.TextStim(self.window,
                                               text="+ or -: Adjust CR Threshold.",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
                                               color=color, colorSpace='rgb255',
                                               opacity=1.0, contrast=1.0, units='pix',
                                               ori=0.0, antialias=True,
                                               bold=False, italic=False, alignHoriz='left',
                                               alignVert='center', wrapWidth=self.display_size[0] * .8))
        self.introlines.append(visual.TextStim(self.window,
                                               text="I: Toggle extra information.",
                                               pos=(
                                               left_margin, topline_y - space_per_lines * (len(self.introlines) + 2)),
                                               height=font_height,
                                               color=color, colorSpace='rgb255',
                                               opacity=1.0, contrast=1.0, units='pix',
                                               ori=0.0, antialias=True,
                                               bold=False, italic=False, alignHoriz='left',
                                               alignVert='center', wrapWidth=self.display_size[0] * .8))

    def draw(self):
        if self.im is not None:
            self.im.draw()
        for s in self.introlines:
            s.draw()

try: 
    2/0
    class EyeLinkCoreGraphicsPsychopy(pl.EyeLinkCustomDisplay):
        WINDOW_BACKGROUND_COLOR = (128, 128, 128)
        CALIBRATION_POINT_OUTER_RADIUS = 15.0, 15.0
        CALIBRATION_POINT_OUTER_EDGE_COUNT = 64
        CALIBRATION_POINT_OUTER_COLOR = (255, 255, 255)
        CALIBRATION_POINT_INNER_RADIUS = 3.0, 3.0
        CALIBRATION_POINT_INNER_EDGE_COUNT = 32
        CALIBRATION_POINT_INNER_COLOR = (25, 25, 25)
    
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
            self.width, self.height = self.window.size
            self.size = self.window.size
            self.image_scale = 1
            self.image_size = None
    
            if sys.byteorder == 'little':
                self.byteorder = 1
            else:
                self.byteorder = 0
    
            EyeLinkCoreGraphicsPsychopy.CALIBRATION_POINT_OUTER_COLOR = targetForegroundColor
            EyeLinkCoreGraphicsPsychopy.CALIBRATION_POINT_INNER_COLOR = targetBackgroundColor
            EyeLinkCoreGraphicsPsychopy.WINDOW_BACKGROUND_COLOR = screenColor
            EyeLinkCoreGraphicsPsychopy.CALIBRATION_POINT_OUTER_RADIUS = targetOuterDiameter / 2.0, targetOuterDiameter / 2.0
            EyeLinkCoreGraphicsPsychopy.CALIBRATION_POINT_INNER_RADIUS = targetInnerDiameter / 2.0, targetInnerDiameter / 2.0
    
            self.blankdisplay = BlankScreen(self.window, self.WINDOW_BACKGROUND_COLOR)
            self.textmsg = TextLine(self.window)
            self.introscreen = IntroScreen(self.window)
            self.fixationpoint = FixationTarget(self)
            self.imagetitlestim = None
            self.eye_image = None
            self.state = None
            self.size = (0, 0)
            self.extra_info = False
            self.setup_cal_display()
            self.lineToDraw = visual.Line(self.window,
                                          start=(0, 0),
                                          end=(0, 0),
                                          lineWidth=1,
                                          lineColorSpace='rgb255',
                                          lineColor=[255, 0, 0],
                                          )
    
        def setMousStart(self):
            mousStart = (-(self.window.size[0] / 2), self.window.size[1] / 2)
            if self.image_size:
                mousStart = (
                (self.image_size[0] / 2) - (self.window.size[0] / 2), (self.window.size[1] / 2) - (self.image_size[1] / 2))
            else:
                mousStart = (100 - self.window.size[0] / 2, (self.window.size[1] / 2) - 100)
            self.tracker.mouse.setPos(mousStart)
    
        def get_input_key(self):
            if self.tracker.activeState:
                allowedKeys = ['up', 'down', 'left', 'right', 'return', 'escape',
                               'space', 'c', 'v', 'a', 'i', 'num_add',
                               'num_subtract']
                keycode = 0
                key = getKey(allowedKeys, False)[0]
                if key != 'NoKey':
                    keycode = key
                    if keycode == 'up':
                        keycode = pl.CURS_UP
                    elif keycode == 'down':
                        keycode = pl.CURS_DOWN
                    elif keycode == 'left':
                        keycode = pl.CURS_LEFT; self.setMousStart()
                    elif keycode == 'right':
                        keycode = pl.CURS_RIGHT; self.setMousStart()
                    elif keycode == 'return':
                        keycode = pl.ENTER_KEY; self.setMousStart()
                    elif keycode == 'escape':
                        keycode = pl.ESC_KEY
                    elif keycode == 'space':
                        keycode = ord(" ")
                    elif keycode == 'c':
                        keycode = ord("c")
                    elif keycode == 'v':
                        keycode = ord("v")
                    elif keycode == 'a':
                        keycode = ord("a")
                    elif keycode == 'i':
                        keycode = self.extra_info = not self.extra_info
                    elif keycode == 'num_add':
                        keycode = ord("+")
                    elif keycode == 'num_subtract':
                        keycode = ord("-")
                    else:
                        keycode = 0
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
            x = x - self.window.size[0] / 2
            y = -(y - self.window.size[1] / 2)
            self.blankdisplay.draw()
            self.fixationpoint.draw((x, y))
            self.window.flip()
    
        def setup_image_display(self, width, height):
            """
            Initialize the index array that will contain camera image data.
            """
    
            self.size = (width, height)
            self.clear_cal_display()
            self.last_mouse_state = -1
            if self.rgb_index_array is None:
                self.rgb_index_array = np.zeros((height, width), dtype=np.uint8)
    
        def exit_image_display(self):
            """Exits the image display."""
            self.clear_cal_display()
            self.setup_cal_display()
    
        def image_title(self, text):
            """
            Display the current camera, Pupil, and CR thresholds above
            the camera image when in Camera Setup Mode.
            """
            color = (0, 0, 0)
            if np.sum(self.window.color < 100) == 3:
                color = (255, 255, 255)
            if self.imagetitlestim is None:
                self.imagetitlestim = visual.TextStim(self.window,
                                                      text=text,
                                                      pos=(0, self.window.size[1] / 2 - 15), height=28,
                                                      color=color, colorSpace='rgb255',
                                                      opacity=1.0, contrast=1.0, units='pix',
                                                      ori=0.0, antialias=True,
                                                      bold=False, italic=False, alignHoriz='center',
                                                      alignVert='top', wrapWidth=self.window.size[0] * .8)
            else:
                self.imagetitlestim.setText(text)
            # self.imagetitlestim.draw()
    
        def draw_image_line(self, width, line, totlines, buff):
            """
            Collects all lines for an eye image, saves the image,
            then creates a psychopy imagestim from it.
            """
            for i in range(width):
                try:
                    self.rgb_index_array[line - 1, i] = buff[i]
                except Exception, e:
                    print e
    
            # Once all lines have been collected, go through the hoops needed
            # to display the frame as an image; scaled to fit the display resolution.
            if line == totlines:
                try:
                    # Remove the black edges
                    imW, imH = self.rgb_index_array.shape
                    frameRSide = self.rgb_index_array[:, imW / 2:]
                    frameLhalf = self.rgb_index_array[imH / 2:, :]
                    if np.median(frameRSide) == 0 and np.median(frameLhalf) == 0:
                        im = self.rgb_index_array[:imW / 2, :imH / 2]
                        self.image_scale = 2
                    else:
                        im = self.rgb_index_array
                        self.image_scale = 4
                    image = scipy.misc.toimage(im, pal=self.rgb_pallete, mode='P')
                    if self.imgstim_size is None:
                        maxsz = self.width / 2
                        mx = 1.0
                        while (mx + 1) * self.size[0] <= maxsz:
                            mx += 1.0
                        self.imgstim_size = int(self.size[0] * mx), int(self.size[1] * mx)
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
                    if self.imagetitlestim:
                        self.imagetitlestim.draw()
                    if self.extra_info:
                        self.draw_cross_hair()
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
            """
            # if pylink_sound_index == pl.CAL_TARG_BEEP:
            #    pass
            if pylink_sound_index == pl.CAL_ERR_BEEP or pylink_sound_index == pl.DC_ERR_BEEP:
                self.textmsg.draw('Calibration Failed or Incomplete.\nPress "Enter" to return')
                self.window.flip()
            elif pylink_sound_index == pl.CAL_GOOD_BEEP:
                txt = 'Press "v" or "Enter" to continue'
                self.textmsg.draw(txt)
                self.window.flip()
    
        def draw_line(self, x1, y1, x2, y2, color_index):
            """ Used to draw crosshair, color does not work """
            if self.image_size:
                # It asumes the image is in the top left   
                x1, y1 = topLeftToCenter((x1 * self.image_scale, y1 * self.image_scale), self.image_size)
                x2, y2 = topLeftToCenter((x2 * self.image_scale, y2 * self.image_scale), self.image_size)
                self.lineToDraw.setStart((x1, y1))
                self.lineToDraw.setEnd((x2, y2))
                self.lineToDraw.draw()
    
        def draw_lozenge(self, x, y, width, height, color_index):
            """ Color does not work, Do not know what this does"""
            x1, y1 = topLeftToCenter((x, y), self.window.size)
            line = visual.Line(self.window,
                               start=(0, 0),
                               end=(0, 0),
                               lineWidth=1,
                               lineColorSpace='rgb255',
                               lineColor=[0, 255, 0],
                               )
            # Draw line 1
            line.start = (x - (width / 2), y)
            line.end = (x, y + (width / 2))
            line.draw()
            # Draw line 2
            line.start = (x + (width / 2), y)
            line.end = (x, y + (height / 2))
            line.draw()
            # Draw line 3
            line.start = (x - (width / 2), y)
            line.end = (x, y - (height / 2))
            line.draw()
            # Draw line 4
            line.start = (x + (width / 2), y)
            line.end = (x, y - (height / 2))
            line.draw()
    
        def record_abort_hide(self):
            """ No idea what this is """
            pass
    
        def get_mouse_state(self):
            """  """
            state = self.tracker.mouse.getPressed()
            pos = centerToTopLeft(self.tracker.mouse.getPos(), self.window.size)
            return pos, state[0]
except:
    EyeLinkCoreGraphicsPsychopy = 'Unable to load pylink module:\npl.EyeLinkCustomDisplay\n\nCheck for correct pylink installation.'
    print EyeLinkCoreGraphicsPsychopy
