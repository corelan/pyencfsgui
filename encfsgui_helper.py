import os
import platform
import sys
import time
import datetime
import string
import subprocess
import inspect
import traceback

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore


try:
    import base64
    import hashlib
    from Crypto import Random
    from Crypto.Cipher import AES
except:
    oops = QApplication([])
    QtWidgets.QMessageBox.critical(None,"Error loading pycrypto library","This version of pyencfsgui requires the 'pycrypto' library.\n\nPlease install using\n'python3 -m pip install pycrypto --user'\n")
    sys.exit(1)

import encfsgui_globals
from encfsgui_globals import *

import cgetmasterkey
from cgetmasterkey import CMasterKeyWindow


#################################
### METHODS, HELPER FUNCTIONS ###
#################################

def getCurDir():
    print_debug("Start %s" % inspect.stack()[0][3])
    curdir = "./"
    try:
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
        curdir = os.getcwd()
    except Exception as e:
        print_debug("Unable to determine current directory: %s" % str(e))
        pass
    return curdir

def getNow():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def getVersion():
    thisversion = ""
    versionlines = readfile("version.txt")
    for thisline in versionlines:
        if not thisline.strip() == "":
            thisversion = thisline.strip()
            break
    return thisversion

def readfile(filename):
    print_debug("Start %s" % inspect.stack()[0][3])
    print_debug("Reading %s" % filename)
    contents = []
    try:
        f = open(filename,"r")
        contents = f.readlines()
        f.close()
        print_debug("Read %d lines" % len(contents))
    except Exception as e:
        print_debug("Unable to read file %s: %s" % (filename, str(e)))
        pass
    return contents

def writefile(filename,contents):
    f = open(filename,'a')
    for l in contents:
        f.write("%s\n" % l)
    f.close()
    return

def createFile(filename):
    f = open(filename,'w+')
    f.write("# file created at %s\n" % getNow())
    f.close()
    return

def print_debug(line):
    if encfsgui_globals.debugmode:
        #try:
        #    print("%s - DEBUG : %s" % (getNow(), str(line)))
        #except Exception:
        #    print(traceback.format_exc())
        writefile(encfsgui_globals.logfile, ["%s : %s" % (getNow(), str(line)) ] )
    return

def getTmpName():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def getEncFSVersion():
    print_debug("Start %s" % inspect.stack()[0][3])
    encfsversion = ""
    oscmd = encfsgui_globals.g_Settings["encfspath"]
    cmdargs = '--version'
    cmdoutput = execOSCmd("%s %s" % (oscmd,cmdargs ))
    outputline = cmdoutput[0]
    for line in cmdoutput:
        if line.startswith("encfs "):
            outputline = line
            break
    outputparts = outputline.split(" ")
    encfsversion = outputparts[-1].replace('\n','')
    return encfsversion


def getGoCryptFSVersion():
    print_debug("Start %s" % inspect.stack()[0][3])
    gocryptfsversion = ""
    oscmd = encfsgui_globals.g_Settings["gocryptfspath"]
    cmdargs = '--version'
    cmdoutput = execOSCmd("%s %s" % (oscmd,cmdargs ))
    outputline = cmdoutput[0]
    for line in cmdoutput:
        if line.startswith("gocryptfs "):
            outputline = line
            break
    outputparts = outputline.split(";")
    gocryptfspart = outputparts[0]
    versionparts = gocryptfspart.split(" ")
    gocryptfsversion = versionparts[-1].replace('\n','')
    return gocryptfsversion


def ifExists(encfsapp="encfs"):
    print_debug("Start %s" % inspect.stack()[0][3])
    encbinfound = False
    dictkey = "%spath" % encfsapp
    if dictkey in encfsgui_globals.g_Settings:
        encbinpath = encfsgui_globals.g_Settings[dictkey]
        if os.path.exists(encbinpath):
            encbinfound = True
    return encbinfound


def getOSType():
    return platform.system()


def ismacOS():
    if "darwin" in getOSType().lower():
        return True
    else:
        return False

def isLinux():
    if "linux" in getOSType().lower():
        return True
    else:
        return False

def isWindows():
    if "windows" in getOSType().lower():
        return True
    else:
        return False

def runwhich(binarytofind):
    whichlocation = ""
    if binarytofind != "":
        cmd = ["which",binarytofind]
        cmdlines, cmdretval = execOSCmdRetVal(cmd)
        # get the first line that contains the binarytofind
        for line in cmdlines:
            if binarytofind in line:
                if os.path.exists(line.strip()):
                    whichlocation = line.strip()
                    break
    return whichlocation


def execOSCmd(cmd):
    print_debug("Start %s" % inspect.stack()[0][3])
    if not cmd.startswith("sh -c"):
        print_debug("Executing [ %s ]" % cmd)
    else:
        print_debug("Note: A part of the command below will not shown because it might contain sensitive information (password)")
        cmdparts = cmd.split("|")
        if len(cmdparts) > 1:
            print_debug("Executing [ %s ]" % cmdparts[1])
    p = subprocess.Popen('%s' % cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         shell=True)
    outputobj = iter(p.stdout.readline, b'')
    outputlines = []
    for l in outputobj:
        thisline = l.decode()
        outputlines.append(thisline.replace('\\n','').replace("'",""))
    return outputlines


def execOSCmdRetVal(cmdarray):
    print_debug("Start %s" % inspect.stack()[0][3])
    print_debug("Executing %s" % cmdarray)
    returncode = 0
    outputlines = []
    p = subprocess.run(cmdarray, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) 
    returncode = p.returncode
    outputobj = p.stdout.split('\n')
    for thisline in outputobj:
        outputlines.append(thisline.replace('\\n','').replace("'",""))
    print_debug("Return code: %s" % str(returncode))
    return outputlines, returncode


def execOScmdAsync(cmdarray):
    print_debug("Start %s" % inspect.stack()[0][3])
    print_debug("Executing %s" % cmdarray)
    p = subprocess.Popen(cmdarray) 
    #p.terminate()
    return

def openFolder(foldername):
    print_debug("Start %s" % inspect.stack()[0][3])
    if ismacOS():
        subprocess.call(["open", "-R", foldername + "/"])
    elif isLinux():
        subprocess.call(["xdg-open", foldername + "/"])
    return

def getKeyChainPassword(volumename):
    print_debug("Start %s" % inspect.stack()[0][3])
    objname = "EncFSGUI_%s" % volumename
    cmd = "sh -c \"security find-generic-password -a '%s' -s '%s' -w login.keychain\"" % (objname, objname)
    passarr = execOSCmd(cmd)
    password = str(passarr[0]).replace("\n","").strip()
    return password

def autoUpdate():
    #return values:
    # -1 = error
    # 0 = ok, no update
    # 1 = update found

    updateresult = 0    # up to date

    print_debug("Start %s" % inspect.stack()[0][3])
    cmdarr = ["git","pull"]
    gitoutput, gitretval = execOSCmdRetVal(cmdarr)

    if (encfsgui_globals.debugmode):
        print_debug("Git output:")

    if gitretval != 0:
        updateresult = -1
    else:

        updatefound = False
        for l in gitoutput:
            if (encfsgui_globals.debugmode):
                print_debug("  >> %s" % l)
            if ":" in l and not "fatal" in l and not "not staged" in l and not "hint:" in l:
                updatefound = True
                break
    
        if updatefound:
            updateresult = 1 # update found

    return updateresult, gitoutput

