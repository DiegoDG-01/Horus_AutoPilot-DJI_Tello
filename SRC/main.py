from Drone.Tello import TelloAutoPilot
from Tracking.Face import FaceTracking
from multiprocessing import Process, Manager
from threading import Thread

def __main() -> None:

    Frame_Queue = Manager().list([])
    Coordinates_Pipe = Manager().list([])

    # Instance of Tello
    MyDrone = TelloAutoPilot()
    # Instance of Face
    MyFace = FaceTracking()

    # Start Process
    Face_Tracking = Process(target=MyFace.display, args=(Frame_Queue, Coordinates_Pipe))
    Face_Tracking.start()

    try:
        MyDrone.start(Frame_Queue, Coordinates_Pipe)
    except Exception:
        MyDrone.__emergency()


if __name__ == "__main__":
    __main()