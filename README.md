# pyencfsgui

## What is pyencfsgui 

pyencfsgui is a Qt based GUI/wrapper around encfs, encfsctl and mount, written in python3, and relies on OSXFuse to provide a filesystem.<br>
In other words, it relies entirely on those utilities, the ability to interact with those tools and to capture the output from those tools.<br>
As a result, the EncFSGui source code is pretty easy to understand, as it does not contain any crypto or other black magic to do its job.<br>
The downside is that it is a wrapper and may break if tools start behaving in a different way.<br>

## Dependencies

In order to use pyencfsgui, you need to install the following dependencies:

- python3
- encfs
- OSXFuse

### Installing dependencies on OSX


1. Install Homebrew

  ```
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  sudo chown -R $(whoami) /usr/local/lib
  brew doctor
  ```

2. Install OSXFuse

  Download the dmg image from http://sourceforge.net/projects/osxfuse/files/ and install


3. Install encfs

  ```
  brew update
  ``` 

 Check if everything is ok and install encfs

  ```
  brew doctor
  brew install homebrew/fuse/encfs
  ```

  Check if encfs works:
  ```
  encfs    
  ```


4. Install python3
  ```
  brew install python3
  ```