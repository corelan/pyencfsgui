# encfsgui Settings
# 
# 

import os
import sys
import time
import datetime
import string
import configparser

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import encfsgui_globals
from encfsgui_globals import *

import encfsgui_helper
from encfsgui_helper import *

import cconfig
from cconfig import CConfig

class CSettingsWindow(QtWidgets.QDialog):
    def __init__(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        super(CSettingsWindow, self).__init__()
        uic.loadUi('encfsgui_settings.ui', self)

        # disable/remove buttons
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        # assign methods to buttons
        self.okbutton =  self.findChild(QtWidgets.QPushButton, 'btn_OK')
        self.okbutton.clicked.connect(self.OKButtonClicked)

        self.cancelbutton = self.findChild(QtWidgets.QPushButton, 'btn_cancel')
        self.cancelbutton.clicked.connect(self.CancelButtonClicked)

        self.selectencfsbutton = self.findChild(QtWidgets.QPushButton, 'btn_selectencfs')
        self.selectencfsbutton.clicked.connect(self.SelectEncfsButtonClicked)

        self.selectmountbutton = self.findChild(QtWidgets.QPushButton, 'btn_selectmount')
        self.selectmountbutton.clicked.connect(self.SelectMountButtonClicked)

        self.selectumountbutton = self.findChild(QtWidgets.QPushButton, 'btn_selectumount')
        self.selectumountbutton.clicked.connect(self.SelectUmountButtonClicked)

        self.selectworkingfolderbutton = self.findChild(QtWidgets.QPushButton, 'btn_selectworkingfolder')
        self.selectworkingfolderbutton.clicked.connect(self.SelectWorkingFolderClicked)

        self.settingsfile = encfsgui_globals.settingsfile


    def SelectEncfsButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.txt_enfcsbinary = self.findChild(QtWidgets.QLineEdit, 'txt_encfsbinary')
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select 'encfs' binary", self.txt_enfcsbinary.displayText(),"All Files (*)", options=options)
        if fileName:
            self.txt_encfsbinary.setText("%s" % fileName)
        return

    def SelectMountButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.txt_mountbinary = self.findChild(QtWidgets.QLineEdit, 'txt_mountbinary')
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select 'mount' binary", self.txt_mountbinary.displayText(),"All Files (*)", options=options)
        if fileName:
            self.txt_mountbinary.setText("%s" % fileName)
        return

    def SelectUmountButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.txt_umountbinary = self.findChild(QtWidgets.QLineEdit, 'txt_umountbinary')
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select 'umount' binary", self.txt_umountbinary.displayText(),"All Files (*)", options=options)
        if fileName:
            
            self.txt_umountbinary.setText("%s" % fileName)
        return

    def SelectWorkingFolderClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.txt_workingfolder = self.findChild(QtWidgets.QLineEdit, 'txt_workingfolder')
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        folderName = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if folderName:
            self.txt_workingfolder.setText("%s" % folderName)
        return

    def OKButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.saveSettings()
        self.close()
        return

    def CancelButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.close()
        return

    def loadSettings(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # populate fields
        self.txt_enfcsbinary = self.findChild(QtWidgets.QLineEdit, 'txt_encfsbinary')
        self.txt_enfcsbinary.setText("%s" % encfsgui_globals.g_Settings["encfspath"])
        self.txt_mountbinary = self.findChild(QtWidgets.QLineEdit, 'txt_mountbinary')
        self.txt_mountbinary.setText("%s" % encfsgui_globals.g_Settings["mountpath"])
        self.txt_umountbinary = self.findChild(QtWidgets.QLineEdit, 'txt_umountbinary')
        self.txt_umountbinary.setText("%s" % encfsgui_globals.g_Settings["umountpath"])
        self.txt_workingfolder = self.findChild(QtWidgets.QLineEdit, 'txt_workingfolder')
        self.txt_workingfolder.setText("%s" % encfsgui_globals.g_Settings["workingfolder"])
        self.chk_starthidden = self.findChild(QtWidgets.QCheckBox, 'chk_starthidden')
        self.chk_autounmount = self.findChild(QtWidgets.QCheckBox, 'chk_autounmount')
        self.chk_autoupdate = self.findChild(QtWidgets.QCheckBox, 'chk_autoupdate')
        self.chk_noconfirmationunmount = self.findChild(QtWidgets.QCheckBox, 'chk_noconfirmationunmount')
        self.chk_noconfirmationexit = self.findChild(QtWidgets.QCheckBox, 'chk_noconfirmationexit')
        self.chk_debugmode = self.findChild(QtWidgets.QCheckBox, 'chk_debugmode')
        self.chk_confirmforceunmountall = self.findChild(QtWidgets.QCheckBox, 'chk_confirmforceunmountall')
        self.chk_doubleclickmount = self.findChild(QtWidgets.QCheckBox, 'chk_doubleclickmount')

        if (encfsgui_globals.g_Settings["autounmount"].lower() == "true"):
            self.chk_autounmount.setChecked(True)

        if (encfsgui_globals.g_Settings["starthidden"].lower() == "true"):
            self.chk_starthidden.setChecked(True)

        if (encfsgui_globals.g_Settings["noconfirmationunmount"].lower() == "true"):
            self.chk_noconfirmationunmount.setChecked(True)
        else:
            self.chk_noconfirmationunmount.setChecked(False)

        if (encfsgui_globals.g_Settings["noconfirmationexit"].lower() == "true"):
            self.chk_noconfirmationexit.setChecked(True)

        if (encfsgui_globals.g_Settings["debugmode"].lower() == "true"):
            self.chk_debugmode.setChecked(True)

        if (encfsgui_globals.g_Settings["autoupdate"].lower() == "true"):
            self.chk_autoupdate.setChecked(True)

        if (encfsgui_globals.g_Settings["confirmforceunmountall"].lower() == "true"):
            self.chk_confirmforceunmountall.setChecked(True)

        if (encfsgui_globals.g_Settings["doubleclickmount"].lower() == "true"):
            self.chk_doubleclickmount.setChecked(True)

        return


    def saveSettings(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # update global settings
        encfsgui_globals.g_Settings["encfspath"] = str(self.txt_enfcsbinary.displayText().strip())
        encfsgui_globals.g_Settings["mountpath"] = str(self.txt_mountbinary.displayText().strip())
        encfsgui_globals.g_Settings["umountpath"] = str(self.txt_umountbinary.displayText().strip())
        if (self.txt_workingfolder.displayText().strip().replace(" ","") == ""):
            self.txt_workingfolder.setText(".")
        encfsgui_globals.g_Settings["workingfolder"] = str(self.txt_workingfolder.displayText().strip())
        encfsgui_globals.g_Settings["autounmount"] = str(self.chk_autounmount.isChecked()).lower()
        encfsgui_globals.g_Settings["noconfirmationunmount"] = str(self.chk_noconfirmationunmount.isChecked()).lower()
        encfsgui_globals.g_Settings["noconfirmationexit"] = str(self.chk_noconfirmationexit.isChecked()).lower()
        encfsgui_globals.g_Settings["starthidden"] = str(self.chk_starthidden.isChecked()).lower()
        encfsgui_globals.g_Settings["debugmode"] = str(self.chk_debugmode.isChecked()).lower()
        encfsgui_globals.g_Settings["autoupdate"] = str(self.chk_autoupdate.isChecked()).lower()
        encfsgui_globals.g_Settings["confirmforceunmountall"] = str(self.chk_confirmforceunmountall.isChecked()).lower()
        encfsgui_globals.g_Settings["doubleclickmount"] = str(self.chk_doubleclickmount.isChecked()).lower()
        if self.chk_debugmode.isChecked():
            encfsgui_globals.debugmode = True
            encfsgui_helper.print_debug("Enable debug mode")
        else:
            encfsgui_helper.print_debug("Disable debug mode")
            encfsgui_globals.debugmode = False
        # and write to file
        config = configparser.RawConfigParser()
        config.add_section('config')
        for settingkey in encfsgui_globals.g_Settings:
            config.set('config', settingkey, encfsgui_globals.g_Settings[settingkey])

        config.add_section('encodings')
        config.set('encodings','filenameencodings', ",".join(encfsgui_globals.g_Encodings))
        
        # save file to disk
        with open(encfsgui_globals.settingsfile, 'w') as configfile:
            config.write(configfile)
        return
