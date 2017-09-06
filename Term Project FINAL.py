################################################################################
### Visual Input
################################################################################

from Tkinter import *
import time

#starting from events-example0.py
def mousePressed(canvas, event):
    if not canvas.data.showHelp:
        canvas.data.restarted = False #change upper text on mouse click
        if canvas.data.stillInput:
            keyNote = getKeyNotePressed(canvas, event)
            #see how many quarter length the note is played for
            keyNoteDuration = canvas.data.rhythms[canvas.data.selectedInd][0]
            maxInput = duration.convertTypeToNumber(keyNoteDuration) #music21
            if keyNote != None: #if you click on a note
                clickedOnNote(canvas, event, maxInput, keyNote, keyNoteDuration)
            elif didRhythmChange(canvas, event) != None:
                changeRhythm(canvas, event)
            else: canvas.data.upperText = "No note added"
        if canvas.data.inputLength == maxInput: #if input is full
            canvas.data.inputText = "This window will close shortly"
        else: canvas.data.inputText = getInputText(canvas, keyNoteDuration,
                                                   canvas.data.noteText)
    redrawAll(canvas)

def clickedOnNote(canvas, event, maxInput, keyNote, keyNoteDuration):
    canvas.data.clicked = [True, event.x, event.y]
    canvas.data.inputLength += 1 #you added a note
    if canvas.data.inputLength <= maxInput: #if there's still more input data
        #add the note and duration values
        addKeyNote(canvas, keyNote, keyNoteDuration)
        if canvas.data.inputLength == maxInput: endInput(canvas)
    else: invalidInput(canvas) #does canvas.data assignments
    print "noteList: %s" % canvas.data.noteList
                              
def addKeyNote(canvas, keyNote, keyNoteDuration):
    canvas.data.noteList.append([keyNote, keyNoteDuration])
    canvas.data.upperText = "Added %s as a %s note" % (keyNote, keyNoteDuration)
                    
def mouseReleased(canvas, event):
    canvas.data.clicked[0] = False
    redrawAll(canvas)
    
def keyPressed(canvas, event):
    if event.keysym == "r":
        canvas.data.restarted = True #enable restarted text
        init(canvas) #reset function
    elif event.keysym == "u": undo(canvas)
    #toggle help
    elif event.keysym == "h": canvas.data.showHelp = not canvas.data.showHelp
    elif event.keysym == "s": canvas.data.showHelp = False #start input
    redrawAll(canvas)

def timerFired(canvas, root):
    redrawAll(canvas)
    delay = 500 #milliseconds
    if not canvas.data.stillInput:
        time.sleep(1)
        root.destroy()
        return None #fixing TCL error
    canvas.after(delay, lambda: timerFired(canvas, root))

def init(canvas):
    canvas.data.noteList = []
    initKeyboard(canvas)
    initRhythmBar(canvas)
    initUpperText(canvas)
    initTerminateVals(canvas)
    initHelpScreen(canvas)
    
def initHelpScreen(canvas):
    canvas.data.showHelp = True if not canvas.data.restarted else False
    canvas.data.XMLViewer = "MuseScore" #on my machine
    #to keep everything within 80 characters to line
    xmlV = canvas.data.XMLViewer 
    tL=["This tool allows you to generate four measure pieces",
        "based on solely one measure of input.",
        " ",
        "Click on piano with your mouse.",
        "Press 'u' to undo your last move.",
        "Press 'r' to restart the program.",
        "Press 'h' to toggle this help screen.",
        " ",
        "Once you input a measure, the window will automatically close.",
        "The command prompt will show the process of creating your piece.",
        " ",
        "Once the piece is complete, the default musicXML viewer",
        "(currently %s) will automatically open, displaying your piece." % xmlV]
    canvas.data.textList = tL
    
    
def initTerminateVals(canvas):
    canvas.data.stillInput, canvas.data.inputLength = True, 0

def initUpperText(canvas):
    canvas.data.upperTextCoord = (canvas.data.winWidth / 2,
                                  (canvas.data.marginY -
                                   canvas.data.rhythmMarginY) / 4)
    if canvas.data.restarted: canvas.data.upperText = "Restarted"
    else: canvas.data.upperText = "Press on a note"
    canvas.data.upperTextFont = ("Arial", 2 * canvas.data.marginY / 15)

