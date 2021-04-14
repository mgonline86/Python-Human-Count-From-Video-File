# import the necessary packages

from collections import OrderedDict
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances


class CentroidTracker:
    def __init__(self, maxDisappeared=50, maxDistance=50):

        self.nextID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.bbox = OrderedDict()
        self.maxDisappeared = maxDisappeared
        self.maxDistance = maxDistance


    def update(self, rects):

        lr = len(rects)
        arr = np.array([lr, 2])
        inpc = np.zeros(arr)
        inputRects = []

        i = 0
        for ([SX, SY, EX, EY]) in (rects):
            x = (SX + EX)
            y = (SY + EY)

            Xn = x * 0.5
            Yn = y * 0.5
            cX = int(Xn)
            cY = int(Yn)

            inpc[i] = (cX, cY)
            inputRects.append(rects[i])

            i = i + 1


        if len(self.objects) != 0:

            obkey = self.objects.keys()
            obvalue = self.objects.values()

            objectIDs = list(obkey)

            OBCen = np.array(list(obvalue))

            D = euclidean_distances(OBCen, inpc)

            ro = D.min(axis=1)
            rows = sorted(range(len(ro)), key=ro.__getitem__)
            min = D.argmin(axis=1)
            cols = min[rows]

            usedRows = set()
            usedCols = set()

            for (row) in (rows):
                for (col) in (cols):

                    if row in usedRows:
                        continue
                    elif col in usedCols:
                        continue

                    if D[row, col] < self.maxDistance:

                        objectID = objectIDs[row]
                        self.objects[objectID] = inpc[col]
                        self.bbox[objectID] = inputRects[col]
                        self.disappeared[objectID] = 0

                    else:
                        continue

                    usedRows.add(row)
                    usedCols.add(col)

            un_usedR = set(range(0, D.shape[0]))
            unusedRows = un_usedR - usedRows
            un_usedC = set(range(0, D.shape[1]))
            unusedCols = un_usedC - usedCols



            if D.shape[0] >= D.shape[1]:

                for row in unusedRows:

                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    if self.disappeared[objectID] > self.maxDisappeared:
                        del self.objects[objectID]
                        del self.disappeared[objectID]
                        del self.bbox[objectID]


            else:



                for col in unusedCols:
                    self.objects[self.nextID] = inpc[col]
                    self.bbox[self.nextID] = inputRects[col]
                    self.disappeared[self.nextID] = 0
                    self.nextID += 1

        else:
            IC = len(inpc)

            for i in range(0, IC):

                self.objects[self.nextID] = inpc[i]
                self.bbox[self.nextID] = inputRects[i]  # CHANGE
                self.disappeared[self.nextID] = 0
                self.nextID += 1

        return self.bbox

