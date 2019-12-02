# pyencfsgui

## What is pyencfsgui?

pyencfsgui is a Qt based GUI/wrapper around encfs, encfsctl and mount, written in python3, and relies on OSXFuse to provide a filesystem.<br>
In other words, it relies entirely on those utilities, the ability to interact with those tools and to capture the output from those tools.<br>
As a result, the EncFSGui source code is pretty easy to understand, as it does not contain any crypto or other black magic to do its job.<br>
The downside is that it is a wrapper and may break if tools start behaving in a different way.<br>
pyencfsgui was developed and tested on OSX High Sierra, Mojave and OSX Catalina, using encfs version 1.9.x. <br>
(It can open existing volumes that have been created with older versions of encfs too)

## Dependencies

In order to use pyencfsgui, you need to install the following dependencies:

- python3 (and PyQT5)
- OSXFuse
- encfs (1.9.x)



### Installing dependencies on OSX

#### 1. Install Homebrew

  ```
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  sudo chown -R $(whoami) /usr/local/lib/pkgconfig
  brew doctor
  ```

#### 2. Install OSXFuse

  Download the latest dmg installer image from https://osxfuse.github.io/ and run the installer.

  If you're running Catalina (or any OSX version that doesn't have a working OSXFuse installer yet), you'll have to install osxfuse using brew:

  ```
  brew tap homebrew/cask
  brew cask install osxfuse
  ```

  Make sure to enable the kernel extension in System Preferences → Security & Privacy → General  if/as requested
  Reboot for osxfuse to work correctly.

#### 3. Install encfs

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

#### 4. Install python3
  ```
  brew install python3
  ```

#### 5. Install PyQt5
  ```
  pip3 install --upgrade pip --user
  python3 -m pip install PyQt5 --user
  ```


### Running pyencfsgui

- Clone the git project onto your machine
- Open a Terminal, go to the folder
- run `python3 encfsgui.py`
- Check/edit the settings as needed
- Create a new volume (or add an existing one to the application)
- Enjoy!