def initKeyboard(canvas):
    canvas.data.marginY = 150 #starter value
    #calculations
    canvas.data.whiteKeyBottom = canvas.data.winHeight + 1
    canvas.data.numberOfKeys = ((canvas.data.winWidth - 2 * canvas.data.marginX)
                                / canvas.data.keyWidth)
    canvas.data.blackKeyWidth = 3 * canvas.data.keyWidth / 4
    canvas.data.blackKeyMargin = (2 * canvas.data.keyWidth -
                                  canvas.data.blackKeyWidth) / 2
    #keyboard letter names and whether they have a sharp key associated
    canvas.data.whiteKeys = ["C",  "D",   "E",  "F",  "G",  "A",   "B"]
    canvas.data.hasSharp = [True, True, False, True, True, True, False]
    canvas.data.clicked = [False, 0, 0]

def initRhythmBar(canvas):
    canvas.data.rhythms = [["64th", False], ["32nd", False], ["16th", False],
                           ["eighth", False], ["quarter", True],
                           ["half", False], ["whole", False]]
    #quarter is "True" at start
    canvas.data.rhythmMarginY, canvas.data.selectedInd = 50, 4
    startingNote = canvas.data.rhythms[canvas.data.selectedInd][0]
    noteLengthStart = duration.convertTypeToNumber(startingNote) #music21 module
    canvas.data.inputText = "You have %d %s notes left" % (noteLengthStart,
                                                           startingNote)
    canvas.data.noteText = startingNote #last note added, default to "quarter"

def undo(canvas):
    if len(canvas.data.noteList) >= 1: #if we are able to undo anything
        lastMove = canvas.data.noteList.pop() #save it to display later
        undoDuration = lastMove[1]
        #in order to activate float division
        newRhythm = (1.0 * duration.convertTypeToNumber(canvas.data.noteText) /
                     duration.convertTypeToNumber(undoDuration)) #conversion
        canvas.data.inputLength -= newRhythm #for style purposes
        canvas.data.upperText = "Undid %s as a %s note" % (lastMove[0],
                                                           lastMove[1])
        #for style purposes
    else: canvas.data.upperText = "No moves left to undo"
    maxInput = duration.convertTypeToNumber(canvas.data.noteText) #module
    lengthLeft = maxInput - canvas.data.inputLength #for style
    #to remove unnecessary floats
    if lengthLeft % 1 == 0: lengthLeft = int(lengthLeft)
    inputTextQuals = (lengthLeft, canvas.data.noteText) #for style
    canvas.data.inputText = "You have %s %s notes left" % inputTextQuals

def getKeyNotePressed(canvas, event):
    if not isKey(canvas, event): return None #no keyNote pressed, in margin
    if isWhiteKey(canvas, event):
        return getWhiteKeyNotePressed(canvas, event.x)
    elif isBlackKey(canvas, event):
        return getBlackKeyNotePressed(canvas, event.x)

def isKey(canvas, event):
    #1. Is it left of the keyboard margin?
    #2. Is is right of the keyboard margin?
    #3. Is it below the keyboard margin?
    #4. Is it above the keyboard margin?
    return (event.x > canvas.data.marginX and
            event.x < canvas.data.winWidth - canvas.data.marginX and
            event.y > canvas.data.marginY and
            event.y < canvas.data.whiteKeyBottom)
    
def getWhiteKeyNotePressed(canvas, locationX):
    #find number of keys location is left of bottom A
    keyNoteIndex = (locationX - canvas.data.marginX) / canvas.data.keyWidth
    #find scale position (A - G)
    noteIndex = keyNoteIndex % len(canvas.data.whiteKeys)
    #find how many octaves above bottom A key is in
    octaveIndex = keyNoteIndex / len(canvas.data.whiteKeys)
    octaveIndex = getCorrectOctave(canvas, octaveIndex)
    return "%s%d" % (canvas.data.whiteKeys[noteIndex], octaveIndex) #ex. A5

