#! /usr/bin/python
#-*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.getcwd() + "/GUI")
sys.path.append(os.getcwd() + "/Objects")
sys.path.append(os.getcwd() + "/robotImages")
sys.path.append(os.getcwd() + "/Robots")
from window import MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QSurfaceFormat


if __name__ == "__main__":

   fmt = QSurfaceFormat()
   fmt.setSwapInterval(0)
   QSurfaceFormat.setDefaultFormat(fmt)

   app = QApplication(sys.argv)
   app.setApplicationName("Python-Robocode")
   myapp = MainWindow()
   myapp.show()
   sys.exit(app.exec_())
