import sys
from view.view import QtWidgets, ViewQVisualiser, pg
from controller import Controller

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()

    sys.exit(app.exec_())
