# encfsgui CConfig
# 
#  

import os
import sys
import time
import datetime
import string
import configparser
import inspect

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import encfsgui_globals
from encfsgui_globals import *

import encfsgui_helper
from encfsgui_helper import *


class CConfig():
    def __init__(self):
        self.settingsfile = encfsgui_globals.settingsfile
        return

    def getVolumes(self):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        encfsgui_helper.print_debug("%s() Called from: %s()" % (inspect.stack()[0][3],calframe[1][3]))          
        encfsgui_globals.g_Volumes.clear()
        
        volumeconfig = configparser.ConfigParser()
        volumeconfig.read(encfsgui_globals.volumesfile)

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
            if "type" in volumeconfig[volumename]:
                EncVolume.enctype = volumeconfig[volumename]["type"]
            if "enctype" in volumeconfig[volumename]:
                EncVolume.enctype = volumeconfig[volumename]["enctype"]
            else:
                EncVolume.enctype = "encfs"
            if "sudo" in volumeconfig[volumename]:
                EncVolume.sudo = volumeconfig[volumename]["sudo"]

            # do we need to decrypt ?
            # if encryption is enabled, decrypt strings in memory using master password
            if encfsgui_globals.g_Settings["encrypt"] == "true":
                # do we have the master key?
                if (encfsgui_globals.masterkey == ""):
                    # ask for masterkey
                    encfsgui_helper.getMasterKey()
                    print_debug("Obtained masterkey, length %d" % len(encfsgui_globals.masterkey))
                if (encfsgui_globals.masterkey != ""):
                    try:
                        EncVolume.enc_path = encfsgui_helper.decrypt(EncVolume.enc_path).decode()
                        EncVolume.mount_path = encfsgui_helper.decrypt(EncVolume.mount_path).decode()
                        encfsgui_globals.timeswrong = 0
                    except Exception: 
                        msg = traceback.format_exc()
                        print(msg)
                        encfsgui_helper.print_debug(msg)
                        QtWidgets.QMessageBox.critical(None,"Error","Error decrypting information.\n\nTry again later.")
                        encfsgui_globals.masterkey = ""
                        encfsgui_globals.timeswrong += 1
                        if encfsgui_globals.timeswrong > 3:
                            sys.exit(1)

            encfsgui_helper.print_debug("Check if path '%s' exists" % EncVolume.enc_path)
            EncVolume.enc_path_exists = os.path.exists(EncVolume.enc_path)
            encfsgui_helper.print_debug(">> %s" % str(EncVolume.enc_path_exists))

            EncVolume.ismounted = False
            encfsgui_helper.print_debug("Check if volume '%s' is mounted" % volumename)
            if EncVolume.mount_path != "":
                # the extra space is important !
                path_to_check = "%s " % EncVolume.mount_path
                for item in mountlist:
                    if EncVolume.enctype == "encfs":  
                        if "encfs" in str(item) and path_to_check in str(item):
                            encfsgui_helper.print_debug("EncFS volume is mounted, mount path '%s' found in '%s'" % (path_to_check, str(item).strip()))
                            EncVolume.ismounted = True
                            break
                    elif EncVolume.enctype == "gocryptfs":
                        if path_to_check in str(item):
                            encfsgui_helper.print_debug("GoCryptFS volume is mounted, mount path '%s' found in '%s'" % (path_to_check, str(item).strip()))
                            EncVolume.ismounted = True
                            break                            
                if not EncVolume.ismounted:
                    encfsgui_helper.print_debug("Volume is not mounted")
            encfsgui_globals.g_Volumes[volumename] = EncVolume

        self.clearMasterKeyIfNeeded()
        return
    

    def clearMasterKeyIfNeeded(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        encfsgui_helper.print_debug("%s() Called from: %s()" % (inspect.stack()[0][3],calframe[1][3]))   
        if encfsgui_globals.ishidden:
            if encfsgui_globals.g_Settings["clearkeywhenhidden"].lower() == "true":
                encfsgui_globals.masterkey = ""
                encfsgui_helper.print_debug("Cleared masterkey")
        return

    def getSettings(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        encfsgui_helper.print_debug("%s() Called from: %s()" % (inspect.stack()[0][3],calframe[1][3]))           
        # if file does not exist, generate default file
        if not os.path.exists(self.settingsfile):
            self.populateDefaultSettings()
            self.saveSettings()

        # if file exists, but does not contain the config section, then regenerate the file as well
        appsettings = configparser.ConfigParser()
        appsettings.read(self.settingsfile)

        if not "config" in appsettings:
            self.populateDefaultSettings()
            self.saveSettings()            

        # we should have a working config file now
        appsettings = configparser.ConfigParser()
        appsettings.read(self.settingsfile)

        for settingkey in appsettings["config"]:
            encfsgui_globals.g_Settings[settingkey] = appsettings["config"][settingkey].strip().replace("\n","")
        
        if "encodings" in appsettings:
            encodinglist = appsettings["encodings"]["filenameencodings"]
            encfsgui_globals.g_Encodings = encodinglist.split(",")

        # in case the current settings file is incomplete, pick up additional settings
        self.populateDefaultSettings()
        self.saveSettings()

        encfsgui_globals.volumesfile = encfsgui_globals.g_Settings["workingfolder"] + "/" + 'encfsgui.volumes'

        return

    def populateDefaultSettings(self):
        #global encfsgui_globals.g_Settings
        if not "encfspath" in encfsgui_globals.g_Settings:
            whichpath = encfsgui_helper.runwhich("encfs")
            if whichpath != "":
                encfsgui_globals.g_Settings["encfspath"] = whichpath
            else:
                encfsgui_globals.g_Settings["encfspath"] = "/usr/local/bin/encfs"

        if not "gocryptfspath" in encfsgui_globals.g_Settings:
            whichpath = encfsgui_helper.runwhich("gocryptfs")
            if whichpath != "":
                encfsgui_globals.g_Settings["gocryptfspath"] = whichpath
            else:   
                encfsgui_globals.g_Settings["gocryptfspath"] = "/usr/local/bin/gocryptfs"
                if os.path.exists("/opt/homebrew/bin/gocryptfs"):
                    encfsgui_globals.g_Settings["gocryptfspath"] = "/opt/homebrew/bin/gocryptfs"

        if not "mountpath" in encfsgui_globals.g_Settings:
            whichpath = encfsgui_helper.runwhich("mount")
            if whichpath != "":
                encfsgui_globals.g_Settings["mountpath"] = whichpath
            else:    
                encfsgui_globals.g_Settings["mountpath"] = "/sbin/mount"

        if not "umountpath" in encfsgui_globals.g_Settings:
            whichpath = encfsgui_helper.runwhich("umount")
            if whichpath != "":
                encfsgui_globals.g_Settings["umountpath"] = whichpath
            else:    
                encfsgui_globals.g_Settings["umountpath"] = "/sbin/umount"

        if not "autounmount" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["autounmount"] = "false"
        if not "noconfirmationunmount" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["noconfirmationunmount"] = "false"
        if not "noconfirmationexit" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["noconfirmationexit"] = "false"
        if not "workingfolder" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["workingfolder"] = "."
        if not "starthidden" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["starthidden"] = "false"
        if not "debugmode" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["debugmode"] = "false"
            encfsgui_globals.debugmode = False
        if not "autoupdate" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["autoupdate"] = "false"
        if not "confirmforceunmountall" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["confirmforceunmountall"] = "false"
        if not "doubleclickmount" in encfsgui_globals.g_Settings: 
            encfsgui_globals.g_Settings["doubleclickmount"] = "false"
        if not "encrypt" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["encrypt"] = "false"
        if not "clearkeywhenhidden" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["clearkeywhenhidden"] = "false"
        if not "hidevolumenotfound" in encfsgui_globals.g_Settings:
            encfsgui_globals.g_Settings["hidevolumenotfound"] = "false"            
        return

    def addVolume(self, volumename, EncVolumeObj):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        encfsgui_globals.g_Volumes[volumename] = EncVolumeObj
        # write g_Volumes to volumes file
        self.saveVolumes()
        return

    def delVolume(self, volumename):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # remove volume from g_Volumes
        if (volumename in encfsgui_globals.g_Volumes):
            del encfsgui_globals.g_Volumes[volumename]
        # write g_Volumes to volumes file
        self.saveVolumes()
        return

    def saveSettings(self):
        # just in case a new setting was added, get default values
        self.populateDefaultSettings()
        config = configparser.RawConfigParser()
        config.add_section('config')
        for settingkey in encfsgui_globals.g_Settings:
            config.set('config', settingkey, encfsgui_globals.g_Settings[settingkey])

        if len(encfsgui_globals.g_Encodings) > 0:
            config.add_section('encodings')
            config.set('encodings','filenameencodings', ",".join(encfsgui_globals.g_Encodings))

        # save file to disk
        with open(self.settingsfile, 'w') as configfile:
            config.write(configfile)

        encfsgui_globals.volumesfile = encfsgui_globals.g_Settings["workingfolder"] + "/" + 'encfsgui.volumes'

        return

    def saveVolumes(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        config = configparser.RawConfigParser()
        for volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            config.add_section(volumename)
            str_enc_path = EncVolumeObj.enc_path
            str_mount_path = EncVolumeObj.mount_path
            # if encryption is enabled, encrypt the strings first using the master password
            if encfsgui_globals.g_Settings["encrypt"] == "true":
                if encfsgui_globals.masterkey == "":
                    # ask for masterkey
                    encfsgui_helper.getMasterKey()
                if len(encfsgui_globals.masterkey) == 32:
                    str_enc_path = encfsgui_helper.encrypt(EncVolumeObj.enc_path)
                    str_mount_path = encfsgui_helper.encrypt(EncVolumeObj.mount_path)
            config.set(volumename, 'enc_path' , str_enc_path)
            config.set(volumename, 'mount_path', str_mount_path)
            config.set(volumename, 'automount',  EncVolumeObj.automount)
            config.set(volumename, 'preventautounmount',  EncVolumeObj.preventautounmount)
            config.set(volumename, 'allowother',  EncVolumeObj.allowother)
            config.set(volumename, 'mountaslocal',  EncVolumeObj.mountaslocal)
            config.set(volumename, 'encfsmountoptions',  EncVolumeObj.encfsmountoptions)
            config.set(volumename, 'passwordsaved',  EncVolumeObj.passwordsaved)
            config.set(volumename, 'enctype', EncVolumeObj.enctype)
            config.set(volumename, 'sudo', EncVolumeObj.sudo)

        with open(encfsgui_globals.volumesfile, 'w') as configfile:
            config.write(configfile)

        self.clearMasterKeyIfNeeded()

        return
