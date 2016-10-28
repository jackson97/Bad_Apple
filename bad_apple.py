import os
import sys

GUID = raw_input('Please enter the GUID of the drive you wish to crack: ')

def password_attempt():
	with open('sevenDigitDict.txt') as f:
		for password in f:
			command = os.system('diskutil cs unlockVolume %s -passphrase %s' % (GUID, password))
   
password_attempt()
