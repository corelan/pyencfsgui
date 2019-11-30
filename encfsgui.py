import os
import sys
import time
import datetime
import string
import subprocess
import configparser

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import *

# forms
import csettings 
from csettings import CSettingsWindow

import cvolume
from cvolume import CVolumeWindow

import cmountpassword
from cmountpassword import CMountPassword

# globals
import encfsgui_globals
from encfsgui_globals import *
from encfsgui_globals import CEncryptedVolume

# config
import cconfig
from cconfig import CConfig
from cconfig import *

# code
import encfsgui_helper
from encfsgui_helper import *

app = QApplication([])

encfsgui_globals.g_Volumes = { }
encfsgui_globals.g_Settings = { }
encfsgui_globals.g_CurrentlySelected = ""



#################
### Main form ###
#################
class CMainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(CMainWindow, self).__init__()
        uic.loadUi('encfsgui_main.ui', self)

        # assign methods to buttons
        self.quitbutton =  self.findChild(QtWidgets.QToolButton, 'btn_Quit')
        self.quitbutton.clicked.connect(self.QuitButtonClicked)

        self.createvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_createVolume')
        self.createvolumebutton.clicked.connect(self.CreateVolumeButtonClicked)

        self.addvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_openVolume')
        self.addvolumebutton.clicked.connect(self.AddVolumeButtonClicked)

        self.editvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_editVolume')
        self.editvolumebutton.clicked.connect(self.EditVolumeButtonClicked)

        self.settingsbutton = self.findChild(QtWidgets.QToolButton, 'btn_Settings')
        self.settingsbutton.clicked.connect(self.SetttingsButtonClicked)

        self.volumetable = self.findChild(QtWidgets.QTableWidget, 'tbl_Volumes')
        self.volumetable.itemSelectionChanged.connect(self.TableEntrySelected)

        self.browsevolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_browseVolume')
        self.browsevolumebutton.clicked.connect(self.BrowseVolumeClicked)
        
        self.removevolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_removeVolume')
        
        self.infovolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_infoVolume')
        
        self.mountvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_mountVolume')
        self.mountvolumebutton.clicked.connect(self.MountVolumeClicked)

        self.unmountvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_unmountVolume')
        self.unmountvolumebutton.clicked.connect(self.UnmountVolumeClicked)

        # enable/disablebuttons as needed
        self.RefreshVolumes()
        self.EnableDisableButtons()
        self.SetInfoLabel()


    #methods linked to buttons
    def QuitButtonClicked(self):
        self.AutoUnMount()
        sys.exit(0)


    def CreateVolumeButtonClicked(self):
        createvolumewindow = CVolumeWindow()
        createvolumewindow.show()
        createvolumewindow.setRunMode(0)    # create
        createvolumewindow.exec_()
        self.RefreshVolumes()
        return


    def AddVolumeButtonClicked(self):
        addvolumewindow = CVolumeWindow()
        addvolumewindow.show()
        addvolumewindow.setRunMode(1)    # add
        addvolumewindow.exec_()
        self.RefreshVolumes()
        return       

    def EditVolumeButtonClicked(self):
        if encfsgui_globals.g_CurrentlySelected != "":
            editvolumewindow = CVolumeWindow()
            editvolumewindow.show()
            editvolumewindow.setRunMode(2)    # edit
            editvolumewindow.origvolumename = encfsgui_globals.g_CurrentlySelected
            editvolumewindow.PopulateFields(encfsgui_globals.g_CurrentlySelected)
            editvolumewindow.exec_()
            encfsgui_globals.appconfig.getVolumes()
            self.RefreshVolumes()
        return 

    def SetttingsButtonClicked(self):
        settingswindow = CSettingsWindow()
        settingswindow.loadSettings()
        settingswindow.show()
        settingswindow.exec_()
        # when dialog closes, refresh settings (in case user made a change)
        self.RefreshSettings()
        self.RefreshVolumes()
        self.SetInfoLabel()
        return

    def MountVolumeClicked(self):
        # do we need to ask for password?
        if encfsgui_globals.g_CurrentlySelected != "":
            if encfsgui_globals.g_CurrentlySelected in encfsgui_globals.g_Volumes:
                thispassword = self.getPasswordForVolume(encfsgui_globals.g_CurrentlySelected)
                self.MountVolume(encfsgui_globals.g_CurrentlySelected, thispassword)
        return

    def getPasswordForVolume(self, volumename):
        thispassword = ""
        EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
        if str(EncVolumeObj.passwordsaved) == "0":
            frmpassword = CMountPassword()
            frmpassword.setEncPath(EncVolumeObj.enc_path)
            frmpassword.setMountPath(EncVolumeObj.mount_path)
            frmpassword.show()
            frmpassword.exec_()
            # did we get a password?
            thispassword = frmpassword.getPassword()
        else:
            thispassword = str(encfsgui_helper.getKeyChainPassword(volumename))
        return thispassword

    def UnmountVolumeClicked(self):
        if encfsgui_globals.g_CurrentlySelected != "":
            volumename = encfsgui_globals.g_CurrentlySelected
            self.UnmountVolume(volumename) 
        return


    def UnmountVolume(self, volumename):
        # do we need to ask for confirmation?
        askforconfirmation = True
        if "noconfirmationunmount" in encfsgui_globals.g_Settings:
            if encfsgui_globals.g_Settings["noconfirmationunmount"].lower() == "true":
                askforconfirmation = False
        if volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            dounmount = True
            if askforconfirmation:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("Are you sure?")
                msgBox.setText("Unmount volume '%s' \n '%s'?\n\n(Make sure all files on this volume are closed first!)" % (volumename, EncVolumeObj.mount_path))
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes)
                msgBox.addButton(QtWidgets.QMessageBox.No)
                msgBox.show()
                if (msgBox.exec_() == QtWidgets.QMessageBox.No):
                    dounmount = False

            if dounmount:
                cmd = "%s '%s'" % (encfsgui_globals.g_Settings["umountpath"], EncVolumeObj.mount_path)
                encfsgui_helper.execOSCmd(cmd)
                # did unmount work?
                self.RefreshVolumes()
                EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
                if EncVolumeObj.ismounted:
                    QtWidgets.QMessageBox.critical(None,"Error unmounting volume","Unable to unmount volume '%s'\nMake sure all files are closed and try again." % volumename)
        return


    def BrowseVolumeClicked(self):
        if encfsgui_globals.g_CurrentlySelected != "":
            if encfsgui_globals.g_CurrentlySelected in encfsgui_globals.g_Volumes:
                EncVolumeObj = encfsgui_globals.g_Volumes[encfsgui_globals.g_CurrentlySelected]
                encfsgui_helper.openFolder(EncVolumeObj.mount_path)
        return

    def MountVolume(self, volumename, password):
        if volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            extra_osxfuse_opts = ""
            if (password != ""):
                mountcmd = "%s '%s' '%s' %s" % (encfsgui_globals.g_Settings["encfspath"], EncVolumeObj.enc_path, EncVolumeObj.mount_path, EncVolumeObj.encfsmountoptions)
                if (EncVolumeObj.allowother):
                    extra_osxfuse_opts += "-o allow_other "
                if (EncVolumeObj.mountaslocal):
                    extra_osxfuse_opts += "-o local "
            # first, create mount point if necessary
            createfoldercmd = "mkdir -p '%s'" % EncVolumeObj.mount_path
            encfsgui_helper.execOSCmd(createfoldercmd)

            encfsbin = encfsgui_globals.g_Settings["encfspath"]
            encvol = EncVolumeObj.enc_path
            mountvol = EncVolumeObj.mount_path
            encfsmountoptions = ""
            if not EncVolumeObj.encfsmountoptions == "":
                encfsmountoptions = "'%s'" % EncVolumeObj.encfsmountoptions

            # do the actual mount
            mountcmd = "sh -c \"echo '%s' | %s -v -S %s %s -o volname='%s' '%s' '%s' \"" % (str(password), encfsbin, extra_osxfuse_opts, encfsmountoptions, volumename, encvol, mountvol)
            #encfsgui_helper.print_debug("MOUNT: %s" % mountcmd)
            encfsgui_helper.execOSCmd(mountcmd)
            self.RefreshVolumes()
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            if not EncVolumeObj.ismounted:
                QtWidgets.QMessageBox.critical(None,"Error mounting volume","Unable to mount volume '%s'\n" % volumename)
        return


    def TableEntrySelected(self):
        # update the currently selected volume
        #encfsgui_helper.print_debug("Table clicked")
        encfsgui_globals.g_CurrentlySelected = ""
        selectedindex = 0
        for currentQTableWidgetItem in self.volumetable.selectedItems():
            if selectedindex == 1:
                encfsgui_globals.g_CurrentlySelected = currentQTableWidgetItem.text()
            selectedindex += 1
        #encfsgui_helper.print_debug("Currently selected item: %s" % encfsgui_globals.g_CurrentlySelected)
        # enable/disable buttons accordingly
        self.EnableDisableButtons()
        return


    def RefreshVolumes(self):
        # get volumes from config file
        encfsgui_globals.appconfig.getVolumes()
        # show volumes in the table
        self.volumetable.clearContents()
        self.volumetable.setColumnCount(5)
        self.volumetable.setRowCount(len(encfsgui_globals.g_Volumes))

        columnheaders = ['Mounted?', 'Volume Name', 'EncFS path', 'Mount at', 'Automount?']
        self.volumetable.setHorizontalHeaderLabels(columnheaders)

        self.volumetable.setColumnWidth(0,70)
        self.volumetable.setColumnWidth(1,120)
        self.volumetable.setColumnWidth(2,360)
        self.volumetable.setColumnWidth(3,320)
        self.volumetable.setColumnWidth(4,90)

        volumeindex = 0
        for volumekey in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumekey]
            mountedtext = "NO"
            if EncVolumeObj.ismounted:
                mountedtext = "YES"
            
            automounttext = "NO"
            if str(EncVolumeObj.automount) == "1":
                automounttext = "YES"

            boldfont = QFont()
            boldfont.setBold(True)

            regularfont = QFont()
            regularfont.setBold(False)
            mountstate = QTableWidgetItem(mountedtext)
            
            if EncVolumeObj.ismounted:    
                mountstate.setFont(boldfont)
                mountstate.setForeground(QColor(255,0,0))
            else:
                mountstate.setFont(regularfont)
                mountstate.setForeground(QColor(0,255,0))

            self.volumetable.setItem(volumeindex,0, mountstate)
            self.volumetable.setItem(volumeindex,1, QTableWidgetItem(volumekey))
            self.volumetable.setItem(volumeindex,2, QTableWidgetItem(EncVolumeObj.enc_path))
            self.volumetable.setItem(volumeindex,3, QTableWidgetItem(EncVolumeObj.mount_path))
            self.volumetable.setItem(volumeindex,4, QTableWidgetItem(automounttext))

            self.volumetable.setRowHeight(volumeindex,12)

            volumeindex += 1
            
        self.SetInfoLabel()
        return

    def AutoMount(self):
        # process automounts
        for volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            if str(EncVolumeObj.automount) == "1":
                if not EncVolumeObj.ismounted:
                    thispassword = self.getPasswordForVolume(volumename)
                    self.MountVolume(volumename, thispassword)
        return

    def AutoUnMount(self):
        if str(encfsgui_globals.g_Settings["autounmount"]) == "true":
            # unmount the volumes that don't have preventautounmount set
            for volumename in encfsgui_globals.g_Volumes:
                EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
                if str(EncVolumeObj.preventautounmount) == "0":
                    self.UnmountVolume(volumename)
        return

    def RefreshSettings(self):
        encfsgui_globals.appconfig.getSettings()
        self.SetInfoLabel()
        return


    def SetInfoLabel(self):
        self.infolabel = self.findChild(QtWidgets.QLabel, 'lbl_InfoLabel')
        encfsinfo = "encfs v%s" % (getEncFSVersion(encfsgui_globals.g_Settings))
        self.infolabel.setText("%s  |  Nr of volumes: %d  |  %s" % (encfsinfo, len(encfsgui_globals.g_Volumes), encfsgui_globals.volumesfile ))
        return

    def EnableDisableButtons(self):
        # did we select an entry in the table?
        selectedenable = False
        if encfsgui_globals.g_CurrentlySelected != "":
            selectedenable = True
            mounted = False
            if encfsgui_globals.g_CurrentlySelected in encfsgui_globals.g_Volumes:
                mounted = encfsgui_globals.g_Volumes[encfsgui_globals.g_CurrentlySelected].ismounted
            if mounted:
                self.mountvolumebutton.setEnabled(False)
                self.unmountvolumebutton.setEnabled(True)
                self.browsevolumebutton.setEnabled(True)
                self.editvolumebutton.setEnabled(False)
            else:
                self.mountvolumebutton.setEnabled(True)
                self.unmountvolumebutton.setEnabled(False)
                self.browsevolumebutton.setEnabled(False)
                self.editvolumebutton.setEnabled(True)
        else:
            self.mountvolumebutton.setEnabled(False)
            self.unmountvolumebutton.setEnabled(False)
            self.browsevolumebutton.setEnabled(False)

        
        self.infovolumebutton.setEnabled(selectedenable)
        self.removevolumebutton.setEnabled(selectedenable)

        return




if __name__ == "__main__":

    encfsgui_globals.settingsfile = 'encfsgui.settings'

    encfsgui_globals.debugmode = True
    encfsgui_globals.appconfig = CConfig()

    encfsgui_globals.volumesfile = encfsgui_globals.g_Settings["workingfolder"] + "/" + 'encfsgui.volumes'
    
    mainwindow = CMainWindow()

    mainwindow.RefreshSettings()
    mainwindow.RefreshVolumes()
    mainwindow.AutoMount()

    mainwindow.show()
    mainwindow.exec_()
    #app.exec_()