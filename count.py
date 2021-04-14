import cv2
import numpy as np
import argparse
from centroidtracker import CentroidTracker

from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


parser = argparse.ArgumentParser()
pr=parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt" )
mo=parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel" )

pr=parser.parse_args()
mo=parser.parse_args()
th=0.5



net = cv2.dnn.readNetFromCaffe(pr.prototxt, mo.weights)



CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

tracker = CentroidTracker(maxDisappeared=80, maxDistance=90)


def MAX(self, maxDisappeared=50, maxDistance=50):


    self.nextObjectID = 0
    self.objects = OrderedDict()
    self.disappeared = OrderedDict()
    self.bbox = OrderedDict()  # CHANGE


    self.maxDisappeared = maxDisappeared


    self.maxDistance = maxDistance

def non_max_suppression_fast(boxes, overlapThresh):
    try:
        if len(boxes) == 0:
            return []

        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")

        pick = []

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)

        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            overlap = (w * h) / area[idxs[:last]]

            idxs = np.delete(idxs, np.concatenate(([last],
                                                   np.where(overlap > overlapThresh)[0])))

        return boxes[pick].astype("int")
    except Exception as e:
        print("Exception occurred in non_max_suppression : {}".format(e))



def human_detection():
    cap = cv2.VideoCapture('v2.mp4')
    object_id_list=[]

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=2)


        frame_rs = cv2.resize(frame, (300, 300))
        col = frame.shape[0]
        rw = frame.shape[1]

        blob = cv2.dnn.blobFromImage(frame_rs, 0.007843, (400, 400),(127.5,127.5,127.5))

        net.setInput(blob)
        person = net.forward()
        rects = []

        for i in np.arange(0, person.shape[2]):
            confidence = person[0, 0, i, 2]
            if confidence > th:
                idx = int(person[0, 0, i, 1])

                if CLASSES[idx] != "person":
                    continue
                else:
                    xB = (person[0, 0, i, 3] * rw)
                    yB = (person[0, 0, i, 4] * col)
                    xT = (person[0, 0, i, 5] * rw)
                    yT = (person[0, 0, i, 6] * col)

                    SX = xB.astype("int")
                    SY = yB.astype("int")
                    EX = xT.astype("int")
                    EY = yT.astype("int")

                    rects.append([SX,SY,EX,EY])
                    cv2.rectangle(frame, (SX, SY), (EX, EY), (255, 0, 0), 2)


        cv2.putText(frame, "DETECT", (3, 40), cv2.FAST_FEATURE_DETECTOR_TYPE_5_8, 1, (255, 0, 0), 2)

      #  BB = np.array(rects)
       # BB = BB.astype(int)
      #  rects = non_max_suppression_fast(BB, 0.3)

        objects = tracker.update(rects)
        for (objectId, bbox) in objects.items():

             if objectId not in object_id_list:
                 object_id_list.append(objectId)

        text = "Number_Of_Human: {}".format(len(object_id_list))
        cv2.putText(frame, text, (5, 90), cv2.FAST_FEATURE_DETECTOR_TYPE_5_8, 1, (0, 0, 255), 2)



        cv2.imshow("Application", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()


human_detection()

