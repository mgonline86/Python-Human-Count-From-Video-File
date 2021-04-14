import cv2
import numpy as np
import argparse


parser = argparse.ArgumentParser()
pr=parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt" )
mo=parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel" )

pr=parser.parse_args()
mo=parser.parse_args()
th=0.5

y=0

net = cv2.dnn.readNetFromCaffe(pr.prototxt, mo.weights)



CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]




def human_detection():
    #video
    cap = cv2.VideoCapture('v1.mov.')


    while True:
        # preprossing step
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated=cv2.dilate(thresh,None,iterations=2)


        col=frame.shape[0]
        rw=frame.shape[1]

        #resize frame
        blob = cv2.dnn.blobFromImage(cv2.resize(frame,(800,800)), 0.007843, (400, 400), (127.5, 127.5, 127.5), False)
         #forword to the model
        net.setInput(blob)
        person = net.forward()

        #check object
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

                    cv2.rectangle(frame, (SX, SY), (EX, EY), (0, 0, 255), 2)

        cv2.putText(frame,"detect human", (5, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 1)


        cv2.imshow("Application", frame)
        key = cv2.waitKey(2)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()


human_detection()