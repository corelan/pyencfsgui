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

import encfsgui_globals
from encfsgui_globals import *

import encfsgui_helper
from encfsgui_helper import *

import cconfig
from cconfig import CConfig

class CSettingsWindow(QtWidgets.QDialog):
    def __init__(self):
        super(CSettingsWindow, self).__init__()
        uic.loadUi('encfsgui_settings.ui', self)

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
        self.txt_enfcsbinary = self.findChild(QtWidgets.QLineEdit, 'txt_encfsbinary')
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select 'encfs' binary", self.txt_enfcsbinary.displayText(),"All Files (*)", options=options)
        if fileName:
            
            self.txt_encfsbinary.setText("%s" % fileName)
        return

    def SelectMountButtonClicked(self):
        self.txt_mountbinary = self.findChild(QtWidgets.QLineEdit, 'txt_mountbinary')
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select 'mount' binary", self.txt_mountbinary.displayText(),"All Files (*)", options=options)
        if fileName:
            self.txt_mountbinary.setText("%s" % fileName)
        return

    def SelectUmountButtonClicked(self):
        self.txt_umountbinary = self.findChild(QtWidgets.QLineEdit, 'txt_umountbinary')
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select 'umount' binary", self.txt_umountbinary.displayText(),"All Files (*)", options=options)
        if fileName:
            
            self.txt_umountbinary.setText("%s" % fileName)
        return

    def SelectWorkingFolderClicked(self):
        self.txt_workingfolder = self.findChild(QtWidgets.QLineEdit, 'txt_workingfolder')
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFolder(self,"Select working folder", self.txt_workingfolder.displayText(),"All Folders (*)", options=options)
        if fileName:
            self.txt_workingfolder.setText("%s" % fileName)
        return

    def OKButtonClicked(self):
        self.saveSettings()
        self.close()
        return

    def CancelButtonClicked(self):
        self.close()
        return

    def loadSettings(self):
        # populate fields
        self.txt_enfcsbinary = self.findChild(QtWidgets.QLineEdit, 'txt_encfsbinary')
        self.txt_enfcsbinary.setText("%s" % encfsgui_globals.g_Settings["encfspath"])
        self.txt_mountbinary = self.findChild(QtWidgets.QLineEdit, 'txt_mountbinary')
        self.txt_mountbinary.setText("%s" % encfsgui_globals.g_Settings["mountpath"])
        self.txt_umountbinary = self.findChild(QtWidgets.QLineEdit, 'txt_umountbinary')
        self.txt_umountbinary.setText("%s" % encfsgui_globals.g_Settings["umountpath"])

        self.chk_autounmount = self.findChild(QtWidgets.QCheckBox, 'chk_autounmount')
        self.chk_noconfirmationunmount = self.findChild(QtWidgets.QCheckBox, 'chk_noconfirmationunmount')
        self.chk_noconfirmationexit = self.findChild(QtWidgets.QCheckBox, 'chk_noconfirmationexit')

        if (encfsgui_globals.g_Settings["autounmount"].lower() == "true"):
            self.chk_autounmount.setChecked(True)

        if (encfsgui_globals.g_Settings["noconfirmationunmount"].lower() == "true"):
            self.chk_noconfirmationunmount.setChecked(True)
        else:
            self.chk_noconfirmationunmount.setChecked(False)

        if (encfsgui_globals.g_Settings["noconfirmationexit"].lower() == "true"):
            self.chk_noconfirmationexit.setChecked(True)
        return

    def saveSettings(self):
        # update global settings
        encfsgui_globals.g_Settings["encfspath"] = self.txt_enfcsbinary.displayText().strip()
        encfsgui_globals.g_Settings["mountpath"] = self.txt_mountbinary.displayText().strip()
        encfsgui_globals.g_Settings["umountpath"] = self.txt_umountbinary.displayText().strip()
        encfsgui_globals.g_Settings["autounmount"] = str(self.chk_autounmount.isChecked()).lower()
        encfsgui_globals.g_Settings["noconfirmationunmount"] = str(self.chk_noconfirmationunmount.isChecked()).lower()
        encfsgui_globals.g_Settings["noconfirmationexit"] = str(self.chk_noconfirmationexit.isChecked()).lower()
        # and write to file
        config = configparser.RawConfigParser()
        config.add_section('config')
        for settingkey in encfsgui_globals.g_Settings:
            config.set('config', settingkey, encfsgui_globals.g_Settings[settingkey])

        # save file to disk
        with open(encfsgui_globals.settingsfile, 'w') as configfile:
            config.write(configfile)
        return
