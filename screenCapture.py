import numpy as np
from PIL import ImageGrab
import cv2
import pyvjoy
import sys
import ObjectDetectionDeepLearning.deep_learning_object_detection
import threading


###################################################################### Constants
WINDOW_START_X = 0
WINDOW_START_Y = 0
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080


MAX_VJOY = 32767
MID_VJOY = 16383
###################################################################### Constants




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

    print("diffX = ", diffX)
    print("diffY = ", diffY)
    return


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

    print("controller.data.wAxisX = ", controller.data.wAxisX)
    print("controller.data.wAxisY = ", controller.data.wAxisY)


###################################################################### Controller



###################################################################### Main

# scannerThread = threading.Thread(target=ObjectDetectionDeepLearning.deep_learning_object_detection.runDeepLearningObjectDetection)
# scannerThread.start()

myVar = 0
while True:
    myVar = myVar +1
    objectArray = ObjectDetectionDeepLearning.deep_learning_object_detection.runDeepLearningObjectDetection()
    if objectArray:
        for objectCoord in objectArray:
            # print(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4])
            square_in(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4], WINDOW_START_X+(WINDOW_WIDTH/2), WINDOW_START_Y+(WINDOW_HEIGHT/2))
            break
    print('-------------------------------------------------- ', myVar)



# square_in(220, 100, 220, 100, WINDOW_START_X+(WINDOW_WIDTH/2), WINDOW_START_Y+(WINDOW_HEIGHT/2))
###################################################################### Main
