# globals and global classes
global g_Volumes
global g_Settings
global g_CurrentlySelected
global appconfig
global debugmode
global settingsfile
global volumesfile
global logfile

volumesfile = "encfsgui.volumes"
logfile = "encfsgui.log"
debugmode = False

class CEncryptedVolume:
    def __init__(self):
        #self.volumename = ""
        self.enc_path = ""
        self.mount_path = ""
        self.passwordsaved = 0
        self.encfsmountoptions = ""
        self.automount = 0
        self.preventautounmount = 0
        self.allowother = 0
        self.mountaslocal=0
        self.ismounted = False
    