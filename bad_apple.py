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
guid_pattern = re.compile('^[{(]?[0-9A-F]{8}[-]?([0-9A-F]{4}[-]?){3}[0-9A-F]{12}[)}]?$')

def mount_disk():
    loop = True
    print('Please select the .dmg file you would like to decrypt.')
    disk_to_mount = tkFileDialog.askopenfilename()
    print (disk_to_mount)
    os.system('hdiutil attach -nomount %s' % (disk_to_mount))
    mount_command = subprocess.Popen('diskutil cs list', shell=True, stdout=subprocess.PIPE).stdout
    mount_output = mount_command.read()
    for line in mount_output:
        if 'Logical Volume ' in mount_output:
            GUID = line.split('Logical Volume',1)
            if (guid_pattern.match(GUID)):
                start_cracking = raw_input('Do you want to begin cracking? [Y/N]: ')
                if start_cracking in ('y' or 'Y'):
                    password_attempt()
                else:
                    print('Thank you for using Bad_Apple')
                    quit()
            else:
                loop = True
        else:
            loop=True
            
def password_attempt():
    with open('sevenDigitDict.txt') as f:
        for password in f:
            unlock_command = subprocess.Popen('diskutil cs unlockVolume %s -passphrase %s &> /dev/null' % (GUID, password), shell=True, stdout=subprocess.PIPE).stdout
            unlock_output = unlock_command.read()
            if 'unlocked' in unlock_output:
                print('Unlocked with the following password: %s' % (password))
                allocated_disk = int(re.search(r'\d+', output).group())
                image_partition = raw_input('Do you want to acquire the unlocked partition? [Y/N]: ')
                if image_partition in ('y' or 'Y'):
                    print('Please select the desired ouput directory.')
                    output_loc = tkFileDialog.askdirectory()
                    file_name = raw_input('Please enter the desired filename (e.g. filename-DECRYPTED.dd): ')
                    os.system('diskutil eject %s' % (GUID))
                    os.system('sudo pv -tpreb /dev/disk%s | dd of=%s/%s bs=1m' % (allocated_disk, output_loc, file_name))
                    quit()
                else:
                    print('Thank you for using Bad_Apple')
                    quit()

os.system('clear')
print('Welcome to Bad_Apple\n')
time.sleep(0.5)

global GUID
mount_disk()

while(loop == True):
    GUID = raw_input('Please enter the GUID of the drive you wish to crack: ')
    print('Type exit/Exit to quit)')
    if (GUID == 'exit' or GUID == 'Exit'):
        break
    else:
        if (guid_pattern.match(GUID)):
            password_attempt()
        else:
            print "'" + GUID + "' is not a GUID"
            time.sleep(1)
            os.system('clear')
            loop = True