def getBlackKeyNotePressed(canvas, locationX):
    #use getWhiteKeyNotePressed to find associated white key
    #shift location so that black keys are on top of white keys
    whiteNote = getWhiteKeyNotePressed(canvas, (locationX -
                                                canvas.data.blackKeyMargin))
    letter, octave = whiteNote[0], whiteNote[1] #given the formatting in result
    return "%s#%s" % (whiteNote[0], whiteNote[1])

def getCorrectOctave(canvas, octaveIndex):
    #formula tested and constructed from all of the results from
    #c.d.numOfKeys : 8 --> 69
    middleAIndex, octaveCorrector = 4, 14
    return (octaveIndex + middleAIndex -
            (canvas.data.numberOfKeys + 1) / octaveCorrector)

def isWhiteKey(canvas, event):
    if event.y > (canvas.data.winHeight + canvas.data.marginY) / 2:
        return True #lower white key
    else:
        return testUpperWhiteKey(canvas, event.x) #could be an upper white key

def testUpperWhiteKey(canvas, locationX):
    (relativeLocationX, keyNoteIndex, noteIndex) = doCalcs(canvas, locationX)
    #find the left neighboring note
    leftNoteIndex = (noteIndex - 1) % len(canvas.data.whiteKeys)
    #for a spot in between two black keys, then leftNote and note have sharps
    if keyNoteIndex == 0: #lowest A, edge case
        return testRightBlackKey(canvas, relativeLocationX)
    elif keyNoteIndex == canvas.data.numberOfKeys: #highest note, edge case
        return testLeftBlackKey(canvas, relativeLocationX) 
    #edge cases done, now normal cases
    if canvas.data.hasSharp[leftNoteIndex] and canvas.data.hasSharp[noteIndex]:
        return (relativeLocationX > canvas.data.blackKeyWidth / 2 and
                relativeLocationX < (canvas.data.keyWidth -
                                     canvas.data.blackKeyWidth / 2))
    elif canvas.data.hasSharp[leftNoteIndex]:
        return testLeftBlackKey(canvas, relativeLocationX)
    elif canvas.data.hasSharp[noteIndex]:
        return testRightBlackKey(canvas, relativeLocationX)
    #else: The piano keyboard is not a keyboard, since no more than two white
    #   keys are directly next to each other without any black keys in between.

def doCalcs(canvas, locationX):
    relativeLocationX = (locationX - canvas.data.marginX) % canvas.data.keyWidth
    #from getWhiteKeyNotePressed
    keyNoteIndex = (locationX - canvas.data.marginX) / canvas.data.keyWidth
    noteIndex = keyNoteIndex % len(canvas.data.whiteKeys)
    return (relativeLocationX, keyNoteIndex, noteIndex)

def testLeftBlackKey(canvas, relativeLocationX):
    #see if the click is further right than how far the black key extrudes out
    return relativeLocationX > canvas.data.blackKeyWidth / 2

def testRightBlackKey(canvas, relativeLocationX):
    #opposite side of testLeftBlackKey, same width into white key
    return relativeLocationX < (canvas.data.keyWidth -
                                canvas.data.blackKeyWidth / 2)
    
def isBlackKey(canvas, event):
    #1. Is it right of the first black key?
    #2. Is it left of the last black key?
    return (event.x >= canvas.data.blackKeyMargin + canvas.data.marginX and
            event.x < (canvas.data.winWidth - canvas.data.marginX -
                       canvas.data.blackKeyMargin))

def endInput(canvas):
    canvas.data.upperText = canvas.data.upperText + " to complete input"
    canvas.data.stillInput = False

def invalidInput(canvas):
    canvas.data.inputLength -= 1
    canvas.data.upperText = "Invalid entry, too many notes"

def changeRhythm(canvas, event):
    rhythmInd = didRhythmChange(canvas, event)
    canvas.data.rhythms[rhythmInd][1] = True
    canvas.data.rhythms[canvas.data.selectedInd][1] = False
    canvas.data.selectedInd = rhythmInd
    canvas.data.noteText = canvas.data.rhythms[rhythmInd][0]
    canvas.data.upperText = "Inputting %s notes" % canvas.data.noteText
            
def didRhythmChange(canvas, event):
    if (event.x > canvas.data.marginX and
        event.x < canvas.data.winWidth - canvas.data.marginX and
        event.y > canvas.data.marginY / 2 and event.y < canvas.data.marginY):
        return newRhythm(canvas, event.x)

