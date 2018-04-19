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
    gui.moveTo(positionX, positionY, 0.0)
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



###################################################################### Main

# scannerThread = threading.Thread(target=ObjectDetectionDeepLearning.deep_learning_object_detection.runDeepLearningObjectDetection)
# scannerThread.start()

myVar = 0
while True:
    myVar = myVar +1
    screen = cv2.cvtColor(np.array(grabscreen.grab_screen(region=(0, 30, 800, 540))), cv2.COLOR_BGR2RGB)
    startX, startY, endX, endY = recognizer.recognize(screen, args["team"])
    # arr = recognizer.recognition()
    # print (arr)
    # objectArray = ObjectDetectionDeepLearning.deep_learning_object_detection.runDeepLearningObjectDetection(screen,1270,710)
    # print(objectArray)
    if startX != -1 and startY != -1:
        # for objectCoord in objectArray:
            # print(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4])
            # square_in(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4], WINDOW_START_X+(WINDOW_WIDTH/2), WINDOW_START_Y+(WINDOW_HEIGHT/2))
            # flickMovementThread = threading.Thread(target=flick_movement, args=[startX, startY, endX, endY])
            # flickMovementThread.start()
            flick_movement(startX, startY, endX, endY)
            # flick_movement(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4])
            # break
    # print('-------------------------------------------------- ', myVar)

# square_in(220, 100, 220, 100, WINDOW_START_X+(WINDOW_WIDTH/2), WINDOW_START_Y+(WINDOW_HEIGHT/2))
###################################################################### Main
