
# library
import cv2
import argparse
from centroidtracker import CentroidTracker
import numpy as np
from itertools import combinations
from math import pow, sqrt
from statistics import mode
import os
from database.models import Video, User
from datetime import datetime

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))

# Parse the arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt")
parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel")
parser.add_argument('--confidence', type=float, default=0.5,
                    help='put confidence value for detecting the object')
pr = parser.parse_args()
mo = parser.parse_args()
co = parser.parse_args()


# Load model
net = cv2.dnn.readNetFromCaffe(pr.prototxt, mo.weights)


tracker = CentroidTracker(maxDisappeared=40, maxDistance=50)


def main(video, file_name, file_extension, file_size):
    try:
        # Capture video
        cap = cv2.VideoCapture(video)

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

        object_id_list = []

        while (cap.isOpened()):

            # Capture one frame after that onther frame (sequence of frame)
            ret, frame = cap.read()
            if not ret:
                break
                # preprossing data
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=2)

            col = frame.shape[0]
            rw = frame.shape[1]

            # resize frame
            blob = cv2.dnn.blobFromImage(cv2.resize(
                frame, (400, 400)), 0.007843, (rw, col), (127.5, 127.5, 127.5))

            # take resize frame and sed it to the model
            net.setInput(blob)
            detect = net.forward()
            rect = []

           # detect object
            for i in range(detect.shape[2]):
                conf = detect[0, 0, i, 2]
                if conf > co.confidence:
                    idx = int(detect[0, 0, i, 1])
                    # choose only humane detection
                    if idx != 15.00:
                        continue

                    else:
                        # boundry of object
                        xB = (detect[0, 0, i, 3] * rw)
                        yB = (detect[0, 0, i, 4] * col)
                        xT = (detect[0, 0, i, 5] * rw)
                        yT = (detect[0, 0, i, 6] * col)

                        SX = xB.astype("int")
                        SY = yB.astype("int")
                        EX = xT.astype("int")
                        EY = yT.astype("int")

                        rect.append([SX, SY, EX, EY])

            centroid = dict()

            # tracker object
            # if new object count this object
            # if not new object not count it
            objects = tracker.update(rect)
            for (Id, bbox) in objects.items():

                if Id not in object_id_list:
                    object_id_list.append(Id)

                x1, y1, x2, y2 = bbox
                bbox = np.array(bbox, dtype=np.int_)

                cX = x1 + x2
                cY = y1 + y2
                # mid point
                centerX = round((cX) * 0.5)
                centerY = round((cY) * 0.5)

                # add boundry and mid point in centroid_dict
                centroid[Id] = (centerX, centerY, x1, y1, x2, y2)

            # put text in screen to display number of human
            text = "Number_Of_Human: {}".format(len(object_id_list))
            cv2.putText(frame, text, (7, 50),
                        cv2.FAST_FEATURE_DETECTOR_TYPE_5_8, 0.6, (255, 0, 0), 2)

            closeobjects = set()

            # distance between object
            combin = combinations(centroid.items(), 2)
            for (id1, p1), (id2, p2) in combin:
                distance = sqrt(pow((p1[0] - p2[0]), 2) +
                                pow((p1[1] - p2[1]), 2))

                # check distance if less than 1.5
                if distance < 100.50:
                    closeobjects.add(id1)
                    closeobjects.add(id2)
            i = 0
            j = 0

            # loop for every object in frame
            for id, box in centroid.items():
                # If distance less than 1.5 draw rectangle red
                # If distance more than 1.5 draw rectangle green
                # (blue,green,red)
                if id in closeobjects:
                    # Red rectangle
                    cv2.rectangle(
                        frame, (box[2], box[3]), (box[4], box[5]), (0, 0, 255), 2)
                    i += 1

                else:
                    # Green rectangle
                    cv2.rectangle(
                        frame, (box[2], box[3]), (box[4], box[5]), (0, 255, 0), 2)
                    j += 1

            # # To show frame
            # cv2.imshow("Application", frame)
            # key = cv2.waitKey(1)
            # out.write(frame)
            # # to exit
            # if key == ord('q'):
            #     break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        frame = open(os.path.join('static', 'img',
                                  'Redirecting.jpeg'), "rb").read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        # human number
        count_hum = len(object_id_list)
        most = [i]  # not safe
        notpr = [j]  # safe

       # number of people execued safty distance
        most_frequent = mode(most)
        # number of people not execued safty distance(safe people)
        notpr_frequent = mode(notpr)
        # persentage number of people execued safty distance
        # persentage of crowed
        persentage = round((most_frequent/count_hum)*100)

        out.release()
        cv2.destroyAllWindows()

        name = file_name
        extension = file_extension
        upload_date = datetime.now()
        size = file_size
        humans = count_hum
        pent = most_frequent
        not_pent = notpr_frequent
        percent = persentage
        user_id = User.query.filter_by(logged=True).first().id
        video = Video(name=name, extension=extension, upload_date=upload_date,
                      size=size, humans=humans, pent=pent, not_pent=not_pent, percent=percent, user_id=user_id)
        video.insert()

    # To catch error when intrrupt  display video
    except KeyboardInterrupt:
        print(" \n please complete the  video to accurate result by observing :)")