def newRhythm(canvas, locationX):
    section = locationX * len(canvas.data.rhythms) / canvas.data.winWidth
    rhythmText = canvas.data.rhythms[section][0] #based on formatting
    for rhythmInd in xrange(len(canvas.data.rhythms)):
        if (rhythmText == canvas.data.rhythms[rhythmInd][0] and
            rhythmInd != canvas.data.selectedInd): return rhythmInd

def getInputText(canvas, lastDuration, newDuration):
    modifier = (1.0 * duration.convertTypeToNumber(newDuration) /
                duration.convertTypeToNumber(lastDuration))
    canvas.data.inputLength *= modifier
    lengthLeft = duration.convertTypeToNumber(newDuration) - canvas.data.inputLength
    if lengthLeft % 1 == 0: lengthLeft = int(lengthLeft)
    return "You have %s %s notes left" % (lengthLeft, newDuration)

def run(numberOfKeys=17, winHeight=450):
    assurances(numberOfKeys, winHeight)
    root = Tk() #begin run function
    root.resizable(width=FALSE, height=FALSE) #using nonResizableDemo.py
    keyWidth, marginX = 40, 2 #calculations
    winWidth = numberOfKeys * keyWidth + 2 * marginX #for margin issues
    canvas = Canvas(root, width=winWidth, height=winHeight) #finish run function
    canvas.pack(fill=BOTH, expand=YES) #using nonResizableDemo.py
    class Struct: pass
    canvas.data = Struct()
    assignments(canvas, keyWidth, marginX, winWidth, winHeight, numberOfKeys)
    init(canvas)
    root.bind("<Button-1>", lambda event: mousePressed(canvas, event))
    root.bind("<B1-ButtonRelease>", lambda event: mouseReleased(canvas, event))
    root.bind("<Key>", lambda event: keyPressed(canvas, event))
    timerFired(canvas, root)
    root.mainloop()
    return canvas.data.noteList

def assurances(numberOfKeys, winHeight):
    minWinHt, minNumOfKeys = 300, 17 #minWinHeight
    if winHeight < minWinHt:
        print "Too small height!\nTry %d or greater (recommend 450)" % minWinHt
        sys.exit()
    elif numberOfKeys < minNumOfKeys:
        print "Too few keys!\nTry %d or greater" % minNumOfKeys
        sys.exit()

def assignments(canvas, keyWidth, marginX, winWidth, winHeight, numberOfKeys):
    canvas.data.keyWidth, canvas.data.marginX = keyWidth, marginX
    canvas.data.winWidth, canvas.data.winHeight = winWidth, winHeight
    canvas.data.numberOfKeys = numberOfKeys
    canvas.data.restarted = False #so that we can see restarted text later

def redrawAll(canvas):
    canvas.delete(ALL)
    if canvas.data.showHelp: drawHelp(canvas)
    else:
        drawPiano(canvas)
        drawText(canvas)
        drawHelpText(canvas)
        drawRhythm(canvas)
        drawInputBar(canvas)

def drawHelp(canvas):
    canvas.create_text(canvas.data.upperTextCoord,
                       text="Music Generation Tool",
                       font=canvas.data.upperTextFont)
    startLine, smallTextSize, largeTextSize = 70, 14, 24
    lenTextList = len(canvas.data.textList)
    spacer = ((canvas.data.winHeight - startLine - 2 * largeTextSize)
              / lenTextList)
    for textInd in xrange(lenTextList):
        smallCoords = (canvas.data.winWidth / 2,
                       startLine + smallTextSize + spacer * textInd)
        canvas.create_text(smallCoords, text=canvas.data.textList[textInd],
                           font=("Times", smallTextSize))
    #large text is at the bottom of the function
    largeCoords = (canvas.data.winWidth / 2,
                   canvas.data.winHeight - largeTextSize)
    canvas.create_text(largeCoords, text="Press 's' to start program",
                       font=("Arial", largeTextSize), fill="red")
    
def drawPiano(canvas):
    drawPianoWhiteKeys(canvas)
    drawPianoBlackKeys(canvas)

