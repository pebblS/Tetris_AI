# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, time, pygame, sys
from pygame.locals import *
from tetrisAI import *
import sys

FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)

RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
CYAN        = (0, 222, 222)
LIGHTCYAN   = (0, 255, 255)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)
ORANGE      = (255, 127, 0)
LIGHTORANGE = (255, 165, 0)
PURPLE      = (111, 0, 128)
LIGHTPURPLE = (128, 0, 128)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (GREEN, RED, BLUE, ORANGE, CYAN, YELLOW, PURPLE)
LIGHTCOLORS = (LIGHTGREEN, LIGHTRED, LIGHTBLUE, LIGHTORANGE, LIGHTCYAN, LIGHTYELLOW, LIGHTPURPLE)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

piece_bag = list(PIECES)
random.shuffle(piece_bag)

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    global manual_mode
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    # Check for the noai launch option, disable ai
    if len(sys.argv) > 1: 
        if sys.argv[1] == "-noai":
            manual_mode = True
    else:
        manual_mode = False

    showTextScreen('Tetromino')
    while True: # game loop
#        if random.randint(0, 1) == 0:
#            pygame.mixer.music.load('tetrisb.mid')
#        else:
#            pygame.mixer.music.load('tetrisc.mid')
#        pygame.mixer.music.play(-1, 0.0)
        runGame()
#        pygame.mixer.music.stop()
        showTextScreen('Game Over')


