#Bad_Apple
#---------

#Description
#-----------
#Python script utilising the OSX diskutil command in order to perform a brute force attack on FileVault volumes. It currently attaches a specified .dmg image file and determines the encrypted volume's GUID. It will then attempt to crack the password with a pre-determined password list. Once a password is found the script then gives the user the option to acquire the decrypted partition.

#Usage
#-----
#This script will only work for OS X images which have been converted to .dd (the first file being re-named to .dmg).

#|-----------------------------------------------|
#| Dependancies |	How to Install               |
#|-----------------------------------------------|
#| Tkinter	    |  brew install Tkinter          |
#| progressbar  |  sudo easy_install progressbar |
#| dc3dd	    |  brew install dc3dd            |
#|-----------------------------------------------|

#To Do
#-----
# 1. Include the option to create case specific keyword lists.
# 2. Incorportate timekeeping i.e. estimated time remaining etc.
# 3. Add GUI interface.

#Importing the required libraries.
import time
import os
import sys
import subprocess
import datetime
import re
import string
from Tkinter import *
import tkFileDialog
import Tkconstants
import progressbar

def userInfo():
    #Prompting the user to input the case details. Error handling to be added in the future.
    global examinerName
    global caseNumber
    global exhibitRef
    print('Please enter the case details. (Seperate with "-")\n')
    examinerName = raw_input('Examiner Name: ')
    caseNumber = raw_input('Case Number: ')
    exhibitRef = raw_input('Exhibit Ref: ')

def mountDisk():
    global GUID
    loop = True
    print('Please select the .dmg file you would like to decrypt.')
    diskToMount = tkFileDialog.askopenfilename()
    print (diskToMount)
    os.system('hdiutil attach -nomount %s' % (diskToMount))
    chkdiskCommand = subprocess.Popen('diskutil cs list', shell=True, stdout=subprocess.PIPE).stdout
    chkdiskOutput = chkdiskCommand.read()
    oldStdout = sys.stdout
    with open('temp.txt', 'w') as t:
        sys.stdout = t
        print chkdiskOutput
        sys.stdout = oldStdout
    with open('temp.txt', 'r') as GUIDlog:
        guidPattern = re.compile('^[{(]?[0-9A-F]{8}[-]?([0-9A-F]{4}[-]?){3}[0-9A-F]{12}[)}]?$')
        while (loop == True):
            for line in GUIDlog:
                if 'Logical Volume ' in line:
                    GUIDtemp = line.split('Logical Volume ')[1].rstrip()
                    if (guidPattern.match(GUIDtemp)):
                        GUID = str(GUIDtemp)
                        print('Image mounted and locked partition found. GUID: %s' % (GUID))
                        startCracking = raw_input('Do you want to begin cracking? [Y/N]: ')
                        if startCracking in ('y' or 'Y'):                           
                            passwordAttempts()
                        else:
                            print('Thank you for using Bad_Apple')
                            quit()
                    else:
                        loop = True
                else:
                    loop = True

def passwordAttempts():
    global allocatedDisk
    dictFile = open('dictFile.txt', 'rw')
    keepTrack = 0
    print('\n')
    bar = progressbar.ProgressBar(widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    dict = []
    with dictFile as f:
        for line in f:
            dict.append(line.strip())
    dict.sort()
    bar.start()
    for password in dict:
        keepTrack += 1
        bar.update(keepTrack)
        unlockCommand = subprocess.Popen('diskutil cs unlockVolume %r -passphrase %s' % (GUID, password), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        unlockOutput = unlockCommand.read()
        if 'unlocked' in unlockOutput:
            endTime=("Process completed - [{0}]".format(time.strftime("%H:%M:%S")))
            print('\n\n{0} {1}\n'.format(startTime, endTime))
            print('%d passwords attempted.\n' % (keepTrack))
            print(unlockOutput)
            print('Unlocked with the following password: %s\n' % (password))
            allocatedDisk = int(re.search(r'\d+', unlockOutput).group())
            imagePartition = raw_input('Do you want to acquire the unlocked partition? [Y/N]: ')
            if imagePartition in ('y' or 'Y'):
                acquireDisk()
            else:
                print('Thank you for using Bad_Apple.')
                quit()

def acquireDisk():
    #Prompting user for an output directory.
    print('Please select the desired ouput directory.')
    outputLoc = tkFileDialog.askdirectory()
    #Assigning the filename to be an amalgamation of the details entered in the userInfo Function.
    fileName = ('%s-%s-DECRYPTED' % (caseNumber, exhibitRef))
    print('\nAcquiring unlocked partition.')
    #Changing the working directory to the specified output location in order to save the acquisition log there as well.
    os.chdir('%s' % (outputLoc))
    #Writing the details entered in the userInfo Function to the beginning of the acquisition log.
    with open('%s-log.txt' % (fileName), 'w') as log:
        log.write('Examiner Name: %s\n' % (examinerName))
        log.write('Case Number: %s\n' % (caseNumber))
        log.write('Exhibit Reference: %s\n' % (exhibitRef))
        log.close()
    #Imaging the unlocked partition.
    os.system('sudo dc3dd if=/dev/disk%s hash=md5 hash=sha1 hof=%s/%s.dd log=%s-log.txt' % (allocatedDisk, outputLoc, fileName, fileName))
    #Replacing '[ok]' in log with '[Verification Successful]' for readablility.
    f1 = open('%s-log.txt' % (fileName), 'r')
    f2 = open('%s-log.txt.tmp' % (fileName), 'w')
    for line in f1:
        f2.write(line.replace('[ok]', '[Verification Successful]'))
    f1.close()
    f2.close()
    #Replacing 'dc3dd' in log with 'Imaging' for readablility.
    f1 = open('%s-log.txt' % (fileName), 'r')
    f2 = open('%s-log.txt.tmp' % (fileName), 'w')
    for line in f1:
        f2.write(line.replace('dc3dd', 'Imaging'))
    f1.close()
    f2.close()
    
    #Resolving temporary logs.
    os.system('rm %s-log.txt' % (fileName))
    os.rename('%s-log.txt.tmp' % (fileName),'%s-log.txt' % (fileName))
    quit()

root = Tk()

os.system('clear')
print('Welcome to Bad_Apple\n')
time.sleep(0.5)

global loop
#Calculating the time the program was started.
startTime=("Process started - [{0}]".format(time.strftime("%H:%M:%S")))

#Calling the userInfo Function.
userInfo()
#Clearing the screen.
os.system('clear')
#Calling the mountDisk Function.
mountDisk()
