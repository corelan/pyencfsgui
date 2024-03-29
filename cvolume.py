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
from PyQt5 import QtCore

import encfsgui_globals
from encfsgui_globals import *

import encfsgui_helper
from encfsgui_helper import *

class CVolumeWindow(QtWidgets.QDialog):
    def __init__(self):
        encfsgui_helper.print_debug("Start CVolumeWindow %s" % inspect.stack()[0][3])
        super(CVolumeWindow, self).__init__()
        uic.loadUi('encfsgui_volume.ui', self)

        # disable/remove buttons
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        # 0 = create
        # 1 = add
        # 2 = edit
        self.runmode = 0    # create

        self.origvolumename = ""

        self.encfsfolderbutton = self.findChild(QtWidgets.QPushButton, 'btn_selectencfsfolder')
        self.encfsfolderbutton.clicked.connect(self.SelectEncfsFolderClicked)

        self.mountfolderbutton = self.findChild(QtWidgets.QPushButton, 'btn_selectmountfolder')
        self.mountfolderbutton.clicked.connect(self.SelectMountFolderClicked)   

        self.txt_encfsfolder = self.findChild(QtWidgets.QLineEdit, 'txt_encfsfolder')
        self.txt_mountfolder = self.findChild(QtWidgets.QLineEdit, 'txt_mountfolder')    
        self.txt_volumename = self.findChild(QtWidgets.QLineEdit, 'txt_volumename')   
        self.txt_password = self.findChild(QtWidgets.QLineEdit, 'txt_password')
        self.txt_password2 = self.findChild(QtWidgets.QLineEdit, 'txt_password2')
        self.txt_encfsmountoptions = self.findChild(QtWidgets.QLineEdit, 'txt_encfsmountoptions')

        self.chk_saveinkeychain = self.findChild(QtWidgets.QCheckBox, 'chk_saveinkeychain')
        self.chk_mountaslocal = self.findChild(QtWidgets.QCheckBox, 'chk_mountaslocal')
        self.chk_usesudo = self.findChild(QtWidgets.QCheckBox, 'chk_usesudo')
        self.chk_automount = self.findChild(QtWidgets.QCheckBox, 'chk_automount')
        self.chk_preventautounmount = self.findChild(QtWidgets.QCheckBox, 'chk_preventautounmount')
        self.chk_accesstoother = self.findChild(QtWidgets.QCheckBox, 'chk_accesstoother')

        self.savebutton = self.findChild(QtWidgets.QPushButton, 'btn_save')
        self.savebutton.clicked.connect(self.SaveButtonClicked)

        self.cancelbutton = self.findChild(QtWidgets.QPushButton, 'btn_cancel')
        self.cancelbutton.clicked.connect(self.CancelButtonClicked)

        self.radio_volumetype_gocryptfs = self.findChild(QtWidgets.QRadioButton, 'radio_type_gocryptfs')
        self.radio_volumetype_gocryptfs.clicked.connect(self.SelectVolumeTypeGoCryptFS)

        self.radio_volumetype_encfs = self.findChild(QtWidgets.QRadioButton, 'radio_type_encfs')
        self.radio_volumetype_encfs.clicked.connect(self.SelectVolumeTypeEncFS)
        
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

        self.grp_volumetypes = self.findChild(QtWidgets.QGroupBox, 'grp_volumetypes')
        self.grp_encfsoptions = self.findChild(QtWidgets.QGroupBox, 'grp_encfsoptions')
        self.grp_gocryptfsoptions = self.findChild(QtWidgets.QGroupBox, 'grp_gocryptfsoptions')

        self.tab_volumetypes = self.findChild(QtWidgets.QTabWidget, 'tab_volumetypes')
        self.tab_encfs_options = self.findChild(QtWidgets.QWidget, 'tab_encfs_options')
        self.tab_gocryptfs_options = self.findChild(QtWidgets.QWidget, 'tab_gocryptfs_options')

        self.chk_gocryptfs_plaintext = self.findChild(QtWidgets.QCheckBox, 'chk_gocryptfs_plaintext')
        self.chk_gocryptfs_aessiv = self.findChild(QtWidgets.QCheckBox, 'chk_gocryptfs_aessiv')

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
        for encodingtype in encfsgui_globals.g_Encodings:
            self.filenameencodingcombo.addItem(encodingtype)

        self.SelectProfileBalanced()
        # default to GoCryptFS
        self.SelectVolumeTypeGoCryptFS()


    def SelectEncfsFolderClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        folderName = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", self.txt_encfsfolder.displayText(), QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks))
        if folderName:
            self.txt_encfsfolder.setText("%s" % folderName)
        return

    def SelectMountFolderClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        folderName = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", self.txt_mountfolder.displayText(), QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks))
        if folderName:
            self.txt_mountfolder.setText("%s" % folderName)
        return

    def SelectVolumeTypeEncFS(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        #disable the GoCryptFS tab
        if self.runmode == 0:
            self.grp_encfsoptions.setEnabled(True)
            self.grp_gocryptfsoptions.setEnabled(False)
            #set EncFS tab in focus     
            self.tab_encfs_options.setEnabled(True)
            self.tab_gocryptfs_options.setEnabled(False)
            self.tab_volumetypes.setCurrentWidget(self.tab_encfs_options)  
            self.tab_encfs_options.show()
        #self.chk_mountaslocal.setEnabled(True)

        return

    def SelectVolumeTypeGoCryptFS(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        #disable the EncfS tab
        if self.runmode == 0:
            self.grp_encfsoptions.setEnabled(False)
            self.grp_gocryptfsoptions.setEnabled(True) 
            #set GoCryptFS tab in focus
            self.tab_encfs_options.setEnabled(False)
            self.tab_gocryptfs_options.setEnabled(True)
            self.tab_volumetypes.setCurrentWidget(self.tab_gocryptfs_options)  
            self.tab_gocryptfs_options.show()
        #self.chk_mountaslocal.setEnabled(False)
        return

    def SelectProfileCustom(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
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
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        # sanity check
        newvolumename = str(self.txt_volumename.displayText()).strip()
        errorfound = False

        if (self.txt_volumename.text().replace(" ","") == ""):
            errorfound = True
            QtWidgets.QMessageBox.warning(None,"Error checking volume name","Volume name cannot be empty.\n Please enter a unique volume name."  )

        if (self.txt_encfsfolder.text().replace(" ","") == ""):
            errorfound = True
            QtWidgets.QMessageBox.warning(None,"Error checking encfs/gocryptfs folder path","Please select a valid encfs/gocryptfs folder."  )
        else:
             if (self.runmode == 0):
                # encfs folder must be empty
                if (os.listdir(self.txt_encfsfolder.text())):
                    QtWidgets.QMessageBox.warning(None,"Error checking encfs/gocryptfs folder","Please make sure the new encfs/gocryptfs folder is empty at this point."  )
                    errorfound = True
            
        if (self.txt_mountfolder.text().replace(" ","") == ""):
            errorfound = True
            QtWidgets.QMessageBox.warning(None,"Error checking volume name","Please select a valid mount folder"  )
        else:
             if (self.runmode == 0):
                # encfs folder must be empty
                if (os.listdir(self.txt_mountfolder.text())):
                    QtWidgets.QMessageBox.warning(None,"Error checking mount folder","Please make sure the mount folder is empty at this point."  )
                    errorfound = True            

        # runmode 0 = create
        # runmode 1 = add
        # runmode 2 = edit
        if (self.runmode == 0) or (self.runmode == 1):
            if (newvolumename in encfsgui_globals.g_Volumes):
                errorfound = True
                QtWidgets.QMessageBox.warning(None,"Error checking volume name","Volume name '%s' already exists.\n Please choose a unique volume name." % newvolumename )
        
        if (self.runmode == 2):
            if (newvolumename != self.origvolumename):
                if (newvolumename in encfsgui_globals.g_Volumes):
                    errorfound = True
                    QtWidgets.QMessageBox.warning(None,"Error checking volume name","Volume name '%s' already exists.\n Please choose a unique volume name." % newvolumename )
                else:
                    print_debug("Volume '%s' will be renamed to '%s'" % (self.origvolumename, newvolumename))
                
                if self.chk_saveinkeychain.isChecked() and (self.txt_password.text() == "" or self.txt_password2.text() == ""):
                    errorfound = True
                    QtWidgets.QMessageBox.warning(None,"Re-enter password","You are trying to rename a volume that had its password saved in keychain.\n\nPlease enter the password again, or disable saving the password in keychain.\n\n" ) 

        if (self.chk_saveinkeychain.isChecked() or self.runmode == 0):
            if (self.txt_password.text() != self.txt_password2.text()):
                errorfound = True
                QtWidgets.QMessageBox.warning(None,"Password error","Both passwords do not match" )

            if not self.chk_saveinkeychain.isChecked() and not self.runmode == 2:
                # in edit mode, we can allow empty passwords, providing that password has been saved in keychain already
                if (self.txt_password.text() == "" or self.txt_password2.text() == ""):
                    errorfound = True
                    QtWidgets.QMessageBox.warning(None,"Password error","Password cannot be empty" )

            if ("'" in self.txt_password.text()):
                errorfound = True
                QtWidgets.QMessageBox.warning(None,"Password error","Sorry, you're not allowed to use the 'single-tick' character (') in the password" )

            if ("!" in self.txt_password.text()):
                errorfound = True
                QtWidgets.QMessageBox.warning(None,"Password error","Sorry, you're not allowed to use the 'exclamation mark' character (!) in the password" )


        if not errorfound:
        
            # save everything
            # translate options into object
            EncVolumeObj = encfsgui_globals.CEncryptedVolume()
            EncVolumeObj.enc_path = str(self.txt_encfsfolder.displayText()).strip()
            EncVolumeObj.mount_path = str(self.txt_mountfolder.displayText()).strip()
            EncVolumeObj.encfsmountoptions = str(self.txt_encfsmountoptions.displayText()).strip()

            if (self.radio_volumetype_gocryptfs.isChecked()):
                EncVolumeObj.enctype = "gocryptfs"
            if (self.radio_volumetype_encfs.isChecked()):
                EncVolumeObj.enctype = "encfs"

            if (self.chk_mountaslocal.isChecked()):
                EncVolumeObj.mountaslocal = "1"
            else:
                EncVolumeObj.mountaslocal = "0"

            if (self.chk_saveinkeychain.isChecked()):
                EncVolumeObj.passwordsaved = "1"
            else:
                EncVolumeObj.passwordsaved = "0"

            if (self.chk_automount.isChecked()):
                EncVolumeObj.automount = "1"
            else:
                EncVolumeObj.automount = "0"

            if (self.chk_preventautounmount.isChecked()):
                EncVolumeObj.preventautounmount = "1"
            else:
                EncVolumeObj.preventautounmount = "0"

            if (self.chk_accesstoother.isChecked()):
                EncVolumeObj.allowother = "1"
            else:
                EncVolumeObj.allowother = "0"

            if (self.chk_usesudo.isChecked()):
                EncVolumeObj.sudo = "1"
            else:
                EncVolumeObj.sudo = "0"

            # in create mode, first create the actual encrypted folder
            # and then add it to the config 

            if (self.runmode == 0):
                if (self.CreateNewEncryptedVolume()):
                    encfsgui_globals.appconfig.addVolume(newvolumename, EncVolumeObj)

            # add mode
            if (self.runmode == 1):
                encfsgui_globals.appconfig.addVolume(newvolumename, EncVolumeObj)
            
            # in edit mode, remove previous volume from volume list
            # and add new one
            if (self.runmode == 2):
                encfsgui_globals.appconfig.delVolume(self.origvolumename)
                # only remove password if a new is set, to avoid that a simple edit would clear the saved password
                if self.chk_saveinkeychain.isChecked() and not self.txt_password.text() == "" and not self.txt_password2 == "":
                    encfsgui_helper.RemovePasswordFromKeyChain(self.origvolumename)

                encfsgui_globals.appconfig.addVolume(newvolumename, EncVolumeObj)

            # remove old password
            if not self.chk_saveinkeychain.isChecked():
                encfsgui_helper.RemovePasswordFromKeyChain(newvolumename)
            # save new password
            if (self.chk_saveinkeychain.isChecked() and self.txt_password.text() != ""):
                encfsgui_helper.RemovePasswordFromKeyChain(newvolumename)
                encfsgui_helper.SavePasswordInKeyChain(newvolumename, self.txt_password.text())
            # and close the dialog
            self.close()
        return


    def CancelButtonClicked(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.close()
        return

    def CreateNewEncryptedVolume(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle("Are you sure?")
        msgboxtext = ""
        if self.radio_volumetype_encfs.isChecked():
            msgboxtext = "Are you sure you would like to create a new encfs volume '%s' at '%s' ?" % (self.txt_volumename.text(), self.txt_encfsfolder.text())
        if self.radio_volumetype_gocryptfs.isChecked():
            msgboxtext = "Are you sure you would like to create a new gocryptfs volume '%s' at '%s' ?" % (self.txt_volumename.text(), self.txt_encfsfolder.text())

        msgBox.setText(msgboxtext)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.No)
        msgBox.addButton(QtWidgets.QMessageBox.Yes)
        msgBox.show()

        encfolderfound = False

        if (msgBox.exec_() == QtWidgets.QMessageBox.Yes):

            # encfs

            if self.radio_volumetype_encfs.isChecked():            

                cipheralgos = {}
                cipheralgos["AES"] = 1
                cipheralgos["Blowfish"] = 2
                cipheralgos["Camilla"] = 3

                encfsversion = encfsgui_helper.getEncFSVersion() 
                selectedalgo = 1
                if not encfsversion.startswith("1.9."):
                    # number selection
                    selectedalgo = str(cipheralgos[self.ciphercombo.currentText()])
                else:
                    # selectedalgo = "%s" % self.ciphercombo.currentText()
                    selectedalgo = str(cipheralgos[self.ciphercombo.currentText()])
                
                fileencodings = {}
                encodingindex = 1
                selectedfileencoding = ""
                for encodingtype in encfsgui_globals.g_Encodings:
                    fileencodings[encodingtype] = encodingindex
                    encodingindex += 1
                encfsgui_helper.print_debug("File encodings: %s" % fileencodings)
                if not encfsversion.startswith("1.9."):
                    # number selection
                    selectedfileencoding = str(fileencodings[self.filenameencodingcombo.currentText()])
                else:
                    selectedfileencoding = str(fileencodings[self.filenameencodingcombo.currentText()])
                    #selectedfileencoding = "%s" % self.filenameencodingcombo.currentText()
                encfsgui_helper.print_debug("Encoding selected: %s" % selectedfileencoding)

                # create expect script
                scriptcontents = encfsgui_helper.getExpectScriptContents("encfs", False)
                # replace variables in the script
                scriptcontents = scriptcontents.replace("$ENCFSBIN", encfsgui_globals.g_Settings["encfspath"])
                scriptcontents = scriptcontents.replace("$ENCPATH", self.txt_encfsfolder.text())
                scriptcontents = scriptcontents.replace("$MOUNTPATH", self.txt_mountfolder.text())
                scriptcontents = scriptcontents.replace("$CIPHERALGO", selectedalgo)
                scriptcontents = scriptcontents.replace("$CIPHERKEYSIZE", self.keysizecombo.currentText())
                scriptcontents = scriptcontents.replace("$BLOCKSIZE", self.blocksizecombo.currentText())
                scriptcontents = scriptcontents.replace("$ENCODINGALGO", selectedfileencoding)

                if (self.chk_chainediv.isChecked()):
                    scriptcontents = scriptcontents.replace("$IVCHAINING","")
                else:
                    scriptcontents = scriptcontents.replace("$IVCHAINING","n")

                if (self.chk_perfileuniqueiv.isChecked()):
                    scriptcontents = scriptcontents.replace("$PERFILEIV","")
                else:
                    scriptcontents = scriptcontents.replace("$PERFILEIV","n")

                if (self.chk_externaliv.isChecked()):
                    scriptcontents = scriptcontents.replace("$FILETOIVHEADERCHAINING","y")
                else:
                    scriptcontents = scriptcontents.replace("$FILETOIVHEADERCHAINING","")   # n is default here
                
                if (self.chk_perblockhmac.isChecked()):
                    scriptcontents = scriptcontents.replace("$BLOCKAUTHCODEHEADERS","y")
                else:
                    scriptcontents = scriptcontents.replace("$BLOCKAUTHCODEHEADERS","")  # n is default here

                scriptcontents = scriptcontents.replace("sleep x","expect eof")

                expectfilename = "expect.encfsgui"
                # write script to file
                scriptfile = open(expectfilename, 'w')
                scriptfile.write(scriptcontents)
                scriptfile.close()
                # run script file
                cmdarray = ["expect",expectfilename, self.txt_password.text(), ">/dev/null"]
                encfsgui_helper.execOScmdAsync(cmdarray)
                self.setEnabled(False)
                time.sleep(3)
                encfolderfound = False
                secondswaited = 1
                while not encfolderfound:
                    if (os.path.exists( self.txt_encfsfolder.text() + "/.encfs6.xml" )):
                        encfolderfound = True
                    else:
                        time.sleep(1)
                        secondswaited += 1
                    if (secondswaited > 10):
                        break
                self.setEnabled(True)

                # unmount new volume
                cmd = "%s '%s'" % (encfsgui_globals.g_Settings["umountpath"], self.txt_mountfolder.text())
                encfsgui_helper.execOSCmd(cmd)
                
                if encfolderfound:
                    QtWidgets.QMessageBox.information(None,"EncFS volume created successfully","EncFS volume was created successfully")
                    #delete script file again
                    os.remove(expectfilename)  
                else:
                    QtWidgets.QMessageBox.information(None,"Error creating volume","Error while creating EncFS volume")
                    # keep the expect file for debugging purposes in case debug mode is active
                    if not encfsgui_globals.debugmode:
                        os.remove(expectfilename)
            
            # gocryptfs

            if self.radio_volumetype_gocryptfs.isChecked():            

                # create expect script

                extra_opts = ""
                if self.chk_gocryptfs_plaintext.isChecked():
                    extra_opts += "-plaintextnames "
                if self.chk_gocryptfs_aessiv.isChecked():
                    extra_opts += "-aessiv "


                scriptcontents = encfsgui_helper.getExpectScriptContents("gocryptfs", False)
                # replace variables in the script
                scriptcontents = scriptcontents.replace("$GOCRYPTFSBIN", encfsgui_globals.g_Settings["gocryptfspath"])
                scriptcontents = scriptcontents.replace("$ENCPATH", self.txt_encfsfolder.text())
                scriptcontents = scriptcontents.replace("$MOUNTPATH", self.txt_mountfolder.text())
                scriptcontents = scriptcontents.replace("$EXTRAOPTS", extra_opts)

                scriptcontents = scriptcontents.replace("sleep x","expect eof")

                expectfilename = "expect.encfsgui"
                # write script to file
                scriptfile = open(expectfilename, 'w')
                scriptfile.write(scriptcontents)
                scriptfile.close()
                # run script file
                cmdarray = ["expect",expectfilename, self.txt_password.text(), ">/dev/null"]
                #QtWidgets.QMessageBox.information(None,"expect script ready","expect script ready")
                
                #encfsgui_helper.execOScmdAsync(cmdarray)
                gocryptfslines, retval = encfsgui_helper.execOSCmdRetVal(cmdarray)
                
                self.setEnabled(False)
                time.sleep(3)
                encfolderfound = False
                secondswaited = 1
                while not encfolderfound:
                    if (os.path.exists( self.txt_encfsfolder.text() + "/gocryptfs.diriv" ) or os.path.exists( self.txt_encfsfolder.text() + "/gocryptfs.conf" )):
                        encfolderfound = True
                    else:
                        time.sleep(1)
                        secondswaited += 1
                    if (secondswaited > 10):
                        break
                self.setEnabled(True)
                
                if encfolderfound:
                    QtWidgets.QMessageBox.information(None,"GoCryptFS volume created successfully","GoCryptFS volume was created successfully")
                    masterkeyinfo = ""
                    takenote = False
                    for line in gocryptfslines:
                        if "Your master key" in line:
                            takenote = True
                        if takenote:
                            if "-" in line:
                                masterkeyinfo += "%s\n" % str(line.replace(" ","").replace("[2m","").replace("[0m","").replace("\x1b",""))
                    QtWidgets.QMessageBox.information(None,"Your master key","WARNING! This is the only time when you get to see your master key!\n\nYour master key is:\n\n%s\n\nPrint it to a piece of paper and store it in a safe location.\n" % masterkeyinfo)                          
                    #delete script file again
                    os.remove(expectfilename)  
                else:
                    QtWidgets.QMessageBox.information(None,"Error creating volume","Error while creating GoCryptFS volume")
                    # keep the expect file for debugging purposes in case debug mode is active
                    if not encfsgui_globals.debugmode:
                        os.remove(expectfilename)
                        
        return encfolderfound


    def setRunMode(self, mode):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        self.runmode = mode
        self.lbl_encfsfolder = self.findChild(QtWidgets.QLabel,'lbl_encfsfolder')

        if mode == 0:
            self.setWindowTitle("Create a new encfs/gocryptfs volume")
            self.lbl_encfsfolder.setText("Location of new (empty) encfs/gocryptfs folder:")
            self.savebutton.setText("Create")
            self.grp_encfsoptions.setEnabled(True)
            self.grp_gocryptfsoptions.setEnabled(True)
            self.tab_volumetypes.setEnabled(True)

        if mode == 1:
            self.setWindowTitle("Open/Add an existing encfs/gocryptfs volume")
            self.lbl_encfsfolder.setText("Location of existing encfs/gocryptfs folder:")
            self.savebutton.setText("Add")
            self.grp_encfsoptions.setEnabled(False)
            self.grp_gocryptfsoptions.setEnabled(False)
            self.tab_volumetypes.setEnabled(False)

        if mode == 2:
            self.setWindowTitle("Edit an encfs/gocryptfs volume")
            self.lbl_encfsfolder.setText("Location of existing encfs/gocryptfs folder:")
            self.savebutton.setText("Save")
            self.grp_encfsoptions.setEnabled(False)
            self.grp_gocryptfsoptions.setEnabled(False)
            self.grp_volumetypes.setEnabled(False)

        #unsupported 
        if encfsgui_helper.isLinux():
            self.chk_mountaslocal.setEnabled(False)
            self.chk_mountaslocal.setChecked(False)

        if encfsgui_helper.isWindows():
            self.chk_usesudo.setEnabled(False)
            self.chk_usesudo.setChecked(False)

        return

    def getRunMode(self):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        encfsgui_helper.print_debug("mode: %d" % self.runmode)
        return


    def PopulateFields(self, volumename):
        encfsgui_helper.print_debug("Start %s" % inspect.stack()[0][3])
        if volumename in encfsgui_globals.g_Volumes:
            EncVolumeObj = encfsgui_globals.g_Volumes[volumename]
            self.txt_volumename.setText(volumename)
            self.txt_encfsfolder.setText(EncVolumeObj.enc_path)
            self.txt_mountfolder.setText(EncVolumeObj.mount_path)
            self.txt_encfsmountoptions.setText(EncVolumeObj.encfsmountoptions)
            self.chk_mountaslocal.setChecked(False)
            self.chk_automount.setChecked(False)
            self.chk_preventautounmount.setChecked(False)
            self.chk_accesstoother.setChecked(False)
            self.chk_saveinkeychain.setChecked(False)

            if str(EncVolumeObj.mountaslocal) == "1":
                self.chk_mountaslocal.setChecked(True)
            if str(EncVolumeObj.automount) == "1":
                self.chk_automount.setChecked(True)
            if str(EncVolumeObj.preventautounmount) == "1":
                self.chk_preventautounmount.setChecked(True)
            if str(EncVolumeObj.allowother) == "1":
                self.chk_accesstoother.setChecked(True)
            if str(EncVolumeObj.passwordsaved) == "1":
                self.chk_saveinkeychain.setChecked(True)
            if str(EncVolumeObj.sudo) == "1":
                self.chk_usesudo.setChecked(True)                
            if str(EncVolumeObj.enctype) == "encfs":
                self.radio_volumetype_encfs.setChecked(True)
                self.tab_volumetypes.setCurrentWidget(self.tab_encfs_options)  
                self.chk_mountaslocal.setEnabled(True)       
            if str(EncVolumeObj.enctype) == "gocryptfs":
                self.radio_volumetype_gocryptfs.setChecked(True)
                self.tab_volumetypes.setCurrentWidget(self.tab_gocryptfs_options)
                #self.chk_mountaslocal.setEnabled(False)

        # overrule, unsupported features
        if encfsgui_helper.isLinux():
            self.chk_mountaslocal.setEnabled(False)
            self.chk_mountaslocal.setChecked(False)

        if encfsgui_helper.isWindows():
            self.chk_usesudo.setEnabled(False)
            self.chk_usesudo.setChecked(False)

        return