def runGame():
    # setup variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()

    gh = gameHandler(fallingPiece, board)
    


    while True: # game loop
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            # et kaks sama juppi jarjest ei tuleks
            while nextPiece == fallingPiece:
                nextPiece = getNewPiece()
            lastFallTime = time.time() # reset lastFallTime

            if not isValidPosition(board, fallingPiece):
                return # can't fit a new piece on the board, so game over
            gh.newPiece(fallingPiece, board)

        checkForQuit()
        if manual_mode == False:
            if gh.rotatePiece(fallingPiece['rotation'], fallingPiece) != 0:
                fallingPiece['rotation'] += gh.rotatePiece(fallingPiece['rotation'], fallingPiece)
                if not isValidPosition(board, fallingPiece): # kui jupp pöörab end mängulaualt välja
                    if fallingPiece['x'] < BOARDWIDTH/2: # kui on vasakul pool mängulauda
                        while not isValidPosition(board, fallingPiece):
                            fallingPiece['x'] += 1
                    else: # jupp on paremal pool mängulauda
                        while not isValidPosition(board, fallingPiece):
                            fallingPiece['x'] -= 1
            elif gh.movePieceToPosition(fallingPiece['x']) == -1:
                movingLeft = True
            elif gh.movePieceToPosition(fallingPiece['x']) == 1:
                movingRight = True
            else: # jupp on oiges kohas ja voib alla kukutada
                    movingLeft = False
                    movingRight = False
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    fallingPiece['y'] += i - 1
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1
                    addToBoard(board, fallingPiece)
                    score += removeCompleteLines(board)
                    level, fallFreq = calculateLevelAndFallFreq(score)
                    fallingPiece = None
            
            if movingRight:
                if isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                if isValidPosition(board, fallingPiece, adjY=1):
                    fallingPiece['y'] += 1
                else:
                    # falling piece has landed, set it on the board
                    addToBoard(board, fallingPiece)
                    score += removeCompleteLines(board)
                    level, fallFreq = calculateLevelAndFallFreq(score)
                    fallingPiece = None
            if movingLeft:
                if isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                if isValidPosition(board, fallingPiece, adjY=1):
                    fallingPiece['y'] += 1
                else:
                    # falling piece has landed, set it on the board
                    addToBoard(board, fallingPiece)
                    score += removeCompleteLines(board)
                    level, fallFreq = calculateLevelAndFallFreq(score)
                    fallingPiece = None
                
        # Manual controls mode
        else:
            for event in pygame.event.get(): # event handling loop
                if event.type == KEYUP:
                    if (event.key == K_p):
                        # Pausing the game
                        DISPLAYSURF.fill(BGCOLOR)
                        pygame.mixer.music.stop()
                        showTextScreen('Paused') # pause until a key press
                        pygame.mixer.music.play(-1, 0.0)
                        lastFallTime = time.time()
                        lastMoveDownTime = time.time()
                        lastMoveSidewaysTime = time.time()
                    elif (event.key == K_LEFT or event.key == K_a):
                        movingLeft = False
                    elif (event.key == K_RIGHT or event.key == K_d):
                        movingRight = False
                    elif (event.key == K_DOWN or event.key == K_s):
                        movingDown = False

                elif event.type == KEYDOWN:
                    # moving the piece sideways
                    if (event.key == K_LEFT or event.key == K_a) and isValidPosition(board, fallingPiece, adjX=-1):
                        fallingPiece['x'] -= 1
                        movingLeft = True
                        movingRight = False
                        lastMoveSidewaysTime = time.time()

                    elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(board, fallingPiece, adjX=1):
                        fallingPiece['x'] += 1
                        movingRight = True
                        movingLeft = False
                        lastMoveSidewaysTime = time.time()

                    # rotating the piece (if there is room to rotate)
                    elif (event.key == K_UP or event.key == K_w):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                        if not isValidPosition(board, fallingPiece):
                            fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    elif (event.key == K_q): # rotate the other direction
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                        if not isValidPosition(board, fallingPiece):
                            fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])

                    # making the piece fall faster with the down key
                    elif (event.key == K_DOWN or event.key == K_s):
                        movingDown = True
                        if isValidPosition(board, fallingPiece, adjY=1):
                            fallingPiece['y'] += 1
                        lastMoveDownTime = time.time()

                    # move the current piece all the way down
                    elif event.key == K_SPACE:
                        movingDown = False
                        movingLeft = False
                        movingRight = False
                        for i in range(1, BOARDHEIGHT):
                            if not isValidPosition(board, fallingPiece, adjY=i):
                                break
                        fallingPiece['y'] += i - 1

            # handle moving the piece because of user input
            if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
                if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                lastMoveSidewaysTime = time.time()

            if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and isValidPosition(board, fallingPiece, adjY=1):
                fallingPiece['y'] += 1
                lastMoveDownTime = time.time()

            # let the piece fall if it is time to fall
            if time.time() - lastFallTime > fallFreq:
                # see if the piece has landed
                if not isValidPosition(board, fallingPiece, adjY=1):
                    # falling piece has landed, set it on the board
                    addToBoard(board, fallingPiece)
                    score += removeCompleteLines(board)
                    level, fallFreq = calculateLevelAndFallFreq(score)
                    fallingPiece = None
                else:
                    # piece did not land, just move the piece down
                    fallingPiece['y'] += 1
                    lastFallTime = time.time()
        movingDown = False
        movingLeft = False
        movingRight = False

        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece != None:
            drawPiece(fallingPiece) #praegu on out-of-bounds probleem kerge, kui juppi poorata siis peab kontrollima kas ta ikka siis ka jaab in bounds

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showTextScreen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level * 0.02)
    return level, fallFreq

def getNewPiece():
    # return a new piece from the piece bag
    global piece_bag
    if piece_bag == []:
        piece_bag = list(PIECES)
        random.shuffle(piece_bag)

    shape = piece_bag.pop(0)

    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2, # start it above the board (i.e. less than 0)
                'color' : list(PIECES.keys()).index(shape)}
    return newPiece


def addToBoard(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']


def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board


def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True

def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1 # move on to check next row up
    return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def drawBoard(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])


def drawStatus(score, level):
    # draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawPiece(piece, pixelx=None, pixely=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def drawNextPiece(piece):
    # draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # draw the "next" piece
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)


if __name__ == '__main__':
    main()