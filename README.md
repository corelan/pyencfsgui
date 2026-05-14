# pyencfsgui

## What is pyencfsgui?

pyencfsgui is a Qt based GUI/wrapper around EncFS (`encfs`, `encfsctl`) and GoCryptFS (`gocryptfs`), `mount` and `umount`. 
It is written in python3, and relies on `encfs`/`gocryptfs` to be able to mount an enrypted folder. (These utilities typically rely on OSXFuse/MacFuse/...Fuse to provide a filesystem.)<br>
In other words, pyencfsgui simply provides a GUI that uses the aformentioned utilities in the backend, and relies on the ability to launch these binaries, to interact with them and to capture & parse the output from those tools.<br>
As a result, the EncFSGui source code is pretty easy to understand, as it does not contain any crypto or other black magic to do its job.  The downside is that it is a wrapper and may break if tools start behaving in a different way.<br>

pyencfsgui was developed on macOS using encfs versions 1.8.x and 1.9.x., and gocryptfs version 1.8.x <br>

pyencfsgui was tested on recent version of macOS and Kali Linux<br>

## Dependencies

In order for pyencfsgui to be able to function, you need to install the following dependencies:

- python3 (3.9.x or higher, tested with newer Python 3 releases as well)
- python3 libraries: PyQt5, and either `pycrypto` or a maintained replacement such as `pycryptodome`

Of course, as pyencfsgui relies on encfs and/or gocryptfs, those utilities need to be installed as well.
- encfs (1.9.x) and/or gocryptfs (1.8.x)

On macOS, you'll also need to install:
- Developer Command Line Tools
- OSXFuse/macFuse (depending on what encfs/gocryptfs needs)

