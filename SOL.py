
#library
import cv2
import argparse
from centroidtracker import CentroidTracker
import numpy as np
from itertools import combinations
from math import pow, sqrt
import imutils
import pylab as plt
import seaborn as sns


# Parse the arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt" )
parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel" )
parser.add_argument( '--confidence', type = float, default = 0.5, help='put confidence value for detecting the object')
pr=parser.parse_args()
mo=parser.parse_args()
co=parser.parse_args()
#arg = vars(parser.parse_args())


# Load model
net = cv2.dnn.readNetFromCaffe(pr.prototxt, mo.weights)


tracker = CentroidTracker(maxDisappeared=40, maxDistance=50)




def main():
    try:
        # Capture video
        cap = cv2.VideoCapture('v7.mov')

        object_id_list=[]

        while True:

            # Capture one frame after that onther frame (sequence of frame)
            ret, frame = cap.read()
            if not ret:
                break
                #preprossing data
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=2)


            col = frame.shape[0]
            rw = frame.shape[1]

            #resize frame
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (400,400)), 0.007843, (rw,col), (127.5, 127.5, 127.5))
        #  blob = cv2.dnn.blobFromImage(imutils.resize(frame, width=600), 0.007843, (rw, col), (127.5, 127.5, 127.5))

            #take resize frame and sed it to the model
            net.setInput(blob)
            detect = net.forward()
            rects = []

           #detect object
            for i in range(detect.shape[2]):
                confidence = detect[0, 0, i, 2]
                if confidence >co.confidence:
                    idx = int(detect[0, 0, i, 1])
                    #choose only humane detection
                    if idx != 15.00:
                        continue

                    else:
                        #boundry of object
                        xB = (detect[0, 0, i, 3] * rw)
                        yB = (detect[0, 0, i, 4] * col)
                        xT = (detect[0, 0, i, 5] * rw)
                        yT = (detect[0, 0, i, 6] * col)

                        SX = xB.astype("int")
                        SY = yB.astype("int")
                        EX = xT.astype("int")
                        EY = yT.astype("int")


                        rects.append([SX,SY,EX,EY])




            centroid_dict = dict()

            # tracker object
            #if new object count this object
            #if not new object not count it
            objects = tracker.update(rects)
            for (objectId, bbox) in objects.items():

                if objectId  not in object_id_list:
                    object_id_list.append(objectId)

                x1, y1, x2, y2 = bbox
                bbox = np.array(bbox, dtype=np.int_)


                cX = x1 + x2
                cY = y1 + y2
                # mid point
                centerX = round((cX) * 0.5)
                centerY = round((cY) * 0.5)


                # add boundry and mid point in centroid_dict
                centroid_dict[objectId] = (centerX, centerY, x1, y1, x2, y2)

            # put text in screen to display number of human
            Count=len(object_id_list)
            text = "Number_Of_Human: {}".format(Count)
            cv2.putText(frame, text, (7, 50), cv2.FAST_FEATURE_DETECTOR_TYPE_5_8, 0.6, (0,255, 0), 2)

    #///////////////////////////////////////////////////////////////


#(blue,green,red)

            #/////////////////////////////////////////////////////////////////



            close_objects = set()

            #distance between object
            for (id1, p1), (id2, p2) in combinations(centroid_dict.items(), 2):
                distance = sqrt(pow((p1[0] - p2[0]),2) +pow((p1[1] - p2[1]),2))
                #check distance if less than 1.5 m
                if distance < 100.50:
                      close_objects.add(id1)
                      close_objects.add(id2)

            #loop for every object in frame
            for id, box in centroid_dict.items():
                # If distance less than 1.5 draw rectangle red
                # If distance more than 1.5 draw rectangle green
                if id in close_objects:

                    cv2.rectangle(frame, (box[2], box[3]), (box[4], box[5]), (0, 0, 255),2)

                else:

                    cv2.rectangle(frame, (box[2], box[3]), (box[4], box[5]),(0, 255, 0), 2)

            #To show frame
            cv2.imshow("Application", frame)
            key = cv2.waitKey(1)
            #to exit
            if key == ord('q'):
                break

        cv2.destroyAllWindows()
    #To catch error when intrrupt  display video

    except KeyboardInterrupt:
        print(" \n please complete the  video to accurate result by observing :)")


main()
