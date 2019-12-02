import os
import sys
import time
import datetime
import string
import subprocess
import configparser
import inspect

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu, QAction, QStyle
from PyQt5 import QtCore

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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        super(CMainWindow, self).__init__()
        uic.loadUi('encfsgui_main.ui', self)

        # disable/remove buttons
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        # assign methods to buttons
        self.quitbutton =  self.findChild(QtWidgets.QToolButton, 'btn_Quit')
        self.quitbutton.clicked.connect(self.QuitButtonClicked)

        self.hidebutton = self.findChild(QtWidgets.QToolButton, 'btn_Hide')
        self.hidebutton.clicked.connect(self.HideButtonClicked)

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
        self.removevolumebutton.clicked.connect(self.RemoveVolumeClicked)

        self.infovolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_infoVolume')
        self.infovolumebutton.clicked.connect(self.ShowVolumeInfoClicked)
        
        self.mountvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_mountVolume')
        self.mountvolumebutton.clicked.connect(self.MountVolumeClicked)

        self.unmountvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_unmountVolume')
        self.unmountvolumebutton.clicked.connect(self.UnmountVolumeClicked)

        self.unmountallbutton = self.findChild(QtWidgets.QToolButton, 'btn_unmountAll')
        self.unmountallbutton.clicked.connect(self.UnmountAllClicked)

        # enable/disablebuttons as needed
        self.RefreshVolumes()
        self.EnableDisableButtons()
        self.SetInfoLabel()

        # system tray menu
        self.tray_icon = QSystemTrayIcon(self)
        #self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_DriveHDIcon))
        self.tray_icon.setIcon(QIcon('./bitmaps/encfsgui.png'))
        self.tray_menu = QMenu()

        self.volume_menu = QMenu()

        self.CreateTrayMenu()


    #methods linked to buttons
    def QuitButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        doexit = False
        autunmount = False
        if "autounmount" in encfsgui_globals.g_Settings:
            if str(encfsgui_globals.g_Settings["autounmount"]) == "true":
                autunmount = True
        if "noconfirmationexit" in encfsgui_globals.g_Settings:
            if str(encfsgui_globals.g_Settings["noconfirmationexit"]) == "false":
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Question)
                msgBox.setWindowTitle("Please confirm?")
                if autunmount:
                    msgBox.setText("Are you sure you would like to exit?\n\nPlease note that some volumes may be unmounted automatically when you exit the application, so please make sure all files are closed.")
                else:
                    msgBox.setText("Are you sure you would like to exit?")
                msgBox.setStandardButtons(QtWidgets.QMessageBox.No)
                msgBox.addButton(QtWidgets.QMessageBox.Yes)
                msgBox.show()
                if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
                    doexit = True
            else:
                doexit = True

        if doexit:
            self.AutoUnMount()
            sys.exit(0)
        return

    def ShowButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.show_action.setEnabled(False)
        self.hide_action.setEnabled(True)
        self.show()
        self.setFocus()
        return

    def HideButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.show_action.setEnabled(True)
        self.hide_action.setEnabled(False)
        self.hide()
        return

    def AboutClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        abouttext = "pyencfsgui is a python3/PyQT5 based GUI wrapper around encfs.\n\n"
        abouttext += "This version has been tested with encfs 1.9.x on OSX Catalina\n"
        abouttext += "It may work on older systems and older versions of encfs, but you'll have to try and see for yourself\n\n"
        abouttext += "pyencfsgui was written in 2019 by Peter 'corelanc0d3r' Van Eeckhoutte\n"
        abouttext += "Corelan Consulting bvba - www.corelan-consulting.com | www.corelan-training.com\n\n"
        abouttext += "Project repository: https://github.com/corelan/pyencfsgui\n\n"
        abouttext +=  "You are running encfs version %s" % getEncFSVersion()

        msgBox = QMessageBox()
        msgBox.setWindowTitle("About pyencfsgui")
        msgBox.setText(abouttext)
        msgBox.show()
        msgBox.exec_()
        return

    def CreateTrayMenu(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.show_action = QAction("Show", self)
        self.hide_action = QAction("Hide", self)
        self.settings_action = QAction("Settings", self)
        self.about_action = QAction("About", self)
        self.quit_action = QAction("Quit", self)
        
        
        self.show_action.triggered.connect(self.ShowButtonClicked)
        self.hide_action.triggered.connect(self.HideButtonClicked)
        self.settings_action.triggered.connect(self.SetttingsButtonClicked)
        self.about_action.triggered.connect(self.AboutClicked)
        self.quit_action.triggered.connect(self.QuitButtonClicked)

        self.PopulateVolumeMenu()

        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.hide_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.settings_action)
        self.tray_menu.addSeparator()
        self.volume_menu.setTitle("Volumes")
        self.tray_menu.addMenu(self.volume_menu)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.about_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)

        if self.isVisible():
            self.show_action.setEnabled(False)
            self.hide_action.setEnabled(True)
        else:
            self.show_action.setEnabled(True)
            self.hide_action.setEnabled(False)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        return


    def PopulateVolumeMenu(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.volume_menu.clear()

        for volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]

            self.volume_mount = QAction("Mount %s" % volumename, self)
            self.volume_mount.triggered.connect(self.MenuMountVolume)
            self.volume_menu.addAction(self.volume_mount)
            
            self.volume_unmount = QAction("Unmount %s" % volumename, self)
            self.volume_unmount.triggered.connect(self.MenuUnmountVolume)
            self.volume_menu.addAction(self.volume_unmount)

            self.volume_menu.addSeparator()

            if EncVolumeObj.ismounted:
                self.volume_mount.setEnabled(False)
                self.volume_unmount.setEnabled(True)
            else:
                self.volume_mount.setEnabled(True)
                self.volume_unmount.setEnabled(False)

        return

    def MenuMountVolume(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        actionname = self.sender().text()
        volumename = self.getVolumeNameFromAction(actionname)
        thispassword = self.getPasswordForVolume(volumename)
        self.MountVolume(volumename, thispassword)
        self.PopulateVolumeMenu()
        return

    def MenuUnmountVolume(self, action):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        actionname = self.sender().text()
        volumename = self.getVolumeNameFromAction(actionname)
        self.UnmountVolume(volumename)
        self.PopulateVolumeMenu()
        return


    def getVolumeNameFromAction(self, actionname):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        volumename = ""
        startindex = 0
        if (actionname.startswith("Mount")):
            volumename = actionname.lstrip("Mount ")
        elif (actionname.startswith("Unmount")):
            volumename = actionname.lstrip("Unmount ")
        return volumename

    def CreateVolumeButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        createvolumewindow = CVolumeWindow()
        createvolumewindow.show()
        createvolumewindow.setRunMode(0)    # create
        createvolumewindow.exec_()
        self.RefreshVolumes()
        return


    def AddVolumeButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        addvolumewindow = CVolumeWindow()
        addvolumewindow.show()
        addvolumewindow.setRunMode(1)    # add
        addvolumewindow.exec_()
        self.RefreshVolumes()
        return       

    def EditVolumeButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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

    def RemoveVolumeClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        volumename = encfsgui_globals.g_CurrentlySelected
        if volumename != "":
            if volumename in encfsgui_globals.g_Volumes: 
                EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
                msgBox = QtWidgets.QMessageBox()
                msgBox.setIcon(QtWidgets.QMessageBox.Question)
                msgBox.setWindowTitle("Are you sure?")
                msgBox.setText("Are you sure you would like to remove volume '%s' from this app?\n (mounted at '%s')?\n\nNote: this will not unmount the volume, and will not remove the actual encrypted folder.\nI will only remove the volume from the application." % (volumename, EncVolumeObj.mount_path))
                msgBox.setStandardButtons(QtWidgets.QMessageBox.No)
                msgBox.addButton(QtWidgets.QMessageBox.Yes)
                msgBox.show()
                if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
                    encfsgui_globals.appconfig.delVolume(volumename)
                    encfsgui_globals.appconfig.getVolumes()
                    self.RefreshVolumes()
                    self.SetInfoLabel()
        return

    def ShowVolumeInfoClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        volumename = encfsgui_globals.g_CurrentlySelected
        if volumename != "":
            if volumename in encfsgui_globals.g_Volumes:
                EncVolumeObj =  encfsgui_globals.g_Volumes[volumename]
                cmd = "%sctl -i '%s'" % (encfsgui_globals.g_Settings["encfspath"], EncVolumeObj.enc_path)
                cmdoutput = encfsgui_helper.execOSCmd(cmd)
                infotext = "EncFS volume info for '%s'\n" % volumename
                infotext += "Encrypted folder '%s'\n\n" % EncVolumeObj.enc_path
                for l in cmdoutput:
                    infotext = infotext + l + "\n"
                msgBox = QtWidgets.QMessageBox()
                msgBox.setIcon(QtWidgets.QMessageBox.Information)
                msgBox.setWindowTitle("EncFS Volume info")
                msgBox.setText(infotext)
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msgBox.show()
                msgBox.exec_()
        return

    def SetttingsButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # do we need to ask for password?
        if encfsgui_globals.g_CurrentlySelected != "":
            if encfsgui_globals.g_CurrentlySelected in encfsgui_globals.g_Volumes:
                thispassword = self.getPasswordForVolume(encfsgui_globals.g_CurrentlySelected)
                self.MountVolume(encfsgui_globals.g_CurrentlySelected, thispassword)
        return

    def getPasswordForVolume(self, volumename):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        thispassword = ""
        EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
        if str(EncVolumeObj.passwordsaved) == "0":
            frmpassword = CMountPassword()
            frmpassword.setEncPath(EncVolumeObj.enc_path)
            frmpassword.setMountPath(EncVolumeObj.mount_path)
            frmpassword.show()
            frmpassword.setFocus()
            frmpassword.exec_()
            # did we get a password?
            thispassword = frmpassword.getPassword()
        else:
            thispassword = str(encfsgui_helper.getKeyChainPassword(volumename))
        return thispassword

    def UnmountVolumeClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        if encfsgui_globals.g_CurrentlySelected != "":
            volumename = encfsgui_globals.g_CurrentlySelected
            self.UnmountVolume(volumename) 
        return

    def UnmountAllClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        for volumename in encfsgui_globals.g_Volumes:
            self.UnmountVolume(volumename, True)
        self.RefreshVolumes()
        return

    def UnmountVolume(self, volumename, forced=False):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # do we need to ask for confirmation?
        askforconfirmation = True
        if "noconfirmationunmount" in encfsgui_globals.g_Settings:
            if encfsgui_globals.g_Settings["noconfirmationunmount"].lower() == "true":
                askforconfirmation = False
        if volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            dounmount = True
            if askforconfirmation and not forced:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setIcon(QMessageBox.Question)
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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        if encfsgui_globals.g_CurrentlySelected != "":
            if encfsgui_globals.g_CurrentlySelected in encfsgui_globals.g_Volumes:
                EncVolumeObj = encfsgui_globals.g_Volumes[encfsgui_globals.g_CurrentlySelected]
                encfsgui_helper.openFolder(EncVolumeObj.mount_path)
        return

    def MountVolume(self, volumename, password):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # update the currently selected volume
        encfsgui_globals.g_CurrentlySelected = ""
        selectedindex = 0
        for currentQTableWidgetItem in self.volumetable.selectedItems():
            if selectedindex == 1:
                encfsgui_globals.g_CurrentlySelected = currentQTableWidgetItem.text()
                encfsgui_helper.print_debug("Selected entry %s" % encfsgui_globals.g_CurrentlySelected)
            selectedindex += 1
        # enable/disable buttons accordingly
        self.EnableDisableButtons()
        return


    def RefreshVolumes(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # process automounts
        for volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            if str(EncVolumeObj.automount) == "1":
                if not EncVolumeObj.ismounted:
                    thispassword = self.getPasswordForVolume(volumename)
                    self.MountVolume(volumename, thispassword)
        return

    def AutoUnMount(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        if str(encfsgui_globals.g_Settings["autounmount"]) == "true":
            # unmount the volumes that don't have preventautounmount set
            for volumename in encfsgui_globals.g_Volumes:
                EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
                if str(EncVolumeObj.preventautounmount) == "0":
                    self.UnmountVolume(volumename)
        return

    def RefreshSettings(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        encfsgui_globals.appconfig.getSettings()
        self.SetInfoLabel()
        return

    def SetInfoLabel(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.infolabel = self.findChild(QtWidgets.QLabel, 'lbl_InfoLabel')
        encfsinfo = "encfs v%s" % (getEncFSVersion())
        self.infolabel.setText("%s  |  Nr of volumes: %d  |  %s" % (encfsinfo, len(encfsgui_globals.g_Volumes), encfsgui_globals.volumesfile ))
        return

    def EnableDisableButtons(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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
            self.editvolumebutton.setEnabled(False)

        
        self.infovolumebutton.setEnabled(selectedenable)
        self.removevolumebutton.setEnabled(selectedenable)

        return


if __name__ == "__main__":

    encfsgui_globals.settingsfile = 'encfsgui.settings'

    encfsgui_globals.appconfig = CConfig()
    encfsgui_globals.volumesfile = encfsgui_globals.g_Settings["workingfolder"] + "/" + 'encfsgui.volumes'

    if str(encfsgui_globals.g_Settings["debugmode"]).lower() == "true":
        encfsgui_globals.debugmode = True
    else:
        encfsgui_globals.debugmode = False


    mainwindow = CMainWindow()
    mainwindow.RefreshSettings()

    mainwindow.RefreshVolumes()
    mainwindow.AutoMount()

    if str(encfsgui_globals.g_Settings["starthidden"]).lower() == "false":
        mainwindow.show()

    app.setQuitOnLastWindowClosed(False)
    app.exec_()