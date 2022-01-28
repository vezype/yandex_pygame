import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/ui/menu.ui', self)

        self.btn_exit.clicked.connect(self.close_app)

        self.btn_arkanoid.clicked.connect(self.open_arkanoid)
        self.btn_pacman.clicked.connect(self.open_pacman)

    def close_app(self):
        sys.exit()

    def open_arkanoid(self):
        pass

    def open_pacman(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu()
    ex.show()
    sys.exit(app.exec_())
