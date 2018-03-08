# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 12:27:35 2018
@author: Jonathan
"""
import psychoLink as pl
from psychopy import visual, monitors
import time
mon = monitors.Monitor('testMonitor',width=47,distance=75)
win = visual.Window(units='pix',monitor=mon,size=(1920,1080),colorSpace='rgb255',color = (255,255,255), fullscr=False)
fixDot = visual.Circle(win,radius=10,fillColorSpace='rgb255',lineColorSpace='rgb255',lineColor=[255,0,255],fillColor=[255,0,255],edges=50)
gazeDot = visual.Circle(win,radius=10,fillColorSpace='rgb255',lineColorSpace='rgb255',lineColor=[255,0,0],fillColor=[255,0,0],edges=50)
tracker = pl.eyeLink(win, fileName = 'testing.EDF')
tracker.calibrate()
for i in range(25):# Run gaze contingent display
    pl.drawText(win, 'Press "Space" to start!')
    tracker.waitForFixation(fixDot)
    tracker.startTrial()
    tracker.drawFixBoundry(0,0,100)
    tracker.sendMsg('var '+ 'trialNr '+str(i))
    s = time.time()
    while time.time() - s < 5:
        pos = tracker.getCurSamp()
        gazeDot.pos = pos
        fixDot.draw()
        gazeDot.draw()
        win.flip()
        if tracker.checkAbort(): break
    tracker.stopTrial()
    if tracker.ABORTED: break
tracker.cleanUp() 