def getExpectScriptContents(scripttype, insertbreak = False):
    print_debug("Start %s" % inspect.stack()[0][3])
    scriptcontents = ""
    if scripttype == "encfs":
        # header
        newline = "#!/usr/bin/env expect\n"
        scriptcontents += newline

        newline = "set passwd [lindex $argv 0]\n"
        scriptcontents += newline

        newline = "set timeout 10\n"
        scriptcontents += newline

        # launch encfs
        newline = "spawn \"$ENCFSBIN\" -v \"$ENCPATH\" \"$MOUNTPATH\"\n"
        scriptcontents += newline

        # activate expert mode
        newline = "expect \"Please choose from one of the following options:\"\n"
        scriptcontents += newline
        newline = "expect \"?>\"\n"
        scriptcontents += newline
        newline = "send \"x\\n\"\n"
        scriptcontents += newline

        # set cipher algorithm
        newline = "expect \"Enter the number corresponding to your choice: \"\n"
        scriptcontents += newline
        newline = "send \"$CIPHERALGO\\n\"\n"
        scriptcontents += newline

        # select cipher keysize
        newline = "expect \"Selected key size:\"\n"
        scriptcontents += newline
        newline = "send \"$CIPHERKEYSIZE\\n\"\n"
        scriptcontents += newline

        # select filesystem block size
        newline = "expect \"filesystem block size:\"\n"
        scriptcontents += newline
        newline = "send \"$BLOCKSIZE\\n\"\n"
        scriptcontents += newline

        # select encoding algo
        newline = "expect \"Enter the number corresponding to your choice: \"\n"
        scriptcontents += newline
        newline = "send \"$ENCODINGALGO\\n\"\n"
        scriptcontents += newline

        if (insertbreak):
            newline = "break\n"
            scriptcontents += newline        

        # filename IV chaining
        newline = "expect \"Enable filename initialization vector chaining?\"\n"
        scriptcontents += newline
        newline = "send \"$IVCHAINING\\n\"\n"
        scriptcontents += newline

        # per filename IV
        newline = "expect \"Enable per-file initialization vectors?\"\n"
        scriptcontents += newline
        newline = "send \"$PERFILEIV\\n\"\n"
        scriptcontents += newline

        # file to IV header chaining can only be used when both previous options are enabled
        # which means it might slide to the next option right away
        newline = "expect {\n"
        scriptcontents += newline
        newline = "\t\"Enable filename to IV header chaining?\" {\n"
        scriptcontents += newline
        newline = "\t\tsend \"$FILETOIVHEADERCHAINING\\n\"\n"
        scriptcontents += newline
        newline = "\t\texpect \"Enable block authentication code headers\"\n"
        scriptcontents += newline
        newline = "\t\tsend \"$BLOCKAUTHCODEHEADERS\\n\"\n"
        scriptcontents += newline
        newline = "\t\t}\n"
        scriptcontents += newline
        newline = "\t\"Enable block authentication code headers\" {\n"  #space matters
        scriptcontents += newline
        newline = "\t\tsend \"$BLOCKAUTHCODEHEADERS\\n\"\n"
        scriptcontents += newline   
        newline = "\t\t}\n"
        scriptcontents += newline   
        newline = "\t}\n"
        scriptcontents += newline    

        # add random bytes to each block header
        newline = "expect \"Select a number of bytes, from 0 (no random bytes) to 8: \"\n"
        scriptcontents += newline
        newline = "send \"0\\n\"\n"
        scriptcontents += newline

        # file-hole pass-through
        newline = "expect \"Enable file-hole pass-through?\"\n"
        scriptcontents += newline
        newline = "send \"\\n\"\n"
        scriptcontents += newline        

        # password
        newline = "expect \"New Encfs Password: \"\n"
        scriptcontents += newline
        newline = "send \"$passwd\\n\"\n"
        scriptcontents += newline    

        newline = "expect \"Verify Encfs Password: \"\n"
        scriptcontents += newline
        newline = "send \"$passwd\\n\"\n"
        scriptcontents += newline    

        newline = "puts \"\\nDone.\\n\"\n"
        scriptcontents += newline

        newline = "expect \"\\n\"\n"
        scriptcontents += newline    
        
        newline = "sleep x\n"  
        scriptcontents += newline
    
    if scripttype == "gocryptfs":
        # header
        newline = "#!/usr/bin/env expect\n"
        scriptcontents += newline

        newline = "set passwd [lindex $argv 0]\n"
        scriptcontents += newline

        newline = "set timeout 10\n"
        scriptcontents += newline

        # launch encfs
        newline = "spawn \"$GOCRYPTFSBIN\" $EXTRAOPTS -init \"$ENCPATH\" \n"
        scriptcontents += newline

        # password
        newline = "expect \"Password:\"\n"
        scriptcontents += newline
        newline = "send \"$passwd\\n\"\n"
        scriptcontents += newline    

        newline = "expect \"Repeat:\"\n"
        scriptcontents += newline
        newline = "send \"$passwd\\n\"\n"
        scriptcontents += newline    

        newline = "expect \"\\n\"\n"
        scriptcontents += newline    
        
        newline = "sleep x\n"  
        scriptcontents += newline


    return scriptcontents

