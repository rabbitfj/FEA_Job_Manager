#!/usr/bin/env python
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication,QMainWindow
import sys
from UI_JM import Ui_MainWindow
import getpass
import os
import xlrd
from xlrd import open_workbook
import subprocess
import threading
import time
import xlutils.copy
import sqlite3
import SQL


from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from __init__ import Main


graphviz = GraphvizOutput(output_file='filter_none.png')

with PyCallGraph(output=graphviz):
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())