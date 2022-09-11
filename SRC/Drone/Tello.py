from time import sleep
from pynput import keyboard
from djitellopy import Tello
from threading import Thread


class TelloAutoPilot:

    def __init__(self):

        self.Frame_Queue = None
        self.Coordinates_Pipe = None

        self.Keyboard_Listener = keyboard.Listener(on_press=self.__key_press)

        # Warning: This is var used to init flight of drone
        # Make sure this var is only true when you want init flight of the drone
        self.Flight = False
        # Warning: This is var used to know status of drone if is connected or not
        self.Connect = True
        self.Error = ""

        self.Speed_Move = 20

        # Instance of Tello
        self.MyDrone = Tello()

        try:
            self.MyDrone.connect()
            self.MyDrone.streamon()
        except AssertionError:
            self.connect = False
            self.Error = "Error To connect"

        # RC Control
        # Variables used to control the drone
        # Values between -100 and 100
        # 0 is the default value, and it means no movement
        self.MyDrone.left_right_velocity = 0
        self.MyDrone.for_back_velocity = 0
        self.MyDrone.up_down_velocity = 0
        self.MyDrone.yaw_velocity = 0

        self.MappingKey = {
            "w": self.MyDrone.for_back_velocity,
            "s": self.MyDrone.for_back_velocity,
            "a": self.MyDrone.left_right_velocity,
            "d": self.MyDrone.left_right_velocity,
        }

    def __validation(self) -> bool:

        if not self.Connect:
            self.Error = "Drone is not connected"
            return False

        if self.MyDrone.get_battery() < 15:
            self.Error = "Low Battery"
            return False

        return True

    def __get_error_validation(self) -> str:
        return self.Error

    def __flight(self) -> None:
        if self.Flight:
            self.MyDrone.takeoff()

    # Warning: This is method used to stop all motors of drone
    def __emergency(self) -> None:
        self.MyDrone.land()

    def __get_frame(self) -> object:
        return self.MyDrone.get_frame_read()

    def __key_press(self, key):
        try:
            if ord(key.char) in range(97, 123):
                self.__rc_control(key.char)
        except AttributeError:
            pass

    def __rc_control(self, key):
        try:
            if key in self.MappingKey.keys():
                if key == "w":
                    self.MyDrone.for_back_velocity += self.Speed_Move
                elif key == "s":
                    self.MyDrone.for_back_velocity -= self.Speed_Move
                elif key == "a":
                    self.MyDrone.left_right_velocity -= self.Speed_Move
                elif key == "d":
                    self.MyDrone.left_right_velocity += self.Speed_Move

            self.MyDrone.send_rc_control(
                self.MyDrone.left_right_velocity,
                self.MyDrone.for_back_velocity,
                self.MyDrone.up_down_velocity,
                self.MyDrone.yaw_velocity
            )
        except Exception:
            self.MyDrone.land()

    def __listen_position_face(self):
            while True:
                if len(self.Coordinates_Pipe) > 0:
                    if -10 < self.Coordinates_Pipe[0] > 10:
                        self.MyDrone.yaw_velocity = self.Coordinates_Pipe.pop(0)

                        self.MyDrone.send_rc_control(
                            self.MyDrone.left_right_velocity,
                            self.MyDrone.for_back_velocity,
                            self.MyDrone.up_down_velocity,
                            self.MyDrone.yaw_velocity
                        )
                    else:
                        self.Coordinates_Pipe.pop(0)



    def __show_canvas(self):

        frame_read = self.__get_frame()

        while True:
            self.Frame_Queue.append(frame_read.frame)
            sleep(0.05)

    def start(self, Frame_Queue, Coordinates_Pipe):

        self.Frame_Queue = Frame_Queue
        self.Coordinates_Pipe = Coordinates_Pipe

        if not self.__validation():
            print("Error: ", self.__get_error_validation())
            return

        # Thread to listen keyboard
        self.Keyboard_Listener.start()
        # Thread to listen position of face in frame and control drone
        Thread(target=self.__listen_position_face).start()

        # Init flight of drone
        self.__flight()
        # Thread to show frame in canvas
        self.__show_canvas()