def determineFileNameEncodings():
    print_debug("Start %s" % inspect.stack()[0][3])
    encodings = []
    # create 2 new tmp folders
    tmpname = getTmpName()
    cwd = os.getcwd()
    tmpfolder_enc = os.path.join(cwd, tmpname+"_enc")
    tmpfolder_mnt = os.path.join(cwd, tmpname+"_mnt")
    if os.path.exists(tmpfolder_enc):
        os.removedirs(tmpfolder_enc)
    if os.path.exists(tmpfolder_mnt):
        os.removedirs(tmpfolder_mnt)
    
    os.mkdir(tmpfolder_enc)
    os.mkdir(tmpfolder_mnt)

    if os.path.exists(encfsgui_globals.g_Settings["encfspath"]):

        # try to create an encrypted volume, and parse output to determine the available fileencoding options
        # argument True is needed to insert 'break' after getting the encoding options
        scriptcontents = getExpectScriptContents("encfs",True)
        password = "boguspassword"

        # replace variables in the script
        scriptcontents = scriptcontents.replace("$ENCFSBIN", encfsgui_globals.g_Settings["encfspath"])
        scriptcontents = scriptcontents.replace("$ENCPATH", tmpfolder_enc)
        scriptcontents = scriptcontents.replace("$MOUNTPATH", tmpfolder_mnt)
        if not str(getEncFSVersion()).startswith("1.9."):
            scriptcontents = scriptcontents.replace("$CIPHERALGO", "1")
        else:
            scriptcontents = scriptcontents.replace("$CIPHERALGO", "1")
        scriptcontents = scriptcontents.replace("$CIPHERKEYSIZE", "128")
        scriptcontents = scriptcontents.replace("$BLOCKSIZE", "1024")
        scriptcontents = scriptcontents.replace("$ENCODINGALGO", "1")
        scriptcontents = scriptcontents.replace("$IVCHAINING","")
        scriptcontents = scriptcontents.replace("$PERFILEIV","")
        scriptcontents = scriptcontents.replace("$FILETOIVHEADERCHAINING","y")
        scriptcontents = scriptcontents.replace("$BLOCKAUTHCODEHEADERS","")
        scriptcontents = scriptcontents.replace("sleep x","expect eof")

        expectfilename = "expect.encfsgui"
        # write script to file
        scriptfile = open(expectfilename, 'w')
        scriptfile.write(scriptcontents)
        scriptfile.close()
        # run script file
        cmd = "expect '%s' '%s'" % (expectfilename, password)
        expectoutput = execOSCmd(cmd)
        
        # parse output
        startfound = False
        endfound = False
        rawCaps = []
        for l in expectoutput:
            #print_debug(">>> %s" % l)
            if not startfound:
                if "filename encoding algorithms" in l and "available" in l:
                    startfound = True
            else:
                if not "." in l:
                    endfound = True
                else:
                    rawCaps.append(l)
            if startfound and endfound:
                break
        
        if not startfound:
            rawCaps.clear()
            endfound = False
            # maybe encfs is in a different language, try in a different way
            for l in expectoutput:
                if not startfound:
                    if "1. Block" in l:
                        startfound = True
                        rawCaps.append(l)
                else:
                    if not "." in l:
                        endfound = True
                    else:
                        rawCaps.append(l)
                if startfound and endfound:
                    break
        
        for l in rawCaps:
            capparts = l.split(" ")
            if len(capparts) > 1:
                thisencoding = capparts[1]
                encodings.append(thisencoding)

    else:
        print_debug("No encfs binary found at %s" % encfsgui_globals.g_Settings["encfspath"])


    if len(encodings) > 0:
        encfsgui_globals.g_Encodings = encodings
    else:
        print_debug("Unable to get filename encodings")
        for l in expectoutput:
            print_debug("%s" % l)
    
    # clean up again
    os.removedirs(tmpfolder_enc)
    os.removedirs(tmpfolder_mnt)
    os.remove(expectfilename)

    return

