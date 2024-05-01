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

        self.gyr_error = np.array([0, 0, 0], dtype=np.float64)
        self.counter = 0

        self.calc_gyr_error()

    def get_q(self):
        return self.q

    def calc_gyr_error(self):
        for i in range(500):
            self.serial_model.read_data()
            self.serial_model.process_data()
            if self.data_model.parse(self.serial_model.get_processed_data()):
                self.gyr_error += self.data_model.angular_velocity
                self.counter += 1

        self.gyr_error /= self.counter
        print(self.gyr_error, self.counter)

    def run(self):
        while True:
            self.lock.acquire()
            self.serial_model.read_data()
            self.serial_model.process_data()
            self.data_model.parse(self.serial_model.get_processed_data())
            ang_vel = (self.data_model.angular_velocity - self.gyr_error) / 57.4
            self.qW.set_vector_as_q(ang_vel)

            q = self.q * self.qW / 2
            self.q += q * 0.01
            self.q.normalize()

            self.view.set_acc_gyr_data(self.data_model.acceleration, ang_vel, self.q.to_numpy())
            self.view.qw.setValue(self.q.w)
            self.view.qx.setValue(self.q.x)
            self.view.qy.setValue(self.q.y)
            self.view.qz.setValue(self.q.z)
            self.lock.release()
