# encfsgui Create a new volume
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

import encfsgui_globals
from encfsgui_globals import *

import encfsgui_helper
from encfsgui_helper import *

class CVolumeWindow(QtWidgets.QDialog):
    def __init__(self):
        super(CVolumeWindow, self).__init__()
        uic.loadUi('encfsgui_volume.ui', self)
        # 0 = create
        # 1 = add
        # 2 = edit
        self.runmode = 0    # create

        self.savebutton = self.findChild(QtWidgets.QPushButton, 'btn_save')
        self.savebutton.clicked.connect(self.SaveButtonClicked)

        self.cancelbutton = self.findChild(QtWidgets.QPushButton, 'btn_cancel')
        self.cancelbutton.clicked.connect(self.CancelButtonClicked)

        self.radio_balanced = self.findChild(QtWidgets.QRadioButton, 'radio_balanced')
        self.radio_performance = self.findChild(QtWidgets.QRadioButton, 'radio_performance')
        self.radio_secure = self.findChild(QtWidgets.QRadioButton, 'radio_secure')
        self.radio_custom = self.findChild(QtWidgets.QRadioButton, 'radio_custom')

        self.radio_balanced.clicked.connect(self.SelectProfileBalanced)
        self.radio_performance.clicked.connect(self.SelectProfilePerformance)
        self.radio_secure.clicked.connect(self.SelectProfileSecure)
        self.radio_custom.clicked.connect(self.SelectProfileCustom)

        self.chk_perblockhmac = self.findChild(QtWidgets.QCheckBox, 'chk_perblockhmac')
        self.chk_perfileuniqueiv = self.findChild(QtWidgets.QCheckBox, 'chk_perfileuniqueiv')
        self.chk_chainediv = self.findChild(QtWidgets.QCheckBox, 'chk_chainediv')
        self.chk_externaliv = self.findChild(QtWidgets.QCheckBox, 'chk_externaliv')

        self.grp_encfsoptions = self.findChild(QtWidgets.QGroupBox, 'grp_encfsoptions')

        # populate combo boxes
        self.ciphercombo = self.findChild(QtWidgets.QComboBox, ('cmb_ciphers'))
        self.ciphercombo.clear()
        self.ciphercombo.addItem("AES")

        self.keysizecombo = self.findChild(QtWidgets.QComboBox, ('cmb_keysize'))
        self.blocksizecombo = self.findChild(QtWidgets.QComboBox, ('cmb_blocksize'))
        self.filenameencodingcombo = self.findChild(QtWidgets.QComboBox, ('cmb_filenameencoding'))

        self.keysizecombo.clear()
        self.keysizecombo.addItem("128")
        self.keysizecombo.addItem("192")
        self.keysizecombo.addItem("256")

        blocksize = 64
        self.blocksizecombo.clear()
        while (blocksize <= 4096):
            self.blocksizecombo.addItem("%d" % blocksize)
            blocksize += 16

        self.filenameencodingcombo.clear()
        self.filenameencodingcombo.addItem("Stream")
        self.filenameencodingcombo.addItem("Block")
        self.filenameencodingcombo.addItem("Block32")
        self.filenameencodingcombo.addItem("Null")

        self.SelectProfileBalanced()
    

    def SelectProfileCustom(self):
        self.ciphercombo.setEnabled(True)
        self.keysizecombo.setEnabled(True)
        self.blocksizecombo.setEnabled(True)
        self.filenameencodingcombo.setEnabled(True)
        self.chk_perblockhmac.setEnabled(True)
        self.chk_perfileuniqueiv.setEnabled(True)
        self.chk_chainediv.setEnabled(True)
        self.chk_externaliv.setEnabled(True)
        return


    def SelectProfileBalanced(self):
        self.ciphercombo.setEnabled(False)
        self.keysizecombo.setEnabled(False)
        self.blocksizecombo.setEnabled(False)
        self.filenameencodingcombo.setEnabled(False)
        self.chk_perblockhmac.setEnabled(False)
        self.chk_perfileuniqueiv.setEnabled(False)
        self.chk_chainediv.setEnabled(False)
        self.chk_externaliv.setEnabled(False)

        self.chk_perfileuniqueiv.setChecked(True)
        self.chk_externaliv.setChecked(False)
        self.chk_chainediv.setChecked(False)
        self.chk_perblockhmac.setChecked(False)

        self.ciphercombo.setCurrentText("AES")
        self.keysizecombo.setCurrentText("192")
        self.blocksizecombo.setCurrentText("2048")
        self.filenameencodingcombo.setCurrentText("Stream")
        return

    def SelectProfilePerformance(self):
        self.ciphercombo.setEnabled(False)
        self.keysizecombo.setEnabled(False)
        self.blocksizecombo.setEnabled(False)
        self.filenameencodingcombo.setEnabled(False)
        self.chk_perblockhmac.setEnabled(False)
        self.chk_perfileuniqueiv.setEnabled(False)
        self.chk_chainediv.setEnabled(False)
        self.chk_externaliv.setEnabled(False)        
        self.ciphercombo.setCurrentText("AES")
        self.keysizecombo.setCurrentText("192")
        self.blocksizecombo.setCurrentText("1024")
        self.filenameencodingcombo.setCurrentText("Null")
        self.chk_perfileuniqueiv.setChecked(False)
        self.chk_externaliv.setChecked(False)
        self.chk_chainediv.setChecked(False)
        self.chk_perblockhmac.setChecked(False)        
        return

    def SelectProfileSecure(self):
        self.ciphercombo.setEnabled(False)
        self.keysizecombo.setEnabled(False)
        self.blocksizecombo.setEnabled(False)
        self.filenameencodingcombo.setEnabled(False)
        self.chk_perblockhmac.setEnabled(False)
        self.chk_perfileuniqueiv.setEnabled(False)
        self.chk_chainediv.setEnabled(False)
        self.chk_externaliv.setEnabled(False)
        self.ciphercombo.setCurrentText("AES")
        self.keysizecombo.setCurrentText("256")
        self.blocksizecombo.setCurrentText("4096")  
        self.filenameencodingcombo.setCurrentText("Block")  
        self.chk_perfileuniqueiv.setChecked(True)
        self.chk_externaliv.setChecked(True)
        self.chk_chainediv.setChecked(True)
        self.chk_perblockhmac.setChecked(True)    
        return

    def SaveButtonClicked(self):
        self.close()
        return


    def CancelButtonClicked(self):
        self.close()
        return

    def setRunMode(self, mode):
        self.runmode = mode

        self.lbl_encfsfolder = self.findChild(QtWidgets.QLabel,'lbl_encfsfolder')

        if mode == 0:
            self.setWindowTitle("Create a new encfs volume")
            self.lbl_encfsfolder.setText("Location of new (empty) encfs folder:")
            self.savebutton.setText("Create")
            self.grp_encfsoptions.setEnabled(True)

        if mode == 1:
            self.setWindowTitle("Open/Add an existing encfs volume")
            self.lbl_encfsfolder.setText("Location of existing encfs folder:")
            self.savebutton.setText("Add")
            self.grp_encfsoptions.setEnabled(False)
        if mode == 2:
            self.setWindowTitle("Edit an encfs volume")
            self.lbl_encfsfolder.setText("Location of existing encfs folder:")
            self.savebutton.setText("Save")
            self.grp_encfsoptions.setEnabled(False)
        return

    def getRunMode(self):
        encfsgui_helper.print_debug("mode: %d" % self.runmode)
        return