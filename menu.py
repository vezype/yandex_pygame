import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/ui/menu.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu()
    ex.show()
    sys.exit(app.exec_())
