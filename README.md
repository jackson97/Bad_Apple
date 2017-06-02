![Supported Python versions](https://img.shields.io/badge/python-2.7-blue.svg)

# Bad_Apple

Description
================
Python script utilising the OSX diskutil command in order to perform a brute force attack on FileVault volumes. It currently attaches a specified .dmg image file and determines the encrypted volume's GUID. It will then attempt to crack the password with a pre-determined password list. Once a password is found the script then gives the user the option to acquire the decrypted partition.

Usage
========
This script will only work for OS X images which have been converted to .dd (the first file being re-named to .dmg).

| Dependancies  | How to Install                 |
| ------------- | ------------------------------ |
| Tkinter       |  brew install Tkinter          |
| progressbar   |  sudo easy_install progressbar |
| dc3dd         |  brew install dc3dd            |

To Do
========
1. Include the option to create case specific keyword lists.
2. Incorportate timekeeping i.e. estimated time remaining etc.
3. Create step-by-step guide for usage.
4. Add GUI interface.


os.system('mount -o ro,noexec,noload,noatime,loop /mnt/ewf/' + imagefile + 'dd /mnt/raw/') 