def drawPianoWhiteKeys(canvas):
    for key in xrange(canvas.data.numberOfKeys): #draw white keys
        whiteX0 = key * canvas.data.keyWidth + canvas.data.marginX
        whiteY0 = canvas.data.marginY #below upper buttons and text
        whiteX1 = whiteX0 + canvas.data.keyWidth #go a keyWidth right
        whiteY1 = canvas.data.whiteKeyBottom
        whitePoints = (whiteX0, whiteY0, whiteX1, whiteY1)
        #drawing the click thing by changing the color of the key
        whiteKeyColor = getWhiteKeyColor(canvas, whitePoints, key) 
        canvas.create_rectangle(whitePoints, fill=whiteKeyColor) #white key draw
        #draw letter names
        fontSize = canvas.data.keyWidth / 2 #proportional to keyWidth
        letterCoords = ((whiteX0 + whiteX1) / 2, whiteY1 - fontSize)
        canvas.create_text(letterCoords, text=canvas.data.whiteKeys[key % 7],
                           font=("Arial", fontSize))
        canvas.data.whiteY0 = whiteY0 #for blackY0 in drawPianoBlackKeys

#since black must all be written over white, draw all white and then black
def drawPianoBlackKeys(canvas):
    for key in xrange(canvas.data.numberOfKeys):
        if key < canvas.data.numberOfKeys - 1 and canvas.data.hasSharp[key % 7]:
            #if valid, draw black keys
            blackX0 = (key * canvas.data.keyWidth + 5 * canvas.data.keyWidth / 8
                       + canvas.data.marginX) #so much math
            blackY0 = canvas.data.whiteY0 #all notes start from top
            blackX1 = blackX0 + canvas.data.blackKeyWidth #blackKeyWidth right
            blackY1 = (canvas.data.winHeight + blackY0) / 2 #halfway down piano
            blackPoints = (blackX0, blackY0, blackX1, blackY1)
            #doing the click thing for black, much shorter
            blackKeyColor = getBlackKeyColor(canvas, blackPoints)
            canvas.create_rectangle(blackPoints, fill=blackKeyColor)

def getBlackKeyColor(canvas, blackPoints):
    (blackX0, blackY0, blackX1, blackY1) = blackPoints
    [pressedDown, clickX, clickY] = canvas.data.clicked
    if (pressedDown and blackX0 < clickX and clickX < blackX1 and
        blackY0 < clickY and clickY < blackY1): keyColor = "blue"
    else: keyColor = "black"
    return keyColor
            
def getWhiteKeyColor(canvas, whitePoints, key):
    (whiteX0, whiteY0, whiteX1, whiteY1) = whitePoints
    [pressedDown, clickX, clickY] = canvas.data.clicked
    if pressedDown: #boolean stating if we have a held down click
        if (clickY >(canvas.data.winHeight + canvas.data.marginY) / 2 and
            clickY < whiteY1): #if lower white key
            #only needs to be in a white key, no black key to worry about
            if whiteX0 < clickX and clickX < whiteX1: keyColor = "blue"
            else: keyColor = "white" #normal
        else: keyColor = getUpperWhiteKeyColor(canvas, whiteX0, whiteX1, key)
    else: keyColor = "white" #normal
    return keyColor

def getUpperWhiteKeyColor(canvas, whiteX0, whiteX1, key):
    [pressedDown, clickX, clickY] = canvas.data.clicked
    if (canvas.data.hasSharp[key % 7] and
        canvas.data.hasSharp[(key - 1) % 7]): #if in between two black keys
        #check that it's outside the black key edges
        if (whiteX0 + canvas.data.blackKeyWidth / 2 < clickX and
            whiteX1 - canvas.data.blackKeyWidth / 2 > clickX): keyColor = "blue"
        else: keyColor = "white" #normal
    elif canvas.data.hasSharp[key % 7]: #only right black key
        if (whiteX0 < clickX and whiteX1 -
            canvas.data.blackKeyMargin / 2 > clickX): keyColor = "blue"
        else: keyColor = "white" #normal
    elif canvas.data.hasSharp[(key - 1) % 7]: #only left black key
        if (whiteX0 + canvas.data.blackKeyMargin / 2 < clickX and
            whiteX1 > clickX): keyColor = "blue"
        else: keyColor = "white" #normal
    return keyColor

