# globals and global classes
global g_Volumes
global g_Settings
global g_Encodings
global g_CurrentlySelected
global appconfig
global debugmode
global settingsfile
global volumesfile
global logfile
global app
global masterkey
global ishidden
global timeswrong

volumesfile = "encfsgui.volumes"
logfile = "encfsgui.log"
debugmode = False
g_Encodings = []
ishidden = False
timeswrong = 0

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
        self.mountaslocal = 0
        self.ismounted = False
        self.enc_path_exists = True
        self.enctype = "encfs"
        self.sudo = 0
        self.errormessage = ""
    