import os
import sys
import time
import datetime
import string
import subprocess
import inspect
import traceback

import encfsgui_globals
from encfsgui_globals import *

#################################
### METHODS, HELPER FUNCTIONS ###
#################################


def getNow():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def readfile(filename):
    print_debug("Start %s" % inspect.stack()[0][3])
    print_debug("Reading %s" % filename)
    contents = []
    f = open(filename,"r")
    contents = f.readlines()
    f.close()
    print_debug("Read %d lines" % len(contents))
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
    outputparts = outputline.split(" ")
    encfsversion = outputparts[-1].replace('\n','')
    return encfsversion

def execOSCmd(cmd):
    print_debug("Start %s" % inspect.stack()[0][3])
    if not cmd.startswith("sh -c"):
        print_debug("Executing '%s'" % cmd)
    else:
        print_debug("Note: A part of the command below will not shown because it might contain sensitive information (password)")
        cmdparts = cmd.split("|")
        if len(cmdparts) > 1:
            print_debug("Executing '%s'" % cmdparts[1])
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


def execOScmdAsync(cmdarray):
    print_debug("Start %s" % inspect.stack()[0][3])
    print_debug("Executing %s" % cmdarray)
    p = subprocess.Popen(cmdarray) 
    #p.terminate()
    return

def openFolder(foldername):
    print_debug("Start %s" % inspect.stack()[0][3])
    subprocess.call(["open", "-R", foldername + "/"])
    return

def getKeyChainPassword(volumename):
    print_debug("Start %s" % inspect.stack()[0][3])
    objname = "EncFSGUI_%s" % volumename
    cmd = "sh -c \"security find-generic-password -a '%s' -s '%s' -w login.keychain\"" % (objname, objname)
    passarr = execOSCmd(cmd)
    password = str(passarr[0]).replace("\n","").strip()
    return password

def autoUpdate():
    updateresult = 0    # up to date
    print_debug("Start %s" % inspect.stack()[0][3])
    cmd = "git pull"
    gitoutput = execOSCmd(cmd)
    if (encfsgui_globals.debugmode):
        print_debug("Git output:")
    updatefound = False
    for l in gitoutput:
        if (encfsgui_globals.debugmode):
            print_debug("  >> %s" % l)
        if ":" in l:
            updatefound = True
            break
    
    if updatefound:
        updateresult = 1 # update found
    return updateresult

def determineFileNameEncodings():
    print_debug("Start %s" % inspect.stack()[0][3])
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

    # try to create an encrypted volume, and parse output to determine the available fileencoding options
    # argument True is needed to insert 'break' after getting the encoding options
    scriptcontents = getExpectScriptContents(True)
    password = "boguspassword"

    # replace variables in the script
    scriptcontents = scriptcontents.replace("$ENCFSBIN", encfsgui_globals.g_Settings["encfspath"])
    scriptcontents = scriptcontents.replace("$ENCPATH", tmpfolder_enc)
    scriptcontents = scriptcontents.replace("$MOUNTPATH", tmpfolder_mnt)
    if getEncFSVersion().startswith("1.9."):
        scriptcontents = scriptcontents.replace("$CIPHERALGO", "AES")
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
    
    encodings = []

    for l in rawCaps:
        capparts = l.split(" ")
        if len(capparts) > 1:
            thisencoding = capparts[1]
            encodings.append(thisencoding)

    encfsgui_globals.g_Encodings = encodings
    # clean up again

    os.removedirs(tmpfolder_enc)
    os.removedirs(tmpfolder_mnt)
    os.remove(expectfilename)
    return


def getExpectScriptContents(insertbreak = False):
    print_debug("Start %s" % inspect.stack()[0][3])
    scriptcontents = ""
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
    
    return scriptcontents