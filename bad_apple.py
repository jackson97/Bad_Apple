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
    #Prompts the user to select a .dmg file they would like to decrypt and assigns the path to a variable.
    print('Please select the .dmg file you would like to decrypt.')
    diskToMount = tkFileDialog.askopenfilename()
    #Printing the .dmg path for testing purposes.
    print (diskToMount)
    #Attaching the specified .dmg file to the systme witghout mounting it to preserve the integrity of the evidence.
    os.system('hdiutil attach -nomount %s' % (diskToMount))
    #Checks the current core storage volumes and finds the GUID of the encrypted partition.
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
                        #Once the GUID is found it is stored as a variable. A message is printed informing the user it has been found.
                        print('Image mounted and locked partition found. GUID: %s' % (GUID))
                        #Asks the user whether they would like to begin cracking? Error handling to be added in the future.
                        startCracking = raw_input('Do you want to begin cracking? [Y/N]: ')
                        if startCracking in ('y' or 'Y'):   
                            #Calling the passwordAttempts Function.                        
                            passwordAttempts()
                        else:
                            print('Thank you for using Bad_Apple')
                            quit()
                    else:
                        loop = True
                else:
                    loop = True

def passwordAttempts():
    #Calculating the time the program was started.
    startTime=("Process started - [{0}]".format(time.strftime("%H:%M:%S")))
    global allocatedDisk
    #Opens the dictionary file.
    dictFile = open('dictFile.txt', 'rw')
    #Sets the tracking variable.
    keepTrack = 0
    print('\n')
    #Sets the progressbar widget.
    bar = progressbar.ProgressBar(widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    #Reads the dictionary file into a list, in alphabetical order.
    dict = []
    with dictFile as f:
        for line in f:
            dict.append(line.strip())
    dict.sort()
    bar.start()
    #Loops through the passwords in the dictionary list.
    for password in dict:
        #Incerements the tracking variable.
        keepTrack += 1
        #Updates the progressbar along with the tracking variable.
        bar.update(keepTrack)
        #Attempts each password in the dictionary list using the GUID variable set earlier. Captures the output of this command.
        unlockCommand = subprocess.Popen('diskutil cs unlockVolume %r -passphrase %s' % (GUID, password), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        unlockOutput = unlockCommand.read()
        #Checks for the keyword 'unlocked' in the captured output. If 'unlocked' is found the partition has been derypted.
        if 'unlocked' in unlockOutput:
            #Calculating the time the program was started.
            endTime=("Process completed - [{0}]".format(time.strftime("%H:%M:%S")))
            #Calculates the time taken by the program to crack the drive.
            print('\n\n{0} {1}\n'.format(startTime, endTime))
            #Prints the number of passwords attempted.
            print('%d passwords attempted.\n' % (keepTrack))
            #Prints the output from the successfull decryption command.
            print(unlockOutput)
            #Prints the correct password for the decrypted partition.
            print('Unlocked with the following password: %s\n' % (password))
            #Sets the allocatedDisk variable using the output from the successfull decryption command.
            allocatedDisk = int(re.search(r'\d+', unlockOutput).group())
            #Asks the user whether they want to acquire the unlocked partition? Error handling to be added in the future.
            imagePartition = raw_input('Do you want to acquire the unlocked partition? [Y/N]: ')
            if imagePartition in ('y' or 'Y'):
                #Calling the acquireDisk Function.
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
#Calling the userInfo Function.
userInfo()
#Clearing the screen.
os.system('clear')
#Calling the mountDisk Function.
mountDisk()
