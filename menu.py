import sys
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

import pacman
import arkanoid
import dino


# import car


def load_file(name):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    fullname = os.path.join(base_path + '/data_menu/', name)
    if not os.path.isfile(fullname):
        print(f"Файл '{fullname}' не найден")
        sys.exit()
    else:
        return fullname


class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(load_file('ui/menu.ui'), self)

    def open_arkanoid(self):
        pass

    def open_pacman(self):
        self.hide()
        pacman.start_game()
        self.show()

    def open_dino(self):
        self.hide()
        dino.start_game()
        self.show()

    def open_car(self):
        pass

    def mousePressEvent(self, event) -> None:
        x, y = event.x(), event.y()

        if 350 < x < 680 and 20 < y < 100:
            self.open_pacman()
        elif 350 < x < 680 and 135 < y < 228:
            self.open_arkanoid()
        elif 350 < x < 680 and 250 < y < 355:
            self.open_dino()
        elif 350 < x < 680 and 380 < y < 460:
            self.open_car()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu()
    ex.show()
    sys.exit(app.exec_())
