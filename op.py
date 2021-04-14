
#library
import cv2
import argparse
from centroidtracker import CentroidTracker
import numpy as np
from itertools import combinations
from math import pow, sqrt
import imutils

# Parse the arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt" )
parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel" )
parser.add_argument( '--confidence', type = float, default = 0.5, help='put confidence value for detecting the object')
pr=parser.parse_args()
mo=parser.parse_args()
co=parser.parse_args()


# Load model
net = cv2.dnn.readNetFromCaffe(pr.prototxt, mo.weights)


tracker = CentroidTracker(maxDisappeared=40, maxDistance=50)



def main():

    try:
        cap = cv2.VideoCapture('v3 with cat.mp4')

        object_id_list = []

        while True:

            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=2)
           # frame = imutils.resize(frame, width=600)
            frame = imutils.resize(frame, width=600)
            col = frame.shape[0]
            rw = frame.shape[1]


            blob = cv2.dnn.blobFromImage(frame, 0.007843, (rw, col), (127.5, 127.5, 127.5))

            net.setInput(blob)
            detect = net.forward()
            rects = []

            for i in range(0, detect.shape[2]):
                confidence = detect[0, 0, i, 2]
                if confidence > co.confidence:
                    idx = int(detect[0, 0, i, 1])

                    if idx != 15:
                        continue

                    else:
                        xB = (detect[0, 0, i, 3] * rw)
                        yB = (detect[0, 0, i, 4] * col)
                        xT = (detect[0, 0, i, 5] * rw)
                        yT = (detect[0, 0, i, 6] * col)

                        SX = xB.astype("int")
                        SY = yB.astype("int")
                        EX = xT.astype("int")
                        EY = yT.astype("int")

                        rects.append([SX, SY, EX, EY])

           # boundingboxes = np.array(rects)
          #  boundingboxes = boundingboxes.astype(int)
         #   rects = non_max_suppression_fast(boundingboxes, 0.3)
            centroid_dict = dict()
            objects = tracker.update(rects)
            for (objectId, bbox) in objects.items():

                if objectId not in object_id_list:
                    object_id_list.append(objectId)

                x1, y1, x2, y2 = bbox
                # ///////////////////////////////////////////////////////////////
                bbox = np.array(bbox, dtype=np.int_)
                #  x1 = int(x1)
                # y1 = int(y1)
                # x2 = int(x2)
                # y2 = int(y2)

                cX = x1 + x2
                cY = y1 + y2

                centerX = round((cX) * 0.5)
                centerY = round((cY) * 0.5)
                # cX = int((x1 + x2) / 2.0)
                # cY = int((y1 + y2) / 2.0)


                centroid_dict[objectId] = (centerX, centerY, x1, y1, x2, y2)

                text = "Number_Of_Human: {}".format(len(object_id_list))
                cv2.putText(frame, text, (5, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 2)



            #red_zone_list = []
            close_objects = set()
            for (id1, p1), (id2, p2) in combinations(centroid_dict.items(), 2):
                #  dx, dy = p1[0] - p2[0], p1[1] - p2[1]
                distance = sqrt(pow((p1[0] - p2[0]), 2) + pow((p1[1] - p2[1]), 2))
                if distance < 100.50:
                    #     if id1 not in red_zone_list:
                    #        red_zone_list.append(id1)
                    #   if id2 not in red_zone_list:
                    #      red_zone_list.append(id2)
                    close_objects.add(id1)
                    close_objects.add(id2)

            for id, box in centroid_dict.items():
                if id in close_objects:
                    cv2.rectangle(frame, (box[2], box[3]), (box[4], box[5]), (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame, (box[2], box[3]), (box[4], box[5]), (0, 255, 0), 2)




            cv2.imshow("Application", frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        cv2.destroyAllWindows()

    except KeyboardInterrupt:
        print(" \n please complete the  video to accurate result by observing :)")


main()