#!/usr/local/bin/python3
import os
import sys
if sys.version_info <(3,0,0):
    sys.stderr.write("\n  ** You need python v3 or later to run this script **\n\n")
    exit(1)
import time
import datetime
import string
import subprocess
import configparser
import inspect
import traceback

try:
    import PyQt5
    from Crypto import Random
except:
    print("*** Oops, some dependencies may be missing: ***")
    print("\t- PyQt5")
    print("\t- pycrypto")
    print("")
    print("You can install the missing depencies using the following commands:")
    print("\tpython3 -m pip install PyQt5 --user")
    print("\tpython3 -m pip install pycrypto --user")
    print("\nNote: installing pycrypto will require macOS Developer Commandline tools to be installed first.  ('xcode-select --install')")
    print("")
    exit(1)

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
from cmountpassword import CMountPasswordWindow

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

encfsgui_globals.app = QApplication([])

# init globals

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
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)
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

        self.refreshbutton = self.findChild(QtWidgets.QToolButton, 'btn_refreshVolumes')
        self.refreshbutton.clicked.connect(self.RefreshVolumesClicked)
        
        self.mountvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_mountVolume')
        self.mountvolumebutton.clicked.connect(self.MountVolumeClicked)

        self.unmountvolumebutton = self.findChild(QtWidgets.QToolButton, 'btn_unmountVolume')
        self.unmountvolumebutton.clicked.connect(self.UnmountVolumeClicked)

        self.unmountallbutton = self.findChild(QtWidgets.QToolButton, 'btn_unmountAll')
        self.unmountallbutton.clicked.connect(self.UnmountAllClicked)

        self.lbl_updatestate = self.findChild(QtWidgets.QLabel, 'lbl_updatestate')
        self.lbl_updatestate.setText("")

        self.lbl_infolabel = self.findChild(QtWidgets.QLabel, 'lbl_InfoLabel')
        self.lbl_infolabel.setText("")


    def initMainWindow(self):
        # only call this after checking for update
        # enable/disablebuttons as needed
        self.RefreshSettings()
        self.RefreshVolumes()
        self.EnableDisableButtons()
        
        # system tray menu
        self.tray_icon = QSystemTrayIcon(self)
        #self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_DriveHDIcon))
        #self.tray_icon.setIcon(QIcon('./bitmaps/encfsgui.png'))
        icondir = encfsgui_helper.getCurDir()
        iconfolder = os.path.join(icondir,'bitmaps' )
        iconpath = os.path.join(iconfolder, 'encfsgui.ico')
        wiconpath = os.path.join(iconfolder, 'encfsgui.png')
        self.tray_icon.setIcon(QIcon(iconpath))
        self.tray_icon.setVisible(True)
        self.tray_menu = QMenu()
        self.volume_menu = QMenu()
        self.CreateTrayMenu()

        self.setWindowIcon(QIcon(wiconpath))

        # context menu for TableWidget
        self.volumetable = self.findChild(QtWidgets.QTableWidget, 'tbl_Volumes')
        self.volumetablemenu = QMenu()
        self.volumetable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.volumetable.customContextMenuRequested.connect(self.CreateVolumeMenu)
        # capture right click
        self.volumetable.viewport().installEventFilter(self)
        # capture double click
        self.volumetable.doubleClicked.connect(self.TableDoubleClicked)


    def eventFilter(self, source, event):
        if(event.type() == QtCore.QEvent.MouseButtonPress and
           event.buttons() == QtCore.Qt.RightButton and
           source is self.volumetable.viewport()):
            item = self.volumetable.itemAt(event.pos())
            encfsgui_helper.print_debug('Right-click at Global Pos: %s' % event.globalPos())
            if item is not None:
                encfsgui_helper.print_debug('Right-click Table Item: %s %s' % (item.row(), item.column()))
                encfsgui_helper.print_debug('Currently selected volume: %s' % encfsgui_globals.g_CurrentlySelected)
                self.CreateVolumeMenu()
                self.volumetablemenu.exec_(event.globalPos())
                #menu.exec_(event.globalPos())
        return super(CMainWindow, self).eventFilter(source, event)


    # table double click
    def TableDoubleClicked(self):
        if encfsgui_globals.g_Settings["doubleclickmount"].lower() == "true":
            if encfsgui_globals.g_CurrentlySelected != "":
                volumename = encfsgui_globals.g_CurrentlySelected
                if volumename in encfsgui_globals.g_Volumes:
                    EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
                    if EncVolumeObj.ismounted:
                        self.UnmountVolumeClicked()
                    else:
                        self.MountVolumeClicked()
        return

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
                msgBox.setFocus()
                if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
                    doexit = True
            else:
                doexit = True

        if doexit:
            self.AutoUnMount()
            encfsgui_helper.print_debug("Application has exited.")
            sys.exit(0)
        return

    def ShowButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.show_action.setEnabled(False)
        self.hide_action.setEnabled(True)
        encfsgui_globals.ishidden = False
        self.show()
        # force reload of modules and update window
        self.lbl_infolabel.setText("")
        self.volumetable.clearContents()
        self.volumetable.setRowCount(0)
        encfsgui_globals.appconfig.getVolumes()
        self.RefreshVolumes()
        self.PopulateVolumeMenu()
        self.setFocus()
        return

    def HideButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.show_action.setEnabled(True)
        self.hide_action.setEnabled(False)
        if encfsgui_globals.g_Settings["clearkeywhenhidden"].lower() == "true":
            print_debug("Hiding window, clearing masterkey")
            encfsgui_globals.masterkey = ""
        encfsgui_globals.ishidden = True
        self.PopulateVolumeMenu()   # will disable menu if needed
        # only hide on macos
        try:
            if encfsgui_helper.ismacOS():
                self.hide()
            elif encfsgui_helper.isLinux():
                self.showMinimized()
        except Exception as e:
            print_debug("Error hiding/minimizing: %s" % str(e))
        return

    def AboutClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        abouttext = "pyencfsgui (EncFSGui) is a python3/PyQT5 based GUI wrapper around encfs and/or gocryptfs.\n\n"
        abouttext += "This version has been tested with encfs 1.9.x on OSX Catalina (and newer macOS versions), \n"
        abouttext += "and with gocryptfs 1.8.x on OSX Big Sur (and newer macOS versions). \n"
        abouttext += "Additionally, EncFSGui has been confirmed to work in Kali Linux.\n\n"
        abouttext += "Development started in 2019. The utility was written by Peter 'corelanc0d3r' Van Eeckhoutte.\n"
        abouttext += "Corelan Consulting bv\nwww.corelan-consulting.com | www.corelan-training.com\n\n"
        abouttext += "Project repository:\nhttps://github.com/corelan/pyencfsgui\n\n"
        abouttext += "Version info:\n"
        abouttext += "EncFSGui version %s.\n" % encfsgui_helper.getVersion()

        if os.path.exists(encfsgui_globals.g_Settings["encfspath"]):
            abouttext +=  "encfs version %s.\n" % getEncFSVersion()
        else:
            abouttext +=  "encfs not found.\n"
        
        if os.path.exists(encfsgui_globals.g_Settings["gocryptfspath"]):
            abouttext +=  "gocryptfs version %s.\n\n" % getGoCryptFSVersion()
        else:
            abouttext +=  "gocryptfs not found.\n\n"
        
        abouttext +=  "This application uses icons from https://icons8.com.\n"
        abouttext +=  "\nYou are running %s" % encfsgui_helper.getOSType()

        msgBox = QMessageBox()
        msgBox.setWindowTitle("About pyencfsgui")
        msgBox.setText(abouttext)
        msgBox.show()
        msgBox.exec_()
        return

    def checkFilenameEncodings(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        encfsgui_helper.print_debug("Encodings: %s" % encfsgui_globals.g_Encodings)
        if len(encfsgui_globals.g_Encodings) == 0:
            self.volumetable.setEnabled(False)
            self.lbl_infolabel.setText("Getting filename encoding capabilities, hold on...")
            self.lbl_infolabel.update()
            encfsgui_globals.app.processEvents()
            self.update()
            encfsgui_helper.determineFileNameEncodings()
            encfsgui_helper.print_debug("Encodings: %s" % encfsgui_globals.g_Encodings)
            encfsgui_globals.appconfig.saveSettings()
            self.volumetable.setEnabled(True)
            self.SetInfoLabel()
        return

    # context menu
    def CreateVolumeMenu(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.volumetablemenu.clear()
        volumename = encfsgui_globals.g_CurrentlySelected 
        if volumename != "":
            if volumename in encfsgui_globals.g_Volumes:
                EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
                self.volumemenuheader = QAction("Actions for volume '%s':" % volumename, self)
                self.volumetablemenu.addAction(self.volumemenuheader)
                self.volumetablemenu.addSeparator()
                if not EncVolumeObj.ismounted:
                    self.volumemountaction = QAction(QIcon("./bitmaps/icons8-unlock-24.png"),"Mount volume", self) 
                    self.volumetablemenu.addAction(self.volumemountaction)
                    self.volumemountaction.triggered.connect(self.TableMenuMountVolume)
                    self.volumeeditaction = QAction("Edit volume", self)
                    self.volumetablemenu.addAction(self.volumeeditaction)
                    self.volumeeditaction.triggered.connect(self.EditVolumeButtonClicked)
                else:
                    self.volumeunmountaction = QAction(QIcon("./bitmaps/icons8-lock-24.png"), "Unmount volume", self)
                    self.volumetablemenu.addAction(self.volumeunmountaction)
                    self.volumeunmountaction.triggered.connect(self.TableMenuUnmountVolume)
                self.volumeinfoaction = QAction("Show info", self)
                self.volumetablemenu.addAction(self.volumeinfoaction)
                self.volumeinfoaction.triggered.connect(self.ShowVolumeInfoClicked)
        return


    # system tray menu
    def CreateTrayMenu(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.show_action = QAction("Show", self)
        self.hide_action = QAction("Hide", self)
        self.settings_action = QAction("Settings", self)
        self.about_action = QAction("About", self)
        self.quit_action = QAction("Quit", self)
        self.refresh_action = QAction("Refresh", self)
        
        self.show_action.triggered.connect(self.ShowButtonClicked)
        self.hide_action.triggered.connect(self.HideButtonClicked)
        self.settings_action.triggered.connect(self.SetttingsButtonClicked)
        self.about_action.triggered.connect(self.AboutClicked)
        self.quit_action.triggered.connect(self.QuitButtonClicked)
        self.refresh_action.triggered.connect(self.RefreshVolumesClicked)

        self.PopulateVolumeMenu()

        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.hide_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.refresh_action)
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
        buildmenu = False
        # only build menu in certain cases
        encfsgui_helper.print_debug("Main window hidden? %s" % str(encfsgui_globals.ishidden))
        encfsgui_helper.print_debug("Encrypt? %s" % encfsgui_globals.g_Settings["encrypt"].lower() )
        encfsgui_helper.print_debug("Clear Key? %s" % encfsgui_globals.g_Settings["clearkeywhenhidden"].lower())
        if not encfsgui_globals.ishidden:
            buildmenu = True
        else:
            if encfsgui_globals.g_Settings["encrypt"].lower() == "true" and encfsgui_globals.g_Settings["clearkeywhenhidden"].lower() == "true": 
                buildmenu = False
            else:
                buildmenu = True
        if buildmenu: 
            self.volume_menu.setEnabled(True)
            sorted_volumes = {k: encfsgui_globals.g_Volumes[k] for k in sorted(encfsgui_globals.g_Volumes)}
            for volumename in sorted_volumes:
                EncVolumeObj = encfsgui_globals.g_Volumes[volumename]

                addtolist = True

                if encfsgui_globals.g_Settings["hidevolumenotfound"].lower() == "true":
                    addtolist = EncVolumeObj.enc_path_exists

                if addtolist:
                    self.volume_mount = QAction(QIcon("./bitmaps/icons8-unlock-24.png"),  "Mount '%s'" % volumename, self)
                    self.volume_mount.triggered.connect(self.MenuMountVolume)
                    self.volume_menu.addAction(self.volume_mount)
                    
                    self.volume_unmount = QAction(QIcon("./bitmaps/icons8-lock-24.png"), "Unmount '%s'" % volumename, self)
                    self.volume_unmount.triggered.connect(self.MenuUnmountVolume)
                    self.volume_menu.addAction(self.volume_unmount)

                    self.volume_menu.addSeparator()

                    if EncVolumeObj.ismounted:
                        self.volume_mount.setEnabled(False)
                        self.volume_mount.setVisible(False)
                        self.volume_unmount.setEnabled(True)
                        self.volume_unmount.setVisible(True)
                    else:
                        self.volume_mount.setEnabled(True)
                        self.volume_mount.setVisible(True)
                        self.volume_unmount.setEnabled(False)
                        self.volume_unmount.setVisible(False)
        else:
            self.volume_menu.setEnabled(False)
        return

    def MenuMountVolume(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        actionname = self.sender().text()
        volumename = self.getVolumeNameFromAction(actionname)
        if volumename in encfsgui_globals.g_Volumes:
            thispassword = self.getPasswordForVolume(volumename)
            self.MountVolume(volumename, thispassword)
        self.PopulateVolumeMenu()
        return

    def TableMenuMountVolume(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        volumename = encfsgui_globals.g_CurrentlySelected
        if volumename in encfsgui_globals.g_Volumes:
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

    def TableMenuUnmountVolume(self, action):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        volumename = encfsgui_globals.g_CurrentlySelected
        self.UnmountVolume(volumename)
        self.PopulateVolumeMenu()
        return

    def getVolumeNameFromAction(self, actionname):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        volumename = ""
        if (actionname.startswith("Mount")):
            volumename = actionname.lstrip("Mount ").lstrip("'").rstrip("'")
        elif (actionname.startswith("Unmount")):
            volumename = actionname.lstrip("Unmount ").lstrip("'").rstrip("'")
        return volumename


    def CreateVolumeButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.checkFilenameEncodings()
        createvolumewindow = CVolumeWindow()
        createvolumewindow.show()
        createvolumewindow.setRunMode(0)    # create
        createvolumewindow.setFocus()
        createvolumewindow.activateWindow()
        createvolumewindow.exec_()
        self.RefreshVolumes()
        self.PopulateVolumeMenu()
        return


    def AddVolumeButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        addvolumewindow = CVolumeWindow()
        addvolumewindow.show()
        addvolumewindow.setRunMode(1)    # add
        addvolumewindow.setFocus()
        addvolumewindow.activateWindow()
        addvolumewindow.exec_()
        self.RefreshVolumes()
        self.PopulateVolumeMenu()
        return       

    def EditVolumeButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.checkFilenameEncodings()
        if encfsgui_globals.g_CurrentlySelected != "":
            editvolumewindow = CVolumeWindow()
            editvolumewindow.show()
            editvolumewindow.setRunMode(2)    # edit
            editvolumewindow.origvolumename = encfsgui_globals.g_CurrentlySelected
            editvolumewindow.PopulateFields(encfsgui_globals.g_CurrentlySelected)
            editvolumewindow.setFocus()
            editvolumewindow.activateWindow()
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
                    encfsgui_helper.RemovePasswordFromKeyChain(volumename)
                    encfsgui_globals.appconfig.delVolume(volumename)                  
                    encfsgui_globals.appconfig.getVolumes()
                    self.RefreshVolumes()
        return

    def ShowVolumeInfoClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        volumename = encfsgui_globals.g_CurrentlySelected
        if volumename != "":
            if volumename in encfsgui_globals.g_Volumes:
                EncVolumeObj =  encfsgui_globals.g_Volumes[volumename]
                infotext = ""
                if EncVolumeObj.enctype == "encfs":
                    if os.path.exists(encfsgui_globals.g_Settings["encfspath"]):
                        cmd = "%sctl info '%s'" % (encfsgui_globals.g_Settings["encfspath"], EncVolumeObj.enc_path)
                        cmdoutput = encfsgui_helper.execOSCmd(cmd)
                        infotext = "EncFS volume info for '%s'\n" % volumename
                        infotext += "Encrypted folder '%s'\n\n" % EncVolumeObj.enc_path
                        for l in cmdoutput:
                            infotext = infotext + l + "\n"

                if EncVolumeObj.enctype == "gocryptfs":
                    if os.path.exists(encfsgui_globals.g_Settings["gocryptfspath"]):
                        cmd = "%s -info '%s'" % (encfsgui_globals.g_Settings["gocryptfspath"], EncVolumeObj.enc_path)
                        cmdoutput = encfsgui_helper.execOSCmd(cmd)
                        infotext = "GoCryptFS volume info for '%s'\n" % volumename
                        infotext += "Encrypted folder '%s'\n\n" % EncVolumeObj.enc_path
                        for l in cmdoutput:
                            infotext = infotext + l + "\n"
                if not infotext == "":
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setIcon(QtWidgets.QMessageBox.Information)
                    msgBox.setWindowTitle("Encrypted Volume info (%s)" % EncVolumeObj.enctype)
                    msgBox.setText(infotext)
                    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msgBox.show()
                    msgBox.exec_()
        return

    def RefreshVolumesClicked(self): 
        self.RefreshVolumes()
        return

    def SetttingsButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        settingswindow = CSettingsWindow()
        settingswindow.loadSettings()
        settingswindow.show()
        settingswindow.setFocus()
        settingswindow.activateWindow()
        settingswindow.exec_()
        # when dialog closes, refresh settings (in case user made a change)
        self.RefreshSettings()
        # don't refresh gui if gui is hidden, otherwise app might ask for master key
        if not encfsgui_globals.ishidden:
            self.RefreshVolumes()
        self.PopulateVolumeMenu()
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
            frmpassword = CMountPasswordWindow()
            frmpassword.setEncPath(EncVolumeObj.enc_path)
            frmpassword.setMountPath(EncVolumeObj.mount_path)
            frmpassword.setWindowTitle("Please enter password for volume '%s'" % volumename)
            frmpassword.show()
            frmpassword.setFocus()
            frmpassword.activateWindow()
            frmpassword.exec_()
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
        continueunmount = True
        if  encfsgui_globals.g_Settings["confirmforceunmountall"].lower() == "true":
            forcedmsgBox = QtWidgets.QMessageBox()
            forcedmsgBox.setIcon(QMessageBox.Question)
            forcedmsgBox.setWindowTitle("Are you sure?")
            forcedmsgBox.setText("Are you sure you would like to forcibly unmount all volumes now?")
            forcedmsgBox.setStandardButtons(QtWidgets.QMessageBox.Yes)
            forcedmsgBox.addButton(QtWidgets.QMessageBox.No)
            forcedmsgBox.show()
            if (forcedmsgBox.exec_() == QtWidgets.QMessageBox.No):
                continueunmount = False
        if continueunmount:
            for volumename in encfsgui_globals.g_Volumes:
                self.UnmountVolume(volumename, True)
        self.RefreshVolumes()
        return

    def UnmountVolume(self, volumename, forced=False):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # do we need to ask for confirmation?
        askforconfirmation = True
        dounmount = False
        if "noconfirmationunmount" in encfsgui_globals.g_Settings:
            if encfsgui_globals.g_Settings["noconfirmationunmount"].lower() == "true":
                askforconfirmation = False

        if volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            if EncVolumeObj.ismounted:
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
                cmd = "'%s' '%s'" % (encfsgui_globals.g_Settings["umountpath"], EncVolumeObj.mount_path)
                if EncVolumeObj.sudo == "1":
                    cmd = "sudo '%s' '%s'" % (encfsgui_globals.g_Settings["umountpath"], EncVolumeObj.mount_path)
                encfsgui_helper.execOSCmd(cmd)
                # did unmount work?
                self.RefreshVolumes()
                EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
                if EncVolumeObj.ismounted:
                    QtWidgets.QMessageBox.critical(None,"Error unmounting volume","Unable to unmount volume '%s'\nMake sure all files are closed and try again." % volumename)

        # update context menu's
        self.PopulateVolumeMenu()

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
            if (password != ""):
                if not encfsgui_helper.ifExists(EncVolumeObj.enctype):
                    QtWidgets.QMessageBox.critical(None,"Error mounting volume","Unable to mount volume '%s', '%s' binary not found\n" % ( volumename, EncVolumeObj.enctype))
                else:
                    usesudo = ""
                    if EncVolumeObj.sudo == "1":
                        usesudo = "sudo"

                    # if volume is encfs:
                    if EncVolumeObj.enctype == "encfs":
                        extra_osxfuse_opts = ""
                        #mountcmd = "%s '%s' '%s' %s" % (encfsgui_globals.g_Settings["encfspath"], EncVolumeObj.enc_path, EncVolumeObj.mount_path, EncVolumeObj.encfsmountoptions)
                        if (str(EncVolumeObj.allowother) == "1"):
                            extra_osxfuse_opts += "-o allow_other "
                        if (str(EncVolumeObj.mountaslocal) == "1"):
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
                        mountcmd = "sh -c \"echo '%s' | %s '%s' -v -S %s %s -o volname='%s' '%s' '%s' \"" % (str(password), usesudo, encfsbin, extra_osxfuse_opts, encfsmountoptions, volumename, encvol, mountvol)

                        encfsgui_helper.execOSCmd(mountcmd)

                    # if volume is gocryptfs:
                    if EncVolumeObj.enctype == "gocryptfs":
                        extra_osxfuse_opts = ""
                        extra_gocryptfs_opts = ""
                        if (str(EncVolumeObj.allowother) == "1"):
                            extra_gocryptfs_opts += "-allow_other "
                        if (str(EncVolumeObj.mountaslocal) == "1"):
                            extra_osxfuse_opts += "-ko local "
                        # first, create mount point if necessary
                        createfoldercmd = "mkdir -p '%s'" % EncVolumeObj.mount_path
                        encfsgui_helper.execOSCmd(createfoldercmd)

                        gocryptfsbin = encfsgui_globals.g_Settings["gocryptfspath"]
                        encvol = EncVolumeObj.enc_path
                        mountvol = EncVolumeObj.mount_path
                        if not EncVolumeObj.encfsmountoptions == "":
                            extra_gocryptfs_opts += "'%s'" % EncVolumeObj.encfsmountoptions

                        # do the actual mount
                        #mountcmd = "sh -c \"echo '%s' | %s -v -S %s %s -o volname='%s' '%s' '%s' \"" % (str(password), gocryptfsbin, extra_osxfuse_opts, gocryptfsmountoptions, volumename, encvol, mountvol)
                        mountcmd = "sh -c \"echo '%s' | %s '%s' -ko volname='%s' -ko fsname='%s' %s %s '%s' '%s'\"" % (str(password), usesudo, gocryptfsbin, volumename, volumename, extra_osxfuse_opts, extra_gocryptfs_opts, encvol, mountvol)

                        encfsgui_helper.execOSCmd(mountcmd)

                    self.RefreshVolumes()
                    EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
                    if not EncVolumeObj.ismounted:
                        QtWidgets.QMessageBox.critical(None,"Error mounting volume","Unable to mount volume '%s'\n\n%s" % ( volumename, EncVolumeObj.errormessage ))
            else:
                encfsgui_helper.print_debug("Did not attempt to mount, empty password given")

            # update context menu's
            self.PopulateVolumeMenu()
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
        # don't reload if main window is hidden, prevent masterkey to be required
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        encfsgui_helper.print_debug("%s() Called from: %s()" % (inspect.stack()[0][3],calframe[1][3]))          
    
        # get volumes from config file
        encfsgui_globals.appconfig.getVolumes()
        # show volumes in the table
        self.volumetable.clearContents()
        self.volumetable.setColumnCount(5)
        
        #self.volumetable.setRowCount(len(encfsgui_globals.g_Volumes))
        self.volumetable.setRowCount(0)

        columnheaders = ['Mounted?', 'Volume Name', 'Encrypted folder', 'Mount at', 'Automount?']
        self.volumetable.setHorizontalHeaderLabels(columnheaders)

        self.volumetable.setColumnWidth(0,75)
        self.volumetable.setColumnWidth(1,125)
        self.volumetable.setColumnWidth(2,365)
        self.volumetable.setColumnWidth(3,325)
        self.volumetable.setColumnWidth(4,95)

        # sort 
        sorted_volumes = {k: encfsgui_globals.g_Volumes[k] for k in sorted(encfsgui_globals.g_Volumes)}

        volumeindex = 0
        volumesfoundsofar = 0
        for volumekey in sorted_volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumekey]
            addtolist = True

            if encfsgui_globals.g_Settings["hidevolumenotfound"].lower() == "true":
                addtolist = EncVolumeObj.enc_path_exists

            if addtolist:
                volumesfoundsofar += 1
                self.volumetable.setRowCount(volumesfoundsofar)

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
        #if not encfsgui_globals.ishidden:
        #    self.SetInfoLabel()
        return

    def SetInfoLabel(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        encfspath = encfsgui_globals.g_Settings["encfspath"]
        gocryptfspath = encfsgui_globals.g_Settings["gocryptfspath"]
        encfsinfo = "encfs not found"

        if os.path.exists(encfspath):
            encfsinfo = "encfs v%s" % (getEncFSVersion())
        gocryptfsinfo = "gocryptfs not found"

        if os.path.exists(gocryptfspath):
            gocryptfsinfo = "gocryptfs %s" % (getGoCryptFSVersion())

        self.lbl_infolabel.setText(" %s  | %s  |  Nr of volumes: %d  |  %s" % (encfsinfo, gocryptfsinfo, self.volumetable.rowCount(), encfsgui_globals.volumesfile ))
        self.lbl_infolabel.update()
        encfsgui_globals.app.processEvents()
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
    try:
        encfsgui_globals.masterkey = ""
        encfsgui_globals.settingsfile = 'encfsgui.settings'
        encfsgui_helper.createFile(encfsgui_globals.logfile)

        encfsgui_globals.appconfig = CConfig()
        settingsfilefound = encfsgui_globals.appconfig.getSettings()

        encfsgui_globals.volumesfile = encfsgui_globals.g_Settings["workingfolder"] + "/" + 'encfsgui.volumes'
            
        if str(encfsgui_globals.g_Settings["debugmode"]).lower() == "true":
            encfsgui_globals.debugmode = True
        else:
            encfsgui_globals.debugmode = False
        
        encfsgui_helper.print_debug("Create main window")
        mainwindow = CMainWindow()
        mainwindow.RefreshSettings()

        updateresult = 0

        encfsgui_helper.print_debug("Check for updates? %s" % str(encfsgui_globals.g_Settings["autoupdate"]).lower())

        if str(encfsgui_globals.g_Settings["autoupdate"]).lower() == "true":
            
            mainwindow.lbl_infolabel.setText("Checking for updates...")

            updateresult, gitoutput = encfsgui_helper.autoUpdate()

            if updateresult == 0:
                appupdatestatus = "Up to date."
            elif updateresult == 1:
                appupdatestatus = '<span style="color:red">Update found, please restart.<span>'
            elif updateresult == -1:
                appupdatestatus = '<span style="color:red">Possible error while running "git pull"<span>'

            mainwindow.lbl_updatestate.setText(appupdatestatus)
            if not updateresult == 0:
                boldfont = QFont()
                boldfont.setBold(True)
                mainwindow.lbl_updatestate.setFont(boldfont)

        if updateresult == 1:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle("Update found?")
            msgBox.setText("An update has been found and downloaded via 'git pull'.\n\nPlease restart the application to run the updated code.\n\nWould you like to exit now?")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.No)
            msgBox.addButton(QtWidgets.QMessageBox.Yes)
            msgBox.show()
            msgBox.setFocus()
            if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):
                mainwindow.QuitButtonClicked()
        elif updateresult == -1:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle("Error while running 'git pull'")
            msgtext = "An error may have occurred while running 'git pull'.\nOutput:\n\n"
            for l in gitoutput:
                msgtext += ">> %s\n" % l
            msgBox.setText(msgtext)
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.show()
            msgBox.setFocus()

        mainwindow.lbl_updatestate.setText("")
        mainwindow.initMainWindow()

        try:
            icondir = encfsgui_helper.getCurDir()
            iconfolder = os.path.join(icondir,'bitmaps' )
            iconpath = os.path.join(iconfolder, 'encfsgui.ico')
            encfsgui_globals.app.setWindowIcon(QIcon(iconpath))
            print_debug("Set application icon '%s'" % iconpath)
        except:
            print_debug("Unable to set application icon '%s'" % iconpath)
            pass

        curversion = "EncFSGui v%s" % encfsgui_helper.getVersion()

        encfsgui_globals.app.setApplicationName(curversion)
        encfsgui_globals.app.setApplicationDisplayName(curversion)
        mainwindow.setWindowTitle(curversion)

        if encfsgui_globals.g_Settings["encrypt"].lower() == "true":
            encfsgui_helper.getMasterKey()

        encfsgui_globals.appconfig.getVolumes()

        if not settingsfilefound:
            QtWidgets.QMessageBox.information(None,"Please verify and confirm settings","It looks like the application settings were not verified & confirmed yet.\n\nI'll open the settings window so you can check if everything looks ok.")
            mainwindow.SetttingsButtonClicked()

        mainwindow.RefreshVolumes()
        mainwindow.AutoMount()

        if str(encfsgui_globals.g_Settings["starthidden"]).lower() == "false":
            mainwindow.show()
            encfsgui_globals.ishidden = False
        else:
            encfsgui_globals.ishidden = True
            mainwindow.PopulateVolumeMenu()
            encfsgui_globals.appconfig.clearMasterKeyIfNeeded()
            # on Linux, show minimized
            if encfsgui_helper.isLinux():
                #mainwindow.show()
                mainwindow.showMinimized()

        encfsgui_globals.app.setQuitOnLastWindowClosed(False)

        encfsgui_globals.app.exec_()

        encfsgui_helper.print_debug("Application has exited.")


    except Exception: 
        msg = traceback.format_exc()
        print(msg)
        try:
            encfsgui_helper.print_debug(msg)
        except:
            pass
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Error")
        msgBox.setText(msg)
        msgBox.show()
        msgBox.exec_()
        
