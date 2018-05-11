import numpy as np
from PIL import ImageGrab
import grabscreen
import cv2
import pyvjoy
import sys
import pyautogui
# import ObjectDetectionDeepLearning.deep_learning_object_detection
import threading
import directInput


###################################################################### Constants
WINDOW_START_X = 5
WINDOW_START_Y = 30
WINDOW_WIDTH = 1280-5
WINDOW_HEIGHT = 820


MAX_VJOY = 32767
MID_VJOY = 16383
###################################################################### Constants

















###################################################################### Screen Capture
def process_img(image):
    original_image = image
    # convert to gray
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # edge detection
    processed_img = cv2.Canny(processed_img, threshold1=500, threshold2=600)
    return processed_img

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





















############################################################ VIPER
# FISRT PIONEER // Highly unoptimized
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
    
############################################################ VIPER
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
    # directInput.PressKey(directInput.W)

    myVar = myVar +1
    # print("tres1 =",tres1,"| tres_gap =",tres_gap,"| minLineLength =",minLineLength,"| maxLineGap =",maxLineGap,"| threshold =",threshold)
    screen = cv2.cvtColor(np.array(grabscreen.grab_screen(region=(5, 30, 1275, 740))), cv2.COLOR_BGR2RGB)

    
    
    processedScreen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    processedScreen = cv2.equalizeHist(processedScreen)

    bg_img = cv2.dilate(processedScreen, np.ones((7,7), np.uint8))

    
    # processedScreen = cv2.GaussianBlur(processedScreen, (5,5), 0)
    # processedScreen = cv2.GaussianBlur(processedScreen, (5,5), 0)
    

    # processedScreen = cv2.Laplacian(processedScreen, cv2.CV_64F)
    # bg_img = cv2.medianBlur(processedScreen, 21)
    # processedScreen = cv2.bilateralFilter(processedScreen,9,75,75)

    processedScreen = 255 - cv2.absdiff(processedScreen, bg_img)
    
    norm_img = processedScreen.copy()
    cv2.normalize(processedScreen, norm_img, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    

    
    
    
    
    
    tempTres = 200
    processedScreen = cv2.Canny(processedScreen, tempTres, tempTres+1, L2gradient=False)
    # processedScreen = cv2.Canny(processedScreen, threshold1=int(tres1), threshold2=int(tres1)+tres_gap, L2gradient=False)

    

    # vertices = np.array([
    #     [0,140],
    #     [0,670],
    #     [780,670],
    #     [780,450],
    #     [820,450],
    #     [1270,650],
    #     [1270,35],
    #     [1230,35],
    #     [1200,0],
    #     [140,0],
    #     [140,110],
    #     [110,140]])
    vertices = np.array([
        [0,320],
        [0,670],
        [780,670],
        [780,460],
        [860,460],
        [1140,640],
        [1270,640],
        [1270,320]])
    processedScreen = roi(processedScreen, [vertices])
    
    

    lines = cv2.HoughLinesP(processedScreen, 1, np.pi/180, 100, 100, minLineLength, maxLineGap)
    if not (lines is None):
        # draw_lines(processedScreen, lines)
        newLines = processLines(lines)
        draw_processed_lines(processedScreen, newLines)

        for newLine in newLines:
            if findLineLength(newLine) > 400:
                ALMOST_FLAT_SLOPE = 0.05
                m_pos = pyautogui.position()
                # print(newLine)
                if newLine[4] > 0:
                    if newLine[4] < ALMOST_FLAT_SLOPE:
                        print("//////////////////////////////\nSlope > 0!")
                        pyautogui.moveTo(m_pos[0]-100)
                elif newLine[4] < 0:
                    if newLine[4] > -ALMOST_FLAT_SLOPE:
                        print("//////////////////////////////\nSlope < 0!")
                        pyautogui.moveTo(m_pos[0]+100)
                        

            
            if newLine[0] < 635 and newLine[1] > 356 and newLine[4] < 0:
                directInput.HoldKey(directInput.W, 0.1)
                break

            if newLine[0] > 653 and newLine[1] > 356 and newLine[4] > 0:
                directInput.HoldKey(directInput.W, 0.1)
                break
    




























    # newLines = processLines(lines)

    # cv2.line(processedScreen, (635,340), (635,370), (255,255,255), 1)
    # cv2.line(processedScreen, (620,356), (650,356), (255,255,255), 1)
    
    # processedScreen.reshape(2,2,2,2).average(axis=1).average(axis=2)




    # Center of screen by observation = (635, 356) // Relative X_OFFSET = 5 | Y_OFFSET = 30
    # Center of screen by calculation = (640, 385)
    

    




    # Setup wars
    # 140 0 61 x 10









    # For processing lines
    # 131 120 51 10 10      With histogram equalization
    # 131 120 51 10 10      Without

    # New MAP
    # 141 140 ? ? ?qqqqqqq


    
    
    
    
    
    cv2.imshow('PyOutWindow', processedScreen)








    # if cv2.waitKey(1) & 0xff == ord('1'):
    #     tres1 = tres1 + 5
    # if cv2.waitKey(1) & 0xff == ord('2'):
    #     tres_gap = tres_gap + 20
    # if cv2.waitKey(1) & 0xff == ord('3'):
    #     minLineLength = minLineLength + 10
    # if cv2.waitKey(1) & 0xff == ord('1'):
    #     maxLineGap = maxLineGap + 1
    # if cv2.waitKey(1) & 0xff == ord('5'):
    #     threshold = threshold + 20

    # if cv2.waitKey(1) & 0xff == ord('6'):
    #     if tres1 - 15 >= 0:
    #         tres1 = tres1 - 15
    # if cv2.waitKey(1) & 0xff == ord('7'):
    #     if tres_gap - 40 >= 0:
    #         tres_gap = tres_gap - 40
    # if cv2.waitKey(1) & 0xff == ord('8'):
    #     if minLineLength - 10 >= 0:
    #         minLineLength = minLineLength - 10
    # qqqq#         maxLineGap = maxLineGap - 1
    # if cv2.waitKey(1) & 0xff == ord('0'):
    #     if threshold - 20 >= 0:
    #         threshold = threshold - 20
    
    if cv2.waitKey(1) & 0xff == ord('q'):
        cv2.destroyAllWindows()
        break
        
        

    
cv2.destroyAllWindows()    

    # objectArray = ObjectDetectionDeepLearning.deep_learning_object_detection.runDeepLearningObjectDetection(screen)
    # if objectArray:
    #     for objectCoord in objectArray:
    #         # print(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4])
    #         square_in(objectCoord[1], objectCoord[2], objectCoord[3], objectCoord[4], WINDOW_START_X+(WINDOW_WIDTH/2), WINDOW_START_Y+(WINDOW_HEIGHT/2))
    #         break
    # print('-------------------------------------------------- ', myVar)


# square_in(220, 100, 220, 100, WINDOW_START_X+(WINDOW_WIDTH/2), WINDOW_START_Y+(WINDOW_HEIGHT/2))
###################################################################### Main