def drawText(canvas): #upper text
    canvas.create_text(canvas.data.upperTextCoord, text=canvas.data.upperText,
                       font=canvas.data.upperTextFont)

def drawHelpText(canvas):
    if canvas.data.stillInput:
        #want it over the 64th rhythm, but in the upperText
        x0 = 2 * canvas.data.marginX
        x1 = canvas.data.winWidth - 2 * canvas.data.marginX
        #the texts will be on top of each other
        y = canvas.data.marginY / 6
        textFont = ("Arial", 10)
        canvas.create_text(x0, y, text="Press 'r' to restart",
                           font=textFont, anchor=W)
        canvas.create_text(x1, y, text="Press 'u' to undo",
                           font=textFont, anchor=E)

def drawInputBar(canvas):
    canvas.create_text(canvas.data.winWidth / 2, canvas.data.marginY / 2,
                       text=canvas.data.inputText,
                       font=("Times", canvas.data.marginY / 8 - 1))
    
def drawRhythm(canvas):
    for rhythmInd in xrange(len(canvas.data.rhythms)):
        rhythmWidth = ((canvas.data.winWidth - 2 * canvas.data.marginX)
                       / len(canvas.data.rhythms))
        x0 = canvas.data.marginX + rhythmInd * rhythmWidth
        y0 = canvas.data.marginY - canvas.data.rhythmMarginY
        x1, y1 = x0 + rhythmWidth, canvas.data.marginY - 1
        rhythmCoords = (x0, y0, x1, y1)
        isSelected = canvas.data.rhythms[rhythmInd][1]
        rhythmText = canvas.data.rhythms[rhythmInd][0]
        if isSelected:
            outlineColor, widthSelected = "red", 3
            canvas.create_rectangle(rhythmCoords, outline=outlineColor,
                                width=widthSelected)
        else: outlineColor, widthSelected = "black", 1
        drawNote(canvas, rhythmCoords, rhythmText)

def drawNote(canvas, rhythmCoords, note):
    (left, top, right, bottom) = rhythmCoords
    middleX, middleY = (left + right) / 2, (top + bottom) / 2
    canvas.create_text(middleX, middleY, text=note)

################################################################################
### Music Generation Algorithm
################################################################################

#NOTE: We can also run this algorithm by creating the file in MuseScore,
#      exporting the musicXML, and then parsing that into the algorithm after
#      the import statement. In this implementation, it is assumed the input
#      will be from the Tkinter piano function above.

#Linear Top-Down Design
#a.k.a. starts at the top (runMusic), then goes down in a linear fashion,
#as supposed to MVC where mainloop changes the program order frequently.

import random

print "This red text means that we have successfully imported module music21"
from music21 import *

def runMusic(noteList):
    musicVars = beginInputWithStruct(noteList)
    keyAndTonality(musicVars)
    testCreation(musicVars, noteList[-1][0])
    finishPiece(musicVars)

def beginInputWithStruct(noteList):
    if len(noteList) < 2:
        print "\nThank you for using this program!"
        sys.exit()
    print "\nRunning algorithm on..."
    for note in noteList:
        print "\t%r" % note
    print "Creating input in musicXML...",
    result = createInput(noteList)
    print "Done!"
    print "Creating Struct to save music data into...",
    class Struct(): pass
    musicVars = Struct()
    musicVars.result = result
    print "Done!"
    return musicVars

def keyAndTonality(musicVars):
    print "Finding key and tonality...",
    keySig = getKey(musicVars.result)
    print "Done!"
    print "Saving key and tonality...",
    musicVars.keySig = str(keySig)
    if "#" in musicVars.keySig or "-" in musicVars.keySig:
        musicVars.rootPitch = musicVars.keySig[0:2]
    else: musicVars.rootPitch = musicVars.keySig[0]
    print keySig

def testCreation(musicVars, lastPitchInput):
    print "Creating music..."
    print #for visual spacing
    musicVars.results = []
    musicVars.chordList, musicVars.octaveList = [], [int(lastPitchInput[-1])]
    pitchList = createPiece(musicVars, [], lastPitchInput)
    if pitchList == None:
        print "Sorry, no input could be created"
    durationList = [1, 1, 2,  1, 1, 1, 1,  1, 1, 2]
    #____Input____| -  -  5 | -  -  -  - | 4  5  1 ||
    createMeasures(musicVars, pitchList, durationList)
    print "Found a good result:", pitchList
    print #for visual spacing

