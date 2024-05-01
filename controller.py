import numpy as np
from threading import Lock
from models.serial_model import SerialModel
from models.data_model import DataModel
from submodule.QLogic.src.QLogic import Quaternion


class Controller:
    def __init__(self, view):
        self.serial_model = SerialModel('COM10', 115200)
        self.serial_model.connect()
        self.data_model = DataModel()
        self.q = Quaternion(np.array([1, 0, 0, 0], dtype=np.float64))
        self.qW = Quaternion(np.array([1, 0, 0, 0], dtype=np.float64))
        self.lock = Lock()
        self.view = view

    def get_q(self):
        return self.q

    def run(self):
        while True:
            self.lock.acquire()
            self.serial_model.read_data()
            self.serial_model.process_data()
            self.data_model.parse(self.serial_model.get_processed_data())
            ang_vel = self.data_model.angular_velocity / 57.4
            self.qW.set_vector_as_q(ang_vel)

            self.q = self.q * self.qW * 0.5 * 0.1

            print(self.q)

            self.view.qw.setValue(self.q.w)
            self.view.qx.setValue(self.q.x)
            self.view.qy.setValue(self.q.y)
            self.view.qz.setValue(self.q.z)
            self.lock.release()
