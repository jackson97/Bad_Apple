#Bad_Apple
#---------

#Description
#-----------
#Python script utilising the OSX diskutil command in order to perform a brute force attack on FileVault volumes. It currently attaches a specified .dmg image file and determines the encrypted volume's GUID. It will then attempt to crack the password with a pre-determined password list. Once a password is found the script then gives the user the option to acquire the decrypted partition.

#Usage
#-----
#This script will only work for OS X images which have been converted to .dd (the first file being re-named to .dmg).

#|-----------------------------------------------|
#| Dependancies |	How to Install           |
#|-----------------------------------------------|
#| Tkinter	    |  brew install Tkinter      |
#| dc3dd	    |  brew install libewf       |
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
import tkFileDialog
import Tkconstants
from sys import platform as _platform
from Tkinter import *

class apple:
		   
    def userInfo(self):
        root = Tk()
        root.title("Bad Apple - FileVault decrypter")
        root.geometry("450x400")
        exam_name_label = Label(root, text="Examiner Name:")
        exam_name_label.pack()
        self.exam_name_text_box = Entry(root, bd=1)
        self.exam_name_text_box.pack()
        case_name_label = Label(root, text="Case Name:")
        case_name_label.pack()
        self.case_name_text_box = Entry(root, bd=1)
        self.case_name_text_box.pack()
        ex_ref_label = Label(root, text="Exhibit Ref:")
        ex_ref_label.pack()
        self.ex_ref_text_box = Entry(root, bd=1)
        self.ex_ref_text_box.pack()
        but = Button(root, text='Start')
        but.bind("<Button-1>", self.save_case_info)
        but.pack()
        self.status_text_box = Text(root,bd=5)
        self.status_text_box.pack(ipady=100, ipadx=100)
        self.status_text_box.insert(INSERT, "Welcome to Bad Apple version 1.0\n")
        self.status_text_box.insert(INSERT, "Enter details, press start, select dmg file...")
        root.mainloop()

    def save_case_info(self, event):
        self.examinerName = (self.exam_name_text_box.get())
        self.caseNumber = (self.case_name_text_box.get())
        self.exhibitRef = (self.ex_ref_text_box.get())
        if "/" in self.exhibitRef:
            self.exhibitRef = self.exhibitRef.replace("/","-")     
        if "/" in self.caseNumber:
            self.caseNumber = self.caseNumber.replace("/","-")
        if _platform == "darwin":
            self.mountDisk()
        else:
            self.popupWarning()

    def popupWarning(self):
        toplevel = Toplevel()
        toplevel.title("WARNING!")
        toplevel.geometry("350x80")
        label1 = Label(toplevel, text="No Darwin based operating system detected", height=0, width=50)
        label1.pack()
        label1 = Label(toplevel, text="Unable to continue...", height=0, width=50)
        label1.pack()
        button = Button(toplevel, text="Close", command=toplevel.destroy)
        button.pack()

    def mountDisk(self):
        diskToMount = tkFileDialog.askopenfilename()
        self.status_text_box.delete('1.0', END)
        self.status_text_box.insert(INSERT, "Attaching dmg to the system without mounting it...\n\n")
        #Attaching dmg file to the system without mounting it, to preserve the integrity of the evidence
        os.system('hdiutil attach -nomount %s' % (diskToMount))
        self.status_text_box.insert(INSERT, "Checking current core storage volumes...\n")
        self.status_text_box.insert(INSERT, "Searching for GUID of encrypted partition...\n\n")
        #Checks the current core storage volumes and finds the GUID of the encrypted partition.
	oldStdout = sys.stdout
        chkdiskCommand = subprocess.Popen('diskutil cs list', shell=True, stdout=subprocess.PIPE).stdout
        chkdiskOutput = chkdiskCommand.read()
        with open('temp.txt', 'w') as fo:
            fo.write(chkdiskOutput)
            sys.stdout = oldStdout
        with open('temp.txt', 'r') as GUIDlog:
            guidPattern = re.compile('^[{(]?[0-9A-F]{8}[-]?([0-9A-F]{4}[-]?){3}[0-9A-F]{12}[)}]?$')
            for line in GUIDlog:
                if 'Logical Volume ' in line:
                    GUIDtemp = line.split('Logical Volume ')[1].rstrip()
                    if (guidPattern.match(GUIDtemp)):
                        self.GUID = str(GUIDtemp)
                        #Once the GUID is found it is stored as a variable. A message is printed informing the user it has been found.
                        self.status_text_box.insert(INSERT, "Locked partition found. GUID: %s' % (self.GUID)")
                        #Asks the user whether they would like to begin cracking? Error handling to be added in the future.
                        self.popupConfirm()
                        
    def popupConfirm(self, event):
        toplevel = Toplevel()
        toplevel.title("Commence Cracking")
        toplevel.geometry("350x80")
        label1 = Label(toplevel, text="Do you want to begin cracking?", height=0, width=50)
        label1.pack()
        start = Button(toplevel, text="Start")
        start.bind("<Button-1>", self.popupConfirm)
        cancel = Button(toplevel, text="Cancel", command=toplevel.destroy)
        start.pack()
        cancel.pack()
    
    def passwordAttempts(self):
        loop = True
        os.system('clear')
        print('''

    Use built in wordlist                    |  [1]  |

    Select a Case Specific wordlist          |  [2]  |

        ''')
        crackingOption = raw_input('Please select an option. [1 or 2]: ')                
        #Calling the passwordAttempts Function.
        if crackingOption == '1':
            listToUse = ('wordlist.txt')
        elif crackingOption == '2':
            listToUse = tkFileDialog.askopenfilename()
        else:
            print('Please select a valid option.')
            os.system('sleep 1')
            os.system('clear')
        #Calculating the time the program was started.
        startTime = ("Process started - [{0}]".format(time.strftime("%H:%M:%S")))
        global allocatedDisk
        #Opens the dictionary file.
        wordList = open(listToUse, 'rw')
        #Sets the tracking variable.
        lineCount = 0
        keepTrack = 1
        print('\n')
        #Reads the dictionary file into a list, in alphabetical order.
        dict = []
        with wordList as f:
            for line in f:
                lineCount += 1
                dict.append(line.strip())
        #dict.sort()
        #Loops through the passwords in the dictionary list.
        for password in dict:
            #Incerements the tracking variable.
            #Attempts each password in the dictionary list using the GUID variable set earlier. Captures the output of this command.
            unlockCommand = subprocess.Popen('diskutil cs unlockVolume %s -passphrase %r' % (GUID, password), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
            unlockOutput = unlockCommand.read()
            #Checks for the keyword 'unlocked' in the captured output. If 'unlocked' is found the partition has been derypted.
            if 'unlocked' in unlockOutput:
                #Calculating the time the program was started.
                endTime=("Process completed - [{0}]".format(time.strftime("%H:%M:%S")))
                #Calculates the time taken by the program to crack the drive.
                print('\n\n{0} {1}\n'.format(startTime, endTime))
                #Prints the output from the successfull decryption command.
                print(unlockOutput)
                #Prints the correct password for the decrypted partition.
                print('Unlocked with the following password: %s\n' % (password))
                #Sets the allocatedDisk variable using the output from the successfull decryption command.
                self.allocatedDisk = int(re.search(r'\d+', unlockOutput).group())
                #Asks the user whether they want to acquire the unlocked partition? Error handling to be added in the future.
                imagePartition = raw_input('Do you want to acquire the unlocked partition? [Y/N]: ')
                if imagePartition in ('y' or 'Y'):
                    #Calling the acquireDisk Function.
                    self.acquireDisk()
                else:
                    print('Thank you for using Bad_Apple.')
                    quit()
            elif keepTrack == lineCount:
                os.system('clear')
                sys.stdout.write("\r%i Passwords attempted out of %i\n" % (keepTrack, lineCount))
                os.system('sleep 1')
                anotherOption = raw_input('Password not found, would you like to try again with a different option? [y or N]: ')
                while (loop == True): 
                    if anotherOption in ('y' or 'Y'):
                        passwordAttempts()
                    else:
                        print('Thank you for using Bad_Apple')
                        quit()
            else:
                sys.stdout.write("\r%i Passwords attempted out of %i" % (keepTrack, lineCount))
                keepTrack += 1
            
    def acquireDisk(self):
        #Prompting user for an output directory.
        print('Please select the desired ouput directory.')
        outputLoc = tkFileDialog.askdirectory()
        #Assigning the filename to be an amalgamation of the details entered in the userInfo Function.
        fileName = ('%s-%s-DECRYPTED' % (self.caseNumber, self.exhibitRef))
        print('\nAcquiring unlocked partition.')
        #Changing the working directory to the specified output location in order to save the acquisition log there as well.
        os.chdir('%s' % (outputLoc))
        #Imaging the unlocked partition.
        os.system('ewfacquire -t %s/%s -w -o 0 -C "%s" -e "%s" -E "%s" -D "Imaged to external HDD using Bad_apple." -N "Decrypted partition of exhibit %s from DFU REF: %s" -M physical -c none -P 512 -f encase6 -r 10 -b 64 -S 640.0MiB -m fixed -g 64 -v -d sha1 /dev/disk%s' % (outputLoc, fileName, self.caseNumber, self.examinerName, self.exhibitRef, self.exhibitRef, self.caseNumber, self.allocatedDisk))
        #Prints the acquisition report to a log.
        reportCommand = subprocess.Popen('ewfinfo -d dm %s/%s.E01' % (outputLoc, fileName), shell=True, stdout=subprocess.PIPE).stdout
        reportOutput = reportCommand.read()
        oldStdout = sys.stdout
        with open('"%s"-"%s"-Acquisition Log.txt' % (self.caseNumber, self.exhibitRef), 'w') as t:
            sys.stdout = t
            print reportOutput
            sys.stdout = oldStdout
        #Verifying the produced .E01 files.
        os.system('ewfverify -d sha1 -l %s/%s-VerifyLog.txt %s/%s.E01' % (outputLoc, fileName, outputLoc, fileName))
        #Ejecting unlocked partition.
        os.system('diskutil eject %s' % outputLoc)
        quit()

os.system('clear')
time.sleep(0.5)

global loop

app = apple()
#Calling the userInfo Function.
app.userInfo()
#Clearing the screen.
os.system('clear')
