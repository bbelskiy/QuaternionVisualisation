import math
import time
import types
import numpy as np
from view.ui.ui import Ui_MainWindow, QtWidgets
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import threading
from submodule.QLogic.src.QLogic import Quaternion


class ViewQVisualiser(Ui_MainWindow):
    def __init__(self, main_window):
        super(ViewQVisualiser, self).__init__()
        self.main_window = main_window
        self.main_window.setFixedSize(964, 643)

        # Змінюємо метод closeEvent для вікна
        self.main_window.closeEvent = types.MethodType(self.__close_event, self.main_window)

        self.setupUi(main_window)

        # Шести-осьова анімація обертання об'єкта в просторі
        self.q = Quaternion()

        self.vector_len = 0.1
        self.text_vector_distance = 0.12

        background = (30, 30, 10)

        gx = gl.GLGridItem()
        gx.setSize(x=0.3, y=0.3, z=0.3)
        gx.setSpacing(x=0.01, y=0.01, z=0.01)
        gx.rotate(90, 0, 1, 0)
        gx.translate(-0.15, 0, 0)
        self.six_dof_animation.addItem(gx)

        gy = gl.GLGridItem()
        gy.setSize(x=0.3, y=0.3, z=0.3)
        gy.setSpacing(x=0.01, y=0.01, z=0.01)
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -0.15, 0)
        self.six_dof_animation.addItem(gy)

        gz = gl.GLGridItem()
        gz.setSize(x=0.3, y=0.3, z=0.3)
        gz.setSpacing(x=0.01, y=0.01, z=0.01)
        gz.translate(0, 0, -0.15)
        self.six_dof_animation.addItem(gz)
        self.zero_point = np.array([0, 0, 0])  # specify the (x, y, z) values of the first point in a tuple

        self.x_point = np.array([0, self.vector_len, 0])  # specify the (x, y, z) values of the second point in a tuple
        self.y_point = np.array([0, 0, self.vector_len])
        self.z_point = np.array([self.vector_len, 0, 0])
        self.rot_vector_point = np.zeros(3)

        self.x_text_point = np.array([0, self.text_vector_distance, 0])
        self.y_text_point = np.array([0, 0, self.text_vector_distance])
        self.z_text_point = np.array([self.text_vector_distance, 0, 0])

        self.x_axis = gl.GLLinePlotItem(pos=np.array([self.zero_point, self.x_point]), width=3)
        self.y_axis = gl.GLLinePlotItem(pos=np.array([self.zero_point, self.y_point]), width=3)
        self.z_axis = gl.GLLinePlotItem(pos=np.array([self.zero_point, self.z_point]), width=3)
        self.rot_vector_axis = gl.GLLinePlotItem(pos=np.array([self.zero_point, self.rot_vector_point]), width=3)

        self.x_axis.setData(color=(1, 0, 0, 1))
        self.y_axis.setData(color=(1, 1, 0, 1))
        self.z_axis.setData(color=(0, 0, 1, 1))
        self.rot_vector_axis.setData(color=(1, 1, 1, 0.5))

        self.six_dof_animation.addItem(self.x_axis)
        self.six_dof_animation.addItem(self.y_axis)
        self.six_dof_animation.addItem(self.z_axis)
        self.six_dof_animation.addItem(self.rot_vector_axis)

        self.text_item_x = gl.GLTextItem(pos=self.x_text_point, text='X', color=(255, 0, 0, 200))
        self.six_dof_animation.addItem(self.text_item_x)

        self.text_item_y = gl.GLTextItem(pos=self.y_text_point, text='Y', color=(255, 255, 0, 200))
        self.six_dof_animation.addItem(self.text_item_y)

        self.text_item_z = gl.GLTextItem(pos=self.z_text_point, text='Z', color=(0, 0, 255, 200))
        self.six_dof_animation.addItem(self.text_item_z)

        self.six_dof_animation.setCameraPosition(distance=0.5)
        self.six_dof_animation.setBackgroundColor(background)

        self.update_q()
        self.update_euler()
        self.update()

        self.connector()

    def __close_event(self, window, event):
        """
        Callback for close of windows event
        """
        event.accept()

    def connector(self):
        """
        Initialization events with callbacks
        """
        self.angle.valueChanged.connect(self.callback_rotation_vector)
        self.vx.valueChanged.connect(self.callback_rotation_vector)
        self.vy.valueChanged.connect(self.callback_rotation_vector)
        self.vz.valueChanged.connect(self.callback_rotation_vector)
        self.cb_show_vector.clicked.connect(self.callback_show_rot_vector)
        self.qw.valueChanged.connect(self.callback_q)
        self.qx.valueChanged.connect(self.callback_q)
        self.qy.valueChanged.connect(self.callback_q)
        self.qz.valueChanged.connect(self.callback_q)

        self.roll.valueChanged.connect(self.callback_euler)
        self.pitch.valueChanged.connect(self.callback_euler)
        self.yaw.valueChanged.connect(self.callback_euler)

        self.bt_play_animation.clicked.connect(self.callback_animation)
        self.bt_clear.clicked.connect(self.callback_clear)

    def callback_q(self):
        """
        Callback which callings when changing quaternion double spin boxes
        """
        self.q.set_using_q(np.array([
            self.qw.value(), self.qx.value(), self.qy.value(), self.qz.value()
        ]))

        self.update_rotation_vector()
        self.update_euler()
        self.update()

    def callback_euler(self):
        roll = np.deg2rad(self.roll.value())
        pitch = np.deg2rad(self.pitch.value())
        yaw = np.deg2rad(self.yaw.value())

        self.q.set_using_euler(np.array([roll, pitch, yaw]))

        self.update_rotation_vector()
        self.update_q()
        self.update()

    def callback_rotation_vector(self):
        angle = np.deg2rad(self.angle.value())
        vx = self.vx.value()
        vy = self.vy.value()
        vz = self.vz.value()

        self.q.set_using_rotation_vector(np.array([angle, vx, vy, vz], dtype=np.float64))

        self.update_euler()
        self.update_q()
        self.update()

    def callback_show_rot_vector(self):
        if self.cb_show_vector.isChecked():
            self.update()
        else:
            vector = np.zeros(3)
            self.rot_vector_axis.setData(pos=np.array([np.zeros(3), self.vector_len * vector]))

    def callback_clear(self):
        self.qw.setValue(1)
        self.qx.setValue(0)
        self.qy.setValue(0)
        self.qz.setValue(0)
        self.lb_formula.setText(
            f"cos({self.angle.value()}/2)   +   sin({self.angle.value()}/2) * ({self.vx.value()} + {self.vy.value()} + {self.vz.value()})")

    def callback_animation(self):
        anim = threading.Thread(target=self.animation_update, args=())
        anim.start()

    def animation_update(self):
        step = self.angle.value() / 40
        sleep = 0.05
        for i in np.arange(0, self.angle.value() + step, step):
            self.angle.setValue(i)
            time.sleep(sleep)

    def update_rotation_vector(self):
        self.angle.blockSignals(True)
        self.vx.blockSignals(True)
        self.vy.blockSignals(True)
        self.vz.blockSignals(True)

        rotation_vector = self.q.rotation_vector
        self.angle.setValue(rotation_vector[0])
        self.vx.setValue(rotation_vector[1])
        self.vy.setValue(rotation_vector[2])
        self.vz.setValue(rotation_vector[3])

        self.angle.blockSignals(False)
        self.vx.blockSignals(False)
        self.vy.blockSignals(False)
        self.vz.blockSignals(False)

    def update_euler(self):
        self.roll.blockSignals(True)
        self.pitch.blockSignals(True)
        self.yaw.blockSignals(True)

        euler = self.q.euler
        self.roll.setValue(euler[0])
        self.pitch.setValue(euler[1])
        self.yaw.setValue(euler[2])

        self.roll.blockSignals(False)
        self.pitch.blockSignals(False)
        self.yaw.blockSignals(False)

    def update_q(self):
        self.qw.blockSignals(True)
        self.qx.blockSignals(True)
        self.qy.blockSignals(True)
        self.qz.blockSignals(True)

        self.qw.setValue(self.q.w)
        self.qx.setValue(self.q.x)
        self.qy.setValue(self.q.y)
        self.qz.setValue(self.q.z)

        self.qw.blockSignals(False)
        self.qx.blockSignals(False)
        self.qy.blockSignals(False)
        self.qz.blockSignals(False)

        self.lb_formula.setText(
            f"cos({self.angle.value()}/2)   +   sin({self.angle.value()}/2) * ({self.vx.value()} + {self.vy.value()} + {self.vz.value()})")

    def update(self):
        """
        Update normalized quaternion, norm of quaternion, direct cosine matrix and 3D visualisation
        """
        self.teznor.setText(str(self.q.length))
        vector_val = self.q.rotation_vector

        self.qwn.setText(str(self.q.w))
        self.qxn.setText(str(self.q.x))
        self.qyn.setText(str(self.q.y))
        self.qzn.setText(str(self.q.z))

        dcm = self.q.dcm_for_qt
        self.Xz.setText(str(dcm[0][1]))
        self.Xx.setText(str(dcm[1][1]))
        self.Xy.setText(str(dcm[2][1]))

        self.Yz.setText(str(dcm[0][2]))
        self.Yx.setText(str(dcm[1][2]))
        self.Yy.setText(str(dcm[2][2]))

        self.Zz.setText(str(dcm[0][0]))
        self.Zx.setText(str(dcm[1][0]))
        self.Zy.setText(str(dcm[2][0]))

        # Set X vector
        self.x_axis.setData(pos=np.array([np.zeros(3), self.vector_len * dcm[:, 1].copy()]))
        self.text_item_x.setData(pos=self.text_vector_distance * dcm[:, 1].copy())

        # Set Y vector
        self.y_axis.setData(pos=np.array([np.zeros(3), self.vector_len * dcm[:, 2].copy()]))
        self.text_item_y.setData(pos=self.text_vector_distance * dcm[:, 2].copy())

        # Set Z vector
        self.z_axis.setData(pos=np.array([np.zeros(3), self.vector_len * dcm[:, 0].copy()]))
        self.text_item_z.setData(pos=self.text_vector_distance * dcm[:, 0].copy())

        if self.cb_show_vector.isChecked():
            vector = np.array([vector_val[3], vector_val[1], vector_val[2]])
            self.rot_vector_axis.setData(pos=np.array([np.zeros(3), self.vector_len * vector]))
