import numpy as np
# from PIL import ImageGrab
import argparse
import cv2
import pyvjoy
import sys
import recognizer
import grabscreen
import threading
import pyautogui as gui
import directInput
from time import sleep


###################################################################### Constants
WINDOW_START_X = 0
WINDOW_START_Y = 0
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080


MAX_VJOY = 32767
MID_VJOY = 16383
###################################################################### Constants

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--team", required=True, help="team to deploy GPY in")
args = vars(ap.parse_args())

team = args["team"]


###################################################################### Screen Capture
def process_img(image):
    original_image = image
    # convert to gray
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # edge detection
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    return processed_img



def capture():
    while True:
        screen = np.array(ImageGrab.grab(bbox=(WINDOW_START_X, WINDOW_START_Y, WINDOW_START_X+WINDOW_WIDTH, WINDOW_START_Y+WINDOW_HEIGHT)))

        new_screen = process_img(screen)
        cv2.imshow('window', new_screen)

        cv2.imshow('window', cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
###################################################################### Screen Capture


###################################################################### Controller
controller = pyvjoy.VJoyDevice(1)


def square_in(startX, startY, endX, endY, windowCenterX, windowCenterY):
    midTargetX = (startX + endX) / 2
    midTargetY = (startY + endY) / 2

    diffX = midTargetX - windowCenterX
    diffY = midTargetY - windowCenterY

    # print("diffX = ", diffX)
    # print("diffY = ", diffY)
    # return


    if diffY < 0:
        verticalBias = -1
        tempDiffY = -diffY
    else:
        verticalBias = 1
        tempDiffY = diffY


    if diffX < 0:
        horizontalBias = -1
        tempDiffX = -diffX
    else:
        horizontalBias = 1
        tempDiffX = diffX


    if tempDiffX == 0 and tempDiffY == 0:
        controller.data.wAxisX = MID_VJOY
        controller.data.wAxisY = MID_VJOY
        controller.update()
        return

    if tempDiffX > tempDiffY:
        axisRatio = tempDiffY / tempDiffX
        controller.data.wAxisX = MID_VJOY + int(MID_VJOY * horizontalBias)
        controller.data.wAxisY = MID_VJOY + int((MID_VJOY * axisRatio) * verticalBias)
        controller.update()
    else:
        axisRatio = tempDiffX / tempDiffY
        controller.data.wAxisX = MID_VJOY + int((MID_VJOY * axisRatio) * horizontalBias)
        controller.data.wAxisY = MID_VJOY + int(MID_VJOY * verticalBias)
        controller.update()

    print("controller.data.wAxisX = {:.0f}%".format((controller.data.wAxisX - MID_VJOY) / MAX_VJOY * 200))
    print("controller.data.wAxisY = {:.0f}%".format((controller.data.wAxisY - MID_VJOY) / MAX_VJOY * 200))


###################################################################### Controller



###################################################################### flick_movement
    
def flick_movement(startX, startY, endX, endY):
    # distance = (startX+endX)
    update_time = gui.MINIMUM_DURATION
    positionAdjustment = 30
    positionX = (startX+endX)/2
    positionY = startY + 0.4*(endY - startY)

    print ('Moving to target location: ', positionX, positionY)

    sourceX = gui.position()[0]
    sourceY = gui.position()[1]
    # gui.moveTo((startX+endX)/2, (startY+endY)/2, duration=0.0)
    # gui.click(x=positionX, y=positionY, interval=update_time)
    # gui.moveTo(positionX, positionY, gui.MINIMUM_DURATION, gui.easeOutQuad)
    gui.moveTo(positionX, positionY, 0.0)
    # gui.moveTo(positionX, positionY, 0.0)
    # sleep(1)
    # if (startX>sourceX and startY<sourceY):
    #     gui.moveTo(positionX-positionAdjustment, positionY+positionAdjustment, update_time, gui.easeOutQuad)
    #     print ('1')
    # elif (startX>sourceX and startY>sourceY):
    #     gui.moveTo(positionX-positionAdjustment, positionY-positionAdjustment, update_time, gui.easeOutQuad)
    #     print ('2')
    # elif (startX<sourceX and startY>sourceY):
    #     gui.moveTo(positionX+positionAdjustment, positionY-positionAdjustment, update_time, gui.easeOutQuad)
    #     print ('3')
    # else:
    #     gui.moveTo(positionX+positionAdjustment, positionY+positionAdjustment, update_time, gui.easeOutQuad)
    #     print ('4')
    print("Intermediate mouse pointer location", gui.position())
    # gui.moveTo(positionX, positionY, update_time)
    gui.click()
    gui.click()
    gui.click()
    gui.click()
    gui.click()
    # print("Current mouse pointer location", gui.position())

###################################################################### flick_movement

###################################################################### Methods for Navigation

def draw_lines(img, lines):
    for line in lines:
        coords = line[0]
        cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), 255, 3)
        cv2.circle(img, (coords[0], coords[1]), 10, 255, 2)
    coords = lines[0][0]
    cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), 255, 20)

