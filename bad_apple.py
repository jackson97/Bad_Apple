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
    with open('temp.txt', 'r') as log:
        guid_pattern = re.compile('^[{(]?[0-9A-F]{8}[-]?([0-9A-F]{4}[-]?){3}[0-9A-F]{12}[)}]?$')
        while (loop == True):
            for line in log:
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
    output_loc = tkFileDialog.askdirectory()
    file_name = raw_input('Please enter the desired filename (e.g. filename-DECRYPTED(.dd assumed)): ')
    print('Ejecting disk for acquisition.')
    os.system('diskutil eject %s' % (GUID))
    print('\nAcquiring unlocked partition.')
    os.system('sudo dcfldd if=/dev/disk%s hash=md5 sizeprobe=if bs=1m of=%s/%s vf=%s/%s.dd' % (allocatedDisk, output_loc, file_name, output_loc, file_name))
    print('\nVerifying acquisition.')
    os.system('sudo dcfldd if=/dev/disk%s status=on vf=%s/%s.dd' % (allocatedDisk, output_loc, file_name))
    quit()

root = Tk()

os.system('clear')
print('Welcome to Bad_Apple\n')
time.sleep(0.5)

global loop
start_time=("Process started - [{0}]".format(time.strftime("%H:%M:%S")))

mount_disk()
