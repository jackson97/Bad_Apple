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

def user_info():
    global examinerName
    global caseNumber
    global exhibitRef
    print('Please enter the case details. (Seperate with "-")\n')
    examinerName = raw_input('Examiner Name: ')
    caseNumber = raw_input('Case Number: ')
    exhibitRef = raw_input('Exhibit Ref: ')

def mount_disk():
    global GUID
    global GUIDstr
    loop = True
    print('Please select the .dmg file you would like to decrypt.')
    disk_to_mount = tkFileDialog.askopenfilename()
    print (disk_to_mount)
    os.system('hdiutil attach -nomount %s' % (disk_to_mount))
    chkdisk_command = subprocess.Popen('diskutil cs list', shell=True, stdout=subprocess.PIPE).stdout
    chkdisk_output = chkdisk_command.read()
    old_stdout = sys.stdout
    with open('temp.txt', 'w') as t:
        sys.stdout = t
        print chkdisk_output
        sys.stdout = old_stdout
    with open('temp.txt', 'r') as GUIDlog:
        guid_pattern = re.compile('^[{(]?[0-9A-F]{8}[-]?([0-9A-F]{4}[-]?){3}[0-9A-F]{12}[)}]?$')
        while (loop == True):
            for line in GUIDlog:
                if 'Logical Volume ' in line:
                    GUIDtemp = line.split('Logical Volume ')[1].rstrip()
                    if (guid_pattern.match(GUIDtemp)):
                        GUID = str(GUIDtemp)
                        print('Image mounted and locked partition found. GUID: %s' % (GUID))
                        start_cracking = raw_input('Do you want to begin cracking? [Y/N]: ')
                        if start_cracking in ('y' or 'Y'):                           
                            password_attempts()
                        else:
                            print('Thank you for using Bad_Apple')
                            quit()
                    else:
                        loop = True
                else:
                    loop = True

def password_attempts():
    global allocatedDisk
    dictFile = open('dictFile.txt', 'rw')
    keepTrack = 0
    print('\n')
    bar = progressbar.ProgressBar(maxval=65, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    dict = []
    with dictFile as f:
        for line in f:
            dict.append(line.strip())
    dict.sort()
    bar.start()
    for password in dict:
        keepTrack += 1
        bar.update(keepTrack)
        unlock_command = subprocess.Popen('diskutil cs unlockVolume %r -passphrase %s' % (GUID, password), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        unlock_output = unlock_command.read()
        if 'unlocked' in unlock_output:
            end_time=("Process completed - [{0}]".format(time.strftime("%H:%M:%S")))
            print('\n\n{0} {1}\n'.format(start_time, end_time))
            print('%d passwords attempted.\n' % (keepTrack))
            print(unlock_output)
            print('Unlocked with the following password: %s\n' % (password))
            allocatedDisk = int(re.search(r'\d+', unlock_output).group())
            image_partition = raw_input('Do you want to acquire the unlocked partition? [Y/N]: ')
            if image_partition in ('y' or 'Y'):
                acquireDisk()
            else:
                print('Thank you for using Bad_Apple.')
                quit()

def acquireDisk():
    print('Please select the desired ouput directory.')
    outputLoc = tkFileDialog.askdirectory()
    fileName = ('%s-%s-DECRYPTED' % (caseNumber, exhibitRef))
    print('Ejecting disk for acquisition.')
    os.system('diskutil eject %s' % (GUID))
    print('\nAcquiring unlocked partition.')
    os.chdir('%s' % (outputLoc))
    with open('%s-log.txt' % (fileName), 'w') as log:
        log.write('Examiner Name: %s\n' % (examinerName))
        log.write('Case Number: %s\n' % (caseNumber))
        log.write('Exhibit Reference: %s\n' % (exhibitRef))
        log.close()
    os.system('sudo dc3dd if=/dev/disk%s hash=md5 hof=%s/%s.dd log=%s-log.txt' % (allocatedDisk, outputLoc, fileName, fileName))
    #Replacing [ok] in log with [Verification Successful] for readablility.
    f1 = open('%s-log.txt' % (fileName), 'r')
    f2 = open('%s-log.txt.tmp' % (fileName), 'w')
    for line in f1:
        f2.write(line.replace('[ok]', '[Verification Successful]'))
    f1.close()
    f2.close()

    os.system('%s-log.txt' % (fileName))
    os.rename('%s-log.txt.tmp' % (fileName),'%s-log.txt' % (fileName))
    quit()

root = Tk()

os.system('clear')
print('Welcome to Bad_Apple\n')
time.sleep(0.5)

global loop
start_time=("Process started - [{0}]".format(time.strftime("%H:%M:%S")))

user_info()
os.system('clear')
mount_disk()