def draw_processed_lines(img, procLines):
    for line in procLines:
        # print("{}".format(line))
        cv2.line(img, (line[0],line[1]), (line[2],line[3]), 255, 3)
        cv2.circle(img, (line[0], line[1]), 10, 255, 2)


def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked

def processLines(lines):
    M_TRES = 0.5
    C_TRES = 0.5
    MAX_LINES = 8

    metaLines = []
    newLines = []
    i_newLines = -1
    
    try:


        # Store lines first
        for line in lines:
            x1,y1,x2,y2 = line[0]
            # print('//////////\n\n{} {} {} {}'.format(x1,y1,x2,y2))
            if x2-x1 == 0:
                m = 999999
            else:
                m = (y2-y1) / (x2-x1)

            c = y2 - m*x2
            
            if m == 0:
                if x1 < x2:
                    metaLines.append([x1,y1,x2,y2,m,c,False])
                else:
                    metaLines.append([x2,y2,x1,y1,m,c,False])
            else:
                if y1 < y2:
                    metaLines.append([x2,y2,x1,y1,m,c,False])
                else:
                    metaLines.append([x1,y1,x2,y2,m,c,False])
        # print("{}".format(metaLines))
        
        
        



        for i in range(MAX_LINES):
            breaker = True
            for metaLine in metaLines:
                if not metaLine[6]:
                    breaker = False
                    newLines.append(metaLine)
                    i_newLines += 1
                    metaLine[6] = True
                    break

            if breaker:
                break
            

            for metaLine in metaLines:
                if not metaLine[6]:
                    if (
                            metaLine[4] < newLines[i_newLines][4]*(1+M_TRES) and 
                            metaLine[4] > newLines[i_newLines][4]*(1-M_TRES) and
                            metaLine[5] < newLines[i_newLines][5]*(1+C_TRES) and 
                            metaLine[5] > newLines[i_newLines][5]*(1-C_TRES)
                        ):

                        # Visited
                        metaLine[6] = True
                        
                        # if not vertical
                        if metaLine[2] - metaLine[0] != 0:
                            if newLines[i_newLines][1] < metaLine[1]:
                                newLines[i_newLines][1] = metaLine[1]
                                newLines[i_newLines][0] = metaLine[0]

                            if newLines[i_newLines][3] > metaLine[3]:
                                newLines[i_newLines][3] = metaLine[3]
                                newLines[i_newLines][2] = metaLine[2]

        

        return newLines
    except TypeError:
        print("No lines found!")

    return None

def findLineLength(line):
    diffx = line[2] - line[0]
    diffy = line[3] - line[1]
    return np.sqrt(diffx*diffx + diffy*diffy)

###################################################################### Methods for Navigation



###################################################################### Main

# scannerThread = threading.Thread(target=ObjectDetectionDeepLearning.deep_learning_object_detection.runDeepLearningObjectDetection)
# scannerThread.start()

myVar = 0
tres1 = 160
tres_gap = 10

minLineLength = 40
maxLineGap = 5
threshold = 1

