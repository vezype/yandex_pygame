import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('data_menu/ui/menu.ui', self)

    def open_arkanoid(self):
        self.hide()
        import arkanoid
        sys.exit()

    def open_pacman(self):
        self.hide()
        import pacman
        sys.exit()

    def mousePressEvent(self, event) -> None:
        x, y = event.x(), event.y()

        if 350 < x < 680 and 90 < y < 170:
            self.open_pacman()
        elif 350 < x < 680 and 208 < y < 300:
            self.open_arkanoid()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu()
    ex.show()
    sys.exit(app.exec_())
