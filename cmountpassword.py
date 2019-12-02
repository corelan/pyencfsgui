# encfsgui Get mount password
# 
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

import encfsgui_globals
from encfsgui_globals import *

import encfsgui_helper
from encfsgui_helper import *

class CMountPassword(QtWidgets.QDialog):
    def __init__(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        super(CMountPassword, self).__init__()
        uic.loadUi('encfsgui_password.ui', self)

        # disable/remove buttons
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        self.lbl_enc_path = self.findChild(QtWidgets.QLabel, 'lbl_enc_path')
        self.lbl_mount_path = self.findChild(QtWidgets.QLabel, 'lbl_mount_path')
        self.txt_password = self.findChild(QtWidgets.QLineEdit, 'txt_password')

        self.okbutton =  self.findChild(QtWidgets.QPushButton, 'btn_OK')
        self.okbutton.clicked.connect(self.OKButtonClicked)

        self.cancelbutton = self.findChild(QtWidgets.QPushButton, 'btn_cancel')
        self.cancelbutton.clicked.connect(self.CancelButtonClicked)

    def setEncPath(self, path):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.lbl_enc_path.setText(path)
        return

    def setMountPath(self, path):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.lbl_mount_path.setText(path)
        return

    def getPassword(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        return self.txt_password.text()
    
    def OKButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.close()
        return

    def CancelButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.txt_password.setText("")
        self.close()
        return