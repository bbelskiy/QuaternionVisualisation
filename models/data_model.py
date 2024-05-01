import numpy as np


class DataModel(object):
    def __init__(self):
        self.acc = np.zeros(3, dtype=np.float32)
        self.gyr = np.zeros(3, dtype=np.float32)

    @property
    def acceleration(self) -> np.array:
        return self.acc.copy()

    @property
    def angular_velocity(self) -> np.array:
        return self.gyr.copy()

    def parse(self, data: list):
        try:
            if list:
                self.acc[0] = float(data[0])
                self.acc[1] = float(data[1])
                self.acc[2] = float(data[2])
                self.gyr[0] = float(data[3])
                self.gyr[1] = float(data[4])
                self.gyr[2] = float(data[5])
        except ValueError or TypeError or IndexError:
            pass
