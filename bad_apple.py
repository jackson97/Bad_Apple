import time
import os
import sys
import subprocess
import datetime
import re
import string
import Tkinter as tk
import tkFileDialog
import Tkconstants

root = tk.Tk()
global loop

def mount_disk():
    print('Please select the .dmg file you would like to decrypt.')
    disk_to_mount = tkFileDialog.askopenfilename()
    print (disk_to_mount)
    os.system('hdiutil attach -nomount %s' % (disk_to_mount))

def password_attempt():
    with open('sevenDigitDict.txt') as f:
        for password in f:
            command = subprocess.Popen('diskutil cs unlockVolume %s -passphrase %s &> /dev/null' % (GUID, password), shell=True, stdout=subprocess.PIPE).stdout
            output = command.read()
            if 'unlocked' in output:
                print('Unlocked with the following password: %s' % (password))
                allocated_disk = int(re.search(r'\d+', output).group())
                image_partition = raw_input('Do you want to acquire the unlocked partition? [Y/N]: ')
                if image_partition in ('y' or 'Y'):
                    print('Please select the desired ouput directory.')
                    output_loc = tkFileDialog.askdirectory()
                    file_name = raw_input('Please enter the desired filename (e.g. filename-DECRYPTED.dd): ')
                    os.system('pv -tpreb /dev/disk%s | dd of=%s/%s bs=1m' % (allocated_disk, output_loc, file_name))
                    quit()
                else:
                    loop = False
                    quit()

os.system('clear')
print('Welcome to Bad_Apple\n')
time.sleep(0.5)

global GUID
loop = True
mount_disk()
guid_pattern = re.compile('^[{(]?[0-9A-F]{8}[-]?([0-9A-F]{4}[-]?){3}[0-9A-F]{12}[)}]?$')
while(loop == True):
    GUID = raw_input('Please enter the GUID of the drive you wish to crack: ')
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