def createPiece(musicVars, pitchList, lastPitchInput):
    print "List of Notes Created So Far:", pitchList
    origPossPitches = ["C", "C#", "D", "E-", "E", "F",
                       "F#", "G", "A-", "A", "B-", "B"]
    possPitches = sorted(origPossPitches, key=lambda k: random.random())
    musicVars.pitchListLen = len(pitchList)
    if musicVars.pitchListLen == 10: return pitchList
    else:
        for pitch in possPitches:
            if ((len(pitchList) == 0 and pitchInKey(musicVars, pitch)) or
                (len(pitchList) > 0 and
                 isLegal(musicVars, pitchList[-1], pitch))):
                result = createPiece(musicVars, pitchList + [pitch],
                                     lastPitchInput)
                if result != None: return result
                elif len(pitchList) > 0:
                    pitchList.pop()
                    musicVars.octaveList = musicVars.octaveList[:len(pitchList)]
                    if musicVars.octaveList == []:
                        musicVars.octaveList = [int(lastPitchInput[-1])]
        return None
    
def isLegal(musicVars, lastPitch, newPitch):
    return (pitchInKey(musicVars, newPitch) and
            validInterval(musicVars, lastPitch, newPitch) and
            validChords(musicVars, newPitch) and
            validPitchInCadence(musicVars, newPitch))

def validPitchInCadence(musicVars, newPitch):
    ### Input | - - V _ | - - - - | IV V I _ ||
    if musicVars.pitchListLen == 3-1 or musicVars.pitchListLen == 9-1:
        dominantChordNotes = [5, 7, 2]
        #the pitch better be one of those if in dominant chord
        return (musicVars.mScale.getScaleDegreeFromPitch(newPitch)
                in dominantChordNotes)
    elif musicVars.pitchListLen == 8-1:
        subDominantChordNotes = [4, 6, 1]
        #the pitch better be one of those if in subdominant chord
        return (musicVars.mScale.getScaleDegreeFromPitch(newPitch)
                in subDominantChordNotes)
    elif musicVars.pitchListLen == 10-1:
        tonicChordNotes = [1]
        #the pitch better be one of those if in tonic chord
        return (musicVars.mScale.getScaleDegreeFromPitch(newPitch)
                in tonicChordNotes)
    else: return True

import string

def pitchInKey(musicVars, pitch):
    tonic, tonality = musicVars.keySig.split()[0], musicVars.keySig.split()[1]
    if tonality == "major": musicVars.mScale = scale.MajorScale(tonic)
    elif tonality == "minor": musicVars.mScale = scale.MinorScale(tonic)
    degrees = xrange(1, 8)
    for degree in degrees:
        #match only letter names
        originalLetterPitch = string.rstrip(pitch, string.digits)
        letterPitch = originalLetterPitch.upper()
        scalePitch = str(musicVars.mScale.pitchFromDegree(degree))
        letterScale = string.rstrip(scalePitch, string.digits) #to remove octave
        if letterPitch == letterScale: return True
    return False

def validInterval(musicVars, pitch1, pitch2):
    octave = 4 #by default
    semi1 = getSemitones(pitch1, musicVars.octaveList[-1])
    semi2 = getSemitones(pitch2, octave)
    validIntervals = [ 1,   2,   3,   4,   5,   7,  12,
                      -1,  -2,  -3,  -4,  -5,  -7, -12,      0]
#                     m2,  M2,  m3,  M3,  P4,  P5,  P8, unison
    if semi2 - semi1 in validIntervals:
        musicVars.octaveList.append(octave)
        return True
    else: return False

