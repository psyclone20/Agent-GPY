# USAGE
# python deep_learning_object_detection.py --image images/example_01.jpg \
#	--prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
import numpy as np
from PIL import ImageGrab
import argparse
import cv2
import os

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False, help="path to input image")
# -------------------------------------------------- Change here
# ap.add_argument("-p", "--prototxt", required=True, help="path to Caffe 'deploy' prototxt file")
# ap.add_argument("-m", "--model", required=True, help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2, help="minimum probability to filter weak detections")
args = vars(ap.parse_args())



dir = os.path.dirname(__file__)
pathToProtoTxt = os.path.join(dir, 'MobileNetSSD_deploy.prototxt.txt')
pathToModel = os.path.join(dir, 'MobileNetSSD_deploy.caffemodel')



# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
# -------------------------------------------------- Change here
# net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
net = cv2.dnn.readNetFromCaffe(pathToProtoTxt, pathToModel)


# load the input image and construct an input blob for the image
# by resizing to a fixed 300x300 pixels and then normalizing it
# (note: normalization is done via the authors of the MobileNet SSD
# implementation)
# image = cv2.imread(args["image"]) custom comment
# (h, w) = image.shape[:2] custom comment
(h, w) = (1080, 1920)
# blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5) custom comment
# blob = cv2.dnn.blobFromImage(image, 0.007843, (1280, 960), 127.5) custom comment





def runDeepLearningObjectDetection(image):
    returnList = []
    # image = np.array(ImageGrab.grab(bbox=(0, 0, w, h)))
    blob = cv2.dnn.blobFromImage(image, 0.007843, (w, h), 127.5)


    # print("[INFO] computing object detections...")
    net.setInput(blob)
    detections = net.forward()

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # Custom confidence value
        if confidence > 0.8:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")



            # label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            label = "{}".format(CLASSES[idx])
            # print("[TARGET-INFO]:{}:{},{},{},{}".format(label, startX, startY, endX, endY))
            cv2.rectangle(image, (startX, startY), (endX, endY),
                COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(image, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

            if label.find('person') != -1:
                returnList.append((confidence, startX, startY, endX, endY))


    # show the output image
    # cv2.imshow("Output", image)
    # cv2.imwrite("C:\Users\WindowsFour\Desktop\frame_" + i + ".jpg", image)
    # cv2.waitKey(0)

    if returnList:
        return returnList
