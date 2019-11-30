# encfsgui CConfig
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


class CConfig():
    def __init__(self):
        self.settingsfile = encfsgui_globals.settingsfile
        self.volumesfile = encfsgui_globals.volumesfile 
        self.getSettings()
        self.getVolumes()
        return

    def getVolumes(self):
        encfsgui_globals.g_Volumes = { }
        
        volumeconfig = configparser.ConfigParser()
        volumeconfig.read(self.volumesfile)

        # prepare to get mount states
        mountcmd = encfsgui_globals.g_Settings["mountpath"]
        mountlist = encfsgui_helper.execOSCmd(mountcmd)

        for volumename in volumeconfig.sections():
            EncVolume = CEncryptedVolume()
            if "enc_path" in volumeconfig[volumename]:
                EncVolume.enc_path = volumeconfig[volumename]["enc_path"]
            if "mount_path" in volumeconfig[volumename]:
                EncVolume.mount_path = volumeconfig[volumename]["mount_path"]
            if "automount" in  volumeconfig[volumename]:
                EncVolume.automount = volumeconfig[volumename]["automount"]
            if "preventautounmount" in volumeconfig[volumename]:
                EncVolume.preventautounmount = volumeconfig[volumename]["preventautounmount"]
            if "allowother" in volumeconfig[volumename]:
                EncVolume.allowother = volumeconfig[volumename]["allowother"]
            if "mountaslocal" in volumeconfig[volumename]:
                EncVolume.mountaslocal = volumeconfig[volumename]["mountaslocal"]
            if "encfsmountoptions" in volumeconfig[volumename]:
                EncVolume.encfsmountoptions = volumeconfig[volumename]["encfsmountoptions"]
            if "passwordsaved" in  volumeconfig[volumename]:
                EncVolume.passwordsaved = volumeconfig[volumename]["passwordsaved"]

            EncVolume.ismounted = False
            if EncVolume.mount_path != "":
                for item in mountlist:        
                    if "encfs" in str(item) and EncVolume.mount_path in str(item):
                        EncVolume.ismounted = True
                        break

            encfsgui_globals.g_Volumes[volumename] = EncVolume   
                
        return
    
    def getSettings(self):
        # read settings from settings file

        # if file does not exist, generate default file
        if not os.path.exists(self.settingsfile):
            self.populateDefaultSettings()
            self.saveSettings() 

        appsettings = configparser.ConfigParser()
        appsettings.read(self.settingsfile)

        for settingkey in appsettings["config"]:
            encfsgui_globals.g_Settings[settingkey] = appsettings["config"][settingkey].strip().replace("\n","")
            #encfsgui_helper.print_debug("%s = %s" % (settingkey, encfsgui_globals.g_Settings[settingkey]))
        # in case the current settings file is incomplete, pick up additional settings
        self.populateDefaultSettings()
        self.saveSettings()   
        return

    def populateDefaultSettings(self):
        #global encfsgui_globals.g_Settings
        if not "encfspath" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["encfspath"] = "/usr/local/bin/encfs"
        if not "mountpath" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["mountpath"] = "/sbin/mount"
        if not "umountpath" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["umountpath"] = "/sbin/umount"
        if not "autounmount" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["autounmount"] = "false"
        if not "noconfirmationunmount" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["noconfirmationunmount"] = "false"
        if not "noconfirmationexit" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["noconfirmationexit"] = "false"
        return

    def addVolume(self):
        return

    def delVolume(self):
        return

    def saveSettings(self):
        # just in case a new setting was added, get default values
        self.populateDefaultSettings()
        config = configparser.RawConfigParser()
        config.add_section('config')
        for settingkey in encfsgui_globals.g_Settings:
            config.set('config', settingkey, encfsgui_globals.g_Settings[settingkey])

        # save file to disk
        with open(self.settingsfile, 'w') as configfile:
            config.write(configfile)
        return