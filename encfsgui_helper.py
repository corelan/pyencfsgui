import os
import sys
import time
import datetime
import string
import subprocess

import encfsgui_globals
from encfsgui_globals import *
#################################
### METHODS, HELPER FUNCTIONS ###
#################################


def getNow():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def readfile(filename):
    #print_debug("Reading %s" % filename)
    contents = []
    f = open(filename,"r")
    contents = f.readlines()
    f.close()
    #print_debug("Read %d lines" % len(contents))
    return contents

def writefile(filename,contents):
    #print_debug("Creating %s" % filename)
    f = open(filename,'w')
    for l in contents:
        f.write("%s\n" % l)
    f.close()
    #print_debug("File created, wrote %d lines" % len(contents))
    return

def print_debug(line):
    if encfsgui_globals.debugmode:
        print("%s - DEBUG : %s" % (getNow(), line))
    return

def getEncFSVersion(g_Settings):
    encfsversion = ""
    oscmd = g_Settings["encfspath"]
    cmdargs = '--version'
    cmdoutput = execOSCmd("%s %s" % (oscmd,cmdargs ))
    #print_debug(cmdoutput)
    outputline = cmdoutput[0]
    outputparts = outputline.split(" ")
    encfsversion = outputparts[-1].replace('\n','')
    return encfsversion

def execOSCmd(cmd):
    #print_debug("Executing '%s'" % cmd)
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

def openFolder(foldername):
    subprocess.call(["open", "-R", foldername + "/"])
    return

def getKeyChainPassword(volumename):
    objname = "EncFSGUI_%s" % volumename
    cmd = "sh -c \"security find-generic-password -a '%s' -s '%s' -w login.keychain\"" % (objname, objname)
    passarr = execOSCmd(cmd)
    password = str(passarr[0]).replace("\n","").strip()
    return password
