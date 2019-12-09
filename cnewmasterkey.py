# encfsgui Create a new master key
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

class CNewMasterKey(QtWidgets.QDialog):
    def __init__(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        super(CNewMasterKey, self).__init__()
        uic.loadUi('encfsgui_newmasterkey.ui', self)
        # disable/remove buttons
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.okbutton =  self.findChild(QtWidgets.QPushButton, 'btn_OK')
        self.okbutton.clicked.connect(self.OKButtonClicked)

        self.cancelbutton = self.findChild(QtWidgets.QPushButton, 'btn_cancel')
        self.cancelbutton.clicked.connect(self.CancelButtonClicked)        

        self.txt_password1 = self.findChild(QtWidgets.QLineEdit, 'txt_password1')
        self.txt_password2 = self.findChild(QtWidgets.QLineEdit, 'txt_password2')


    def getPassword(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # make sure password is exactly 32 bytes
        pw = encfsgui_helper.makePW32(self.txt_password1.text()[0:31])
        return pw

    def OKButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # check if both passwords are the same

        errorsfound = False
        errortext = ""
        if (self.txt_password1.text() != self.txt_password2.text()):
            errorsfound = True
            errortext = "- Both passwords are not the same\n"
        if (self.txt_password1.text() == "" or self.txt_password2.text() == ""):
            errorsfound = True
            errortext = "- Password cannot be empty\n"
        if (len(self.txt_password1.text()) < 8):
            errorsfound = True
            errortext = "- Password must be 8 characters or longer\n"
        if not errorsfound:
            self.close()
        else:
            errorMsgBox = QtWidgets.QMessageBox()
            errorMsgBox.setWindowTitle("Errors found")
            errorMsgBox.setText("Unable to save password:\n\n" + errortext)
            errorMsgBox.setIcon(QMessageBox.Critical)
            errorMsgBox.show()
            errorMsgBox.exec_()
        return

    def CancelButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.txt_password1.setText("")
        self.txt_password2.setText("")
        self.close()
        return