Kali Linux already has most dependencies installed. If you're using a different distro, you may have to install some utilities as needed.
(If you're using xfce as Desktop Manager, you may want to install & run something like `plank` to see application icons at the bottom of your screen)

### Note: April 16 2021 - encfs/gocryptfs brew recipe issues

It appears that the brew recipes for encfs and gocryptfs are currently disabled

https://github.com/Homebrew/discussions/discussions/1250
https://github.com/vgough/encfs/issues/629
https://github.com/vgough/encfs/issues/630

The homebrew-based procedure below used to work fine until a few days ago. If you prefer to use Homebrew, you'll have to wait until someone addresses the issues.
If you already have encfs/gocryptfs installed and working, then you can skip those parts of the installation procedure below.

Of course, you can also try to install encfs via MacPorts. You may have to compile gocryptfs yourself.


### Installing dependencies on macOS

#### 1. Install Homebrew / MacPorts

If you'd like to use Homebrew:

  ```
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  sudo chown -R $(whoami) /usr/local/lib/pkgconfig
  brew doctor
  ```

If you prefer to use MacPorts instead, check installation instructions at  https://www.macports.org/install.php


#### 2. Install OSXFuse/MacFuse

  Download the latest dmg installer image from https://osxfuse.github.io/ and run the installer.

  If you're running a macOS version that doesn't have a working OSXFuse installer (yet), you can also try to install osxfuse using brew:

  ```
  brew tap homebrew/cask
  brew install --cask osxfuse
  ```
  
Next,

- Make sure to enable the kernel extension in System Preferences → Security & Privacy → General  if/as requested
- Reboot for osxfuse to work correctly.

Note: on recent Mac devices (with M1 processor) running Big Sur or later, you may have to allow Kernel Extensions using the Startup Security Utility:

- Shutdown 
- Press & hold Touch ID & power button.  Boot into recovery mode
- Launch Startup Security Utility
- Allow third party "kernel extensions" by changing the "Security Policy" to "Reduced Security"


#### 3. Install encfs / gocryptfs 

##### 3.1 Encfs

If you're using Homebrew:
  ```
  brew update
  ``` 

  Check if everything is ok and install encfs

  ```
  brew doctor
  brew install encfs
  ```

  Check if encfs works:
  ```
  encfs    
  ```

If you're using MacPorts:

  ```
  sudo port selfupdate
  sudo port install encfs
  ```

  Check if encfs works:
  ```
  encfs    
  ```

##### 3.2 GoCryptFS

Homebrew:
  ```
  brew update
  ``` 

  Check if everything is ok and install encfs

  ```
  brew doctor
  brew install gocryptfs
  ```

  Check if encfs works:
  ```
  gocryptfs    
  ```

On a M1 Mac, check out this Github issue for instructions on how to compile gocryptfs: https://github.com/rfjakob/gocryptfs/issues/556#issuecomment-845810085 


#### 4. Install python3

Homebrew:
  ```
  brew install python3
  ```
  (Make sure you're running a recent version of python3. Version 3.14.x or higher should work)


#### 5. Create a virtual environment and install Python dependencies

pyencfsgui now ships with a launcher script that creates and uses a local virtual environment automatically.
The virtual environment folder is named `pyencfsgui`.

You can still install the dependencies manually if you prefer:

  ```
  python3 -m venv pyencfsgui
  ./pyencfsgui/bin/python -m pip install --upgrade pip
  ./pyencfsgui/bin/python -m pip install -r requirements.txt
  ```

Note: On my 2020 MacBook Air (M1 processor), I had to install PyQT5 using the following command instead:

Homebrew:
  ```
  brew install PyQt5
  ```

#### 6. Install macOS Developer Command Line Tools:

  ```
  xcode-select --install
  ```

#### 7. Crypto library notes

The original project used `pycrypto`. That package is no longer maintained and typically does not work on newer Python releases.

Recommended:

  ```
  ./pyencfsgui/bin/python -m pip install pycryptodome
  ```

If you are running an older Python version and still want the legacy dependency, the code will also work with the old `pycrypto` package as long as it installs successfully in your environment.

#### 8. Jura font

Download & install the Jura font from here: https://fontsov.com/font/juraregular.html




### Installing dependencies on Linux (tested on Kali)

On Kali Linux, some dependencies may already be present, but using the local virtual environment is still recommended.

#### 1. Jura font

  ```
  sudo apt install fonts-jura
  ```

#### 2. Install encfs / gocryptfs

##### 2.1 Encfs

  ```
  sudo apt install encfs
  ```

##### 2.2 GoCryptFS

  ```
  sudo apt install gocryptfs
  ```




### Running pyencfsgui

- Clone the git project onto your machine
  ```
  git clone https://github.com/corelan/pyencfsgui.git
  ```
- Open a Terminal, go to the `pyencfsgui`folder
- Make the launcher executable if needed:
  ```
  chmod +x pyencfsgui.sh
  ```
- Run the launcher:
  ```
  ./pyencfsgui.sh
  ```
- On first run, the script will create a local virtual environment in `./pyencfsgui` and install the Python dependencies from `requirements.txt`
- The launcher changes into the repository folder before starting the app, so relative files resolve correctly and the built-in `git pull` update check runs from the project directory
- Check/edit the settings as needed. Make sure to verify the path of the various binaries (`encfs`, `gocryptfs`, `mount`)
- Create a new volume (or add an existing one to the application)
- Enjoy!


### Can I add a shortcut to the app in my Dock?

Sure!  Simply follow these steps:
- Use the included `pyencfsgui.app` bundle in the repository root
- Make sure `pyencfsgui.sh` is executable:
    ```
    chmod +x pyencfsgui.sh
    ```
- In Finder, open the repository folder and drag `pyencfsgui.app` into your Dock
- Launching the Dock icon will start `pyencfsgui.sh` without opening a Terminal window
- The app bundle does not hardcode your home folder. It resolves its own location at runtime and expects to live inside the repository folder, next to `pyencfsgui.sh`
- If you move `pyencfsgui.app` somewhere else, it will no longer know where the repository is. Keep the `.app` bundle in the project folder and add that copy to the Dock
- The bundle already uses the `bitmaps/encfsgui.icns` icon


## Known issues

### Character limitations for passwords

You're not supposed to use a single-tick (') or exclamation mark (!) in the password for new volumes.  It may cause the 'expect' script to fail, and/or might end up setting a different password on the volume. If you insist on using a single-tick or exclamation mark, simply create the volume with encfs yourself, and then add the volume to the app (as opposed to creating it in the app itself)


### GoCryptFS limitations

#### Custom volumename for GoCryptFS folders

GoCryptFS doesn't seem to support the ability to mount folders, specifying a custom volume name.  As a result, the mounted volume will simply have the name of the folder it is mounted at.
(Choose your folder names wisely!) 

### Linux Desktop Manager limitations

#### Hide to System Tray

Some Linux Desktop Managers will not show the system tray icon when "hiding" pyencfsgui.  This appears to be a PyQt5/Linux Desktop Manager compatibility issue.  
On Linux I decided to "minimize" the GUI rather than "hide" it, as you may not be able to "unhide" it (due to lack of a system tray icon you can interact with).
