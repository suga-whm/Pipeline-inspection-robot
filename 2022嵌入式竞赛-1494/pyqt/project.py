# 姓名：戴亮
# 开发时间：2022/7/7 18:19
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
from lib.share import SI


class MyWindow1(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./画面1.ui")
        self.ui.pushButton.clicked.connect(self.onSignIn)
        self.ui.pushButton_2.clicked.connect(self.close)

    def onSignIn(self):
        SI.win2 = MyWindow2()
        SI.win2.ui.show()
        SI.win1.ui.hide()

    def close(self):
        SI.win1.ui.close()


class MyWindow2(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./画面2.ui")
        self.ui.pushButton.clicked.connect(self.logout)

    def logout(self):
        SI.win1.ui.show()
        SI.win2.ui.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    SI.win1 = MyWindow1()
    SI.win1.ui.show()

    app.exec()