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

import cnewmasterkey
from cnewmasterkey import CNewMasterKeyWindow


class CSettingsWindow(QtWidgets.QDialog):
    def __init__(self):
        encfsgui_helper.print_debug("Start CSettingsWindow %s" % inspect.stack()[0][3])
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
        self.chk_encrypt = self.findChild(QtWidgets.QCheckBox, 'chk_encrypt')
        self.chk_clearkeywhenhidden = self.findChild(QtWidgets.QCheckBox, 'chk_clearkeywhenhidden')

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
        
        if (encfsgui_globals.g_Settings["encrypt"].lower() == "true"):
            self.chk_encrypt.setChecked(True)

        if (encfsgui_globals.g_Settings["clearkeywhenhidden"].lower() == "true"):
            self.chk_clearkeywhenhidden.setChecked(True)

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
        encfsgui_globals.g_Settings["clearkeywhenhidden"] = str(self.chk_clearkeywhenhidden.isChecked()).lower()
        if self.chk_debugmode.isChecked():
            encfsgui_globals.debugmode = True
            encfsgui_helper.print_debug("Enable debug mode")
        else:
            encfsgui_helper.print_debug("Disable debug mode")
            encfsgui_globals.debugmode = False

        # encryption?
        if (self.chk_encrypt.isChecked() and str(encfsgui_globals.g_Settings["encrypt"]).lower() == "false"):
            # ask for master password
            encryptionpassword = ""
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("Enable encryption/master password?")
            msgBox.setText("You are about to enable encryption of the encfsgui.volumes file.\n\nYour 'masterkey' password will NOT be stored and cannot be recovered.\nIf you forget the master password, you will not be able to recover/decrypt the contents of the encfsgui.volumes file.\n\nAre you sure?")
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes)
            msgBox.addButton(QtWidgets.QMessageBox.No)
            msgBox.show()
            if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
                # ask for the password
                masterpwwindow = CNewMasterKeyWindow()
                masterpwwindow.setWindowTitle("Please enter master password")
                masterpwwindow.show()
                masterpwwindow.exec_()
                encryptionpassword = masterpwwindow.getPassword()
            # no password = no encryption
            if encryptionpassword != "":
                encfsgui_globals.masterkey = encryptionpassword
                encfsgui_globals.g_Settings["encrypt"] = "true"
                # make sure to encrypt the volumes file - simply request volumes file to be written to disk
                # encryption is handled by the saveVolumes method
                encfsgui_globals.appconfig.saveVolumes()
                QtWidgets.QMessageBox.information(None,"Encryption enabled","Encryption enabled.")
            else:
                encfsgui_globals.g_Settings["encrypt"] = "false"

        removeencryption = False
        if (not self.chk_encrypt.isChecked()) and str(encfsgui_globals.g_Settings["encrypt"]).lower() == "true":
            # ask to confirm to remove encryption?
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("Disable encryption/master password?")
            msgBox.setText("You are about to disable encryption of the encfsgui.volumes file.\n\nThis will decrypt the contents of the file and remove the need to use a master password.\n\nAre you sure?")
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setStandardButtons(QtWidgets.QMessageBox.No)
            msgBox.addButton(QtWidgets.QMessageBox.Yes)
            msgBox.show()
            if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
                removeencryption = True
            if removeencryption:
                encfsgui_globals.g_Settings["encrypt"] = "false"
                encfsgui_globals.masterkey = ""
            else:
                # leave encryption active
                encfsgui_globals.g_Settings["encrypt"] = "true"

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

        # save volumes (to make sure it gets encrypted or decrypted)
        encfsgui_globals.appconfig.saveVolumes()
        
        if removeencryption:
            QtWidgets.QMessageBox.information(None,"Encryption disabled","Encryption disabled.")
        return
