# encfsgui Ask for master key
# 

import os
import sys
import time
import datetime
import string

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu, QAction, QStyle

import encfsgui_globals
from encfsgui_globals import *

import encfsgui_helper
from encfsgui_helper import *

class CMasterKeyWindow(QtWidgets.QDialog):
    def __init__(self):
        encfsgui_helper.print_debug("Start CMasterKeyWindow %s" % inspect.stack()[0][3])
        super(CMasterKeyWindow, self).__init__()
        uic.loadUi('encfsgui_masterkey.ui', self)
        # disable/remove buttons
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.okbutton =  self.findChild(QtWidgets.QPushButton, 'btn_OK')
        self.okbutton.clicked.connect(self.OKButtonClicked)

        self.cancelbutton = self.findChild(QtWidgets.QPushButton, 'btn_cancel')
        self.cancelbutton.clicked.connect(self.CancelButtonClicked)        

        self.txt_password = self.findChild(QtWidgets.QLineEdit, 'txt_password')
        self._password_accepted = False


    def getPassword(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        if not self._password_accepted:
            return ""
        if self.txt_password.text() == "":
            return ""
        pw = encfsgui_helper.makePW32(self.txt_password.text()[0:31])
        return pw

    def OKButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        if self.txt_password.text() == "":
            QtWidgets.QMessageBox.critical(None, "Error", "Master password cannot be empty.")
            return
        self._password_accepted = True
        self.accept()
        return

    def CancelButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self._password_accepted = False
        self.txt_password.setText("")
        self.reject()
        return