while True:
    myVar = myVar +1
    screen = cv2.cvtColor(np.array(grabscreen.grab_screen(region=(0, 30, 800, 540))), cv2.COLOR_BGR2RGB)


    startX, startY, endX, endY = recognizer.recognize(screen, args["team"])

    if startX != -1 and startY != -1:
        # for objectCoord in objectArray:
            # print(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4])
            # square_in(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4], WINDOW_START_X+(WINDOW_WIDTH/2), WINDOW_START_Y+(WINDOW_HEIGHT/2))
            # flickMovementThread = threading.Thread(target=flick_movement, args=[startX, startY, endX, endY])
            # flickMovementThread.start()
        print ("Shoot him!!!!!!!!!!")
        flick_movement(startX, startY, endX, endY)
            # flick_movement(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4])
            # break
    # print('-------------------------------------------------- ', myVar)

    else:

        processedScreen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        processedScreen = cv2.equalizeHist(processedScreen)

        bg_img = cv2.dilate(processedScreen, np.ones((7,7), np.uint8))

        processedScreen = 255 - cv2.absdiff(processedScreen, bg_img)
        
        norm_img = processedScreen.copy()
        cv2.normalize(processedScreen, norm_img, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        tempTres = 200
        processedScreen = cv2.Canny(processedScreen, tempTres, tempTres+1, L2gradient=False)

        # vertices = np.array([
        #     [0,320],
        #     [0,670],
        #     [780,670],
        #     [780,460],
        #     [860,460],
        #     [1140,640],
        #     [1270,640],
        #     [1270,320]])
        
        vertices = np.array([
            [0,266],
            [0,558],
            [491,558],
            [491,350],
            [542,350],
            [718,520],
            [800,520],
            [800,266]])

        processedScreen = roi(processedScreen, [vertices])

        lines = cv2.HoughLinesP(processedScreen, 1, np.pi/180, 100, 100, minLineLength, maxLineGap)

        # if startX != -1 and startY != -1:
        #     # for objectCoord in objectArray:
        #         # print(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4])
        #         # square_in(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4], WINDOW_START_X+(WINDOW_WIDTH/2), WINDOW_START_Y+(WINDOW_HEIGHT/2))
        #         # flickMovementThread = threading.Thread(target=flick_movement, args=[startX, startY, endX, endY])
        #         # flickMovementThread.start()
        #     print ("Shoot him!!!!!!!!!!")
        #     flick_movement(startX, startY, endX, endY)
        #         # flick_movement(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4])
        #         # break
        # # print('-------------------------------------------------- ', myVar)

        if not (lines is None):
            # draw_lines(processedScreen, lines)
            newLines = processLines(lines)
            draw_processed_lines(processedScreen, newLines)

            for newLine in newLines:
                if findLineLength(newLine) > 400:
                    ALMOST_FLAT_SLOPE = 0.05
                    m_pos = gui.position()
                    # print(newLine)
                    if newLine[4] > 0:
                        if newLine[4] < ALMOST_FLAT_SLOPE:
                            # print("//////////////////////////////\nSlope > 0!")
                            gui.moveTo(m_pos[0]-100)
                    elif newLine[4] < 0:
                        if newLine[4] > -ALMOST_FLAT_SLOPE:
                            # print("//////////////////////////////\nSlope < 0!")
                            gui.moveTo(m_pos[0]+100)
                            

                
                # if newLine[0] < 635 and newLine[1] > 356 and newLine[4] < 0:
                if newLine[0] < 529 and newLine[1] > 297 and newLine[4] < 0:
                    directInput.HoldKey(directInput.W, 0.2)
                    break

                # # if newLine[0] > 653 and newLine[1] > 356 and newLine[4] > 0:
                if newLine[0] > 529 and newLine[1] > 297 and newLine[4] > 0:
                    directInput.HoldKey(directInput.W, 0.2)
                    break

        else:
            gui.moveTo(500)

        cv2.imshow("TestPyWindow", processedScreen)
        if cv2.waitKey(1) and 0xFF == ord('q'):
            cv2.destroyAllWindows()        