def validChords(musicVars, nextPitch):
    if len(musicVars.chordList) > 0: lastChordNum = musicVars.chordList[-1]
    else: lastChordNum =  1 #since 1 can go to any chord
    possNextChordNums = chordNumsFromPitch(musicVars, nextPitch)
    musicVars.chordMap = {
        1: [None,  True,  True,  True,  True,  True,  True,  True],
        2: [None, False, False, False, False,  True, False,  True],
        3: [None, False, False, False,  True, False,  True, False],
        4: [None,  True,  True, False, False,  True, False,  True],
        5: [None,  True, False, False, False, False,  True, False],
        6: [None, False,  True, False, False,  True, False, False],
        7: [None,  True, False, False, False,  True, False, False]}
    for nextChordNum in possNextChordNums:
        if musicVars.chordMap[lastChordNum][nextChordNum]:
            musicVars.chordList.append(nextChordNum)
            return True
    return False

def chordNumsFromPitch(musicVars, pitch):
    chordNums, numOfPossChordNums = [], 3
    rootChordNum = musicVars.mScale.getScaleDegreeFromPitch(pitch)
    for i in xrange(numOfPossChordNums):
        originalChordNum = (rootChordNum - 2 * i) % 7
        #0 chord is not valid, presented by mod 7
        chordNum = 7 if originalChordNum == 0 else originalChordNum
        chordNums.append(chordNum)
    return chordNums
    
def getSemitones(pitch, octave):
    pitchChars = str(pitch)
    letter = (ord(pitchChars[0]) - ord("A")) * 2
    if len(pitchChars) > 1:
        if pitchChars[1] == "#": letter += 1 #semitones
        elif pitchChars[1] == "-": letter -= 1 #semitones
    return letter + 12 * octave

def randomPitch(musicVars, chordNum=None):
    tonic, tonality = musicVars.keySig.split()[0], musicVars.keySig.split()[1]
    pitchList = []
    if tonality == "major": musicVars.mScale = scale.MajorScale(tonic)
    elif tonality == "minor": musicVars.mScale = scale.MinorScale(tonic)
    degrees = xrange(1, 8)
    triadLen, triadJump = 3, 2
    for triadInd in xrange(triadLen):
        degree = (chordNum + triadInd * triadJump) % len(degrees)
        triadPitch = mScale.pitchFromDegree(degree)
        pitchList.append(triadPitch)
    num = 0 if chordNum == 1 else random.randrange(len(pitchList))
    return pitch.Pitch(pitchList[num])

def finishPiece(musicVars):
    print "Finished creation!"
    print "Displaying creation...",
    musicVars.result.show()
    print "Done!"

def createInput(noteList): #@TODO: change notes if different in new key
    inputMeasure = stream.Measure()
    for noteInfo in noteList:
        notePitch, noteDuration = noteInfo[0], noteInfo[1]
        notePitchLetter = notePitch[0:len(notePitch) - 1]
        notePitchOctave = int(notePitch[len(notePitch) - 1])
        inputNote = note.Note(notePitch)
        inputNote.duration.type = noteDuration
        inputMeasure.append(inputNote)
    inputPart = stream.Stream()
    inputPart.append(inputMeasure)
    timeSig = meter.TimeSignature('4/4') #assign common time sig.
    inputPart.append(timeSig)
    return inputPart

def getKey(inputPart):
    weights = analysis.discrete.KrumhanslKessler() #algorithm to get keyWeight
    newKey = weights.getSolution(inputPart)
    return newKey

def createMeasures(musicVars, pitchList, durationList):
    beatCounter = 0
    createdMeasure = stream.Measure()
    for i in xrange(len(pitchList)):
        beatCounter += durationList[i]
        if beatCounter > 4: #end of measure
            musicVars.result.append(createdMeasure) #add so far
            createdMeasure = stream.Measure() #initialize a new measure
            beatCounter = 1 #starting at the first beat of the next measure
        addedPitch = pitch.Pitch(pitchList[i] + str(musicVars.octaveList[i]))
        addedNote = note.Note(addedPitch, quarterLength=durationList[i])
        createdMeasure.append(addedNote)
    musicVars.result.append(createdMeasure) #add last accumulated section
        
################################################################################
### Top-Level Function Calls
################################################################################

def masterRun(numOfWhiteKeys=17, winHeight=450):
    tryAgain = True
    while tryAgain:
        noteList = run(numOfWhiteKeys, winHeight) #numOfWhiteKeys, winHeight
        runMusic(noteList)
        answer = raw_input("Try again? Y/N\n--->")
        if answer[0].lower() == "n": tryAgain = False
    print "Thank you!"

masterRun()