def getMasterKey():
    print_debug("Start %s" % inspect.stack()[0][3])
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    print_debug("%s() Called from: %s()" % (inspect.stack()[0][3],calframe[1][3]))   
    print_debug("Current length of masterkey: %d" % len(encfsgui_globals.masterkey))
    if len(encfsgui_globals.masterkey) != 32:
        frmpassword = CMasterKeyWindow()
        frmpassword.setWindowTitle("Please enter master key")
        frmpassword.show()
        frmpassword.setFocus()
        frmpassword.activateWindow()
        frmpassword.exec_()
        encfsgui_globals.masterkey = str(frmpassword.getPassword())
        print_debug("New length of masterkey: %d" % len(encfsgui_globals.masterkey ))
    return

def encrypt(cleartext):
    print_debug("Start %s" % inspect.stack()[0][3])
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    print_debug("%s() Called from: %s()" % (inspect.stack()[0][3],calframe[1][3]))   
    ciphertext = ""
    encfsgui_globals.masterkey = str(encfsgui_globals.masterkey)
    #print_debug("Current length of masterkey: %d" % len(encfsgui_globals.masterkey))
    obj = AES.new(encfsgui_globals.masterkey, AES.MODE_CBC, '!IVNotSoSecret!!')
    while (len(cleartext) % 16 != 0):
        # add spaces at the end, we can remove them later
        cleartext = cleartext + " "
    ciphertext=base64.b64encode(obj.encrypt(cleartext))
    return ciphertext.decode()

def decrypt(ciphertext):
    print_debug("Start %s" % inspect.stack()[0][3])
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    print_debug("%s() Called from: %s()" % (inspect.stack()[0][3],calframe[1][3]))       
    encfsgui_globals.masterkey = str(encfsgui_globals.masterkey)
    #print_debug("Current length of masterkey: %d" % len(encfsgui_globals.masterkey))
    cleartext = ""
    #print_debug("Requested to decrypt '%s'" % ciphertext)
    #print_debug("Base64 decoded: %s" % base64.b64decode(ciphertext))
    obj = AES.new(encfsgui_globals.masterkey, AES.MODE_CBC, '!IVNotSoSecret!!')
    cleartext = obj.decrypt(base64.b64decode(ciphertext))
    #remove spaces from the end again
    cleartext = cleartext.rstrip()
    return cleartext

def makePW32(key):
    print_debug("Start %s" % inspect.stack()[0][3])
    pw = key[0:31]
    ccode = 1
    while len(pw) < 32:
        pw += chr(ccode)
        ccode += 1
    return pw

def SavePasswordInKeyChain(volumename, password):
    print_debug("Start %s" % inspect.stack()[0][3])
    cmd = "sh -c \"security add-generic-password -U -a 'EncFSGUI_%s' -s 'EncFSGUI_%s' -w '%s' login.keychain\"" % (volumename, volumename, str(password))
    print_debug(cmd)
    setpwoutput = execOSCmd(cmd)
    return

def RemovePasswordFromKeyChain(volumename):
    print_debug("Start %s" % inspect.stack()[0][3])
    cmd = "sh -c \"security delete-generic-password -a 'EncFSGUI_%s' -s 'EncFSGUI_%s' login.keychain\"" % (volumename, volumename)
    print_debug(cmd)
    setpwoutput = execOSCmd(cmd)
    return      