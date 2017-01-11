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

root = Tk()

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
                            password_attempt()
                        else:
                            print('Thank you for using Bad_Apple')
                            quit()
                    else:
                        loop = True
                else:
                    loop = True

def password_attempt():
    dict = []
    with open('numCodeDict.txt', 'r') as f:
        for line in f:
            dict.append(line.strip())
    dict.sort()
    for password in dict:
        unlock_command = subprocess.Popen('diskutil cs unlockVolume %r -passphrase %s' % (GUID, password), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        unlock_output = unlock_command.read()
        if 'unlocked' in unlock_output:
            end_time=("Process completed - [{0}]".format(time.strftime("%H:%M:%S")))
            print('{0} {1}'.format(start_time, end_time))
            print(unlock_output)
            print('Unlocked with the following password: %s' % (password))
            allocated_disk = int(re.search(r'\d+', unlock_output).group())
            image_partition = raw_input('Do you want to acquire the unlocked partition? [Y/N]: ')
            if image_partition in ('y' or 'Y'):
                print('Please select the desired ouput directory.')
                output_loc = tkFileDialog.askdirectory()
                file_name = raw_input('Please enter the desired filename (e.g. filename-DECRYPTED.dd): ')
                print('Ejecting disk for acquisition.')
                os.system('diskutil eject %s' % (GUID))
                os.system('sudo pv -tpreb /dev/disk%s | dd of=%s/%s bs=1m' % (allocated_disk, output_loc, file_name))
                quit()
            else:
                print('Thank you for using Bad_Apple')
                quit()

os.system('clear')
print('Welcome to Bad_Apple\n')
time.sleep(0.5)

global loop
start_time=("Process started - [{0}]".format(time.strftime("%H:%M:%S")))
mount_disk()
