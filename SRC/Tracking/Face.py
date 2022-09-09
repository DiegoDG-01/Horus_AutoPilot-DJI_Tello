import cv2
import numpy as np
from os import getcwd
from pathlib import Path

class FaceTracking:

    def __init__(self):

        self.ModelPath = getcwd()

        self.Frame_Queue = None
        self.Coordinates_Pipe = None

        self.pError = 0

    def __face_recognition(self, frame, height, width):

        FaceList = []
        FaceListArea = []

        frame_resized = cv2.resize(frame, (300, 300))
        blob = cv2.dnn.blobFromImage(frame_resized, scalefactor=1.0, size=(300, 300), mean=(104.0, 177.0, 123.0))

        self.net.setInput(blob)

        detections = self.net.forward()

        # Detect only one face
        for detection in detections[0][0]:

                if detection[2] > 0.7:
                    box = detection[3:7] * np.array([width, height, width, height])
                    (x_start, y_start, x_end, y_end) = box.astype("int")
                    cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
                    cv2.putText(frame, "Conf: {:.2f}".format(detection[2] * 100), (x_start, y_start - 5), 1, 1.2, (0, 255, 255), 2)

                    cx = (x_start + x_end) // 2
                    cy = (y_start + y_end) // 2
                    area = width * height

                    FaceList.append([cx, cy])
                    FaceListArea.append(area)

        if len(FaceListArea) != 0:
            return [FaceList[0], FaceListArea[0]]
        else:
            return [[0, 0], 0]

    def __face_tracker(self, position, width, pError):
        # PID = [kd, kp, ki]
        pid = [0.5, 0.5, 0]

        # position[0][0] = cx
        # Get central position
        PID_Error = position[0][0] - width // 2

        speed = int(pid[0] * PID_Error + pid[1] * (PID_Error - pError))
        speed = np.clip(speed, -100, 100)

        if speed <= 10:
            self.Coordinates_Pipe.append(0)
        else:
            self.Coordinates_Pipe.append(speed)

        print(speed)

        return PID_Error

    def display(self, Frame_Queue, Coordinates_Pipe):

        self.net = cv2.dnn.readNetFromCaffe(
            str(Path(self.ModelPath + "/Tracking/Data/Model/deploy.prototxt")),
            str(Path(self.ModelPath + "/Tracking/Data/Model/res10_300x300_ssd_iter_140000.caffemodel"))
        )

        self.Coordinates_Pipe = Coordinates_Pipe

        while True:

            if len(Frame_Queue) != 0:

                frame = Frame_Queue.pop(0)

                height, width, _ = frame.shape

                # Get face
                position = self.__face_recognition(frame, height, width)
                self.pError = self.__face_tracker(position, width, self.pError)

                frame_resized = cv2.resize(frame, (480, 270))


                # Show frame
                cv2.imshow("Frame", frame_resized)

                # Exit
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
