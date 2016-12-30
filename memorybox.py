#!/usr/bin/python2.7.3 -tt
# test BLE Scanning software
# jcs 6/8/2014
# version 1.1 released on 27/11/2015 
# add timeout functions
# version 1.0 released on 27/11/2015

import os
import sys
import time
import datetime
import threading
import serial
import commands

from gpiozero import LED
from shutil import copyfile

#import urllib2
#import fcntl, socket, struct

cardID=''
USBStatus = False
lastUSBStatus = False
ser1 = serial.Serial(port='/dev/ttyUSB0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
ser2 = serial.Serial(port='/dev/ttyUSB1', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

redLED = LED(17)
greenLED = LED(27)

def copyFile():
    print "now do some copy"
    src1 = '/mnt/usb/students.lst'
    dst1 = '/home/pi/projects/memorybox/students.lst'
    src2 = '/mnt/usb/tsmemory.tar.gz'
    dst2 = '/home/pi/projects/memorybox/tsmemory.tar.gz'
    if os.path.isfile(src1) == True:
        print "find the src1 file"
        copyfile(src1, dst1)
        print "file copied, now you can safely unplug the usb"
        blinkGreenLED(2)
    else:
        print "src1 not found"
        blinkRedLED(2)

    time.sleep(5)
    if os.path.isfile(src2) == True:
        print "find the src1 file"
        if os.path.isdir('home/pi/projects/memorybox/temp') == False:
            os.system('mkdir -p /home/pi/projecst/memorybox/temp')
        copyfile(src2, dst2)
        print "file copied, now you can safely unplug the usb"
        blinkGreenLED(3)
    else:
        print "src2 not found"
        blinkRedLED(3)
    time.sleep(5)

def blinkRedLED(sec):
    print "blink Red LED for " + str(sec) + " seconds"
    for x in range(0, sec):
        redLED.on()
        time.sleep(1)
        redLED.off()
        time.sleep(1)

def blinkGreenLED(sec):
    print "blink Green LED for " + str(sec) + " seconds"
    for x in range(0, sec):
        greenLED.on()
        time.sleep(1)
        greenLED.off()
        time.sleep(1)

def turnOnRedLED():
    greenLED.off()
    redLED.on()

def turnOnGreenLED():
    redLED.off()
    greenLED.on()()

def checkUSB():

    global USBStatus
    global lastUSBStatus

    while True:
        t = commands.getstatusoutput('ls /dev | grep \'^sd[a-z][0-9]*$\'')
        if t[1] == '':
            USBStatus = False
        else:
            USBStatus = True
        if lastUSBStatus == False and USBStatus == True:
            newusb = t[1].split('\n')[-1]
            print "new usb inserted:" + newusb
            cmdstr1 = 'sudo mount /dev/' + newusb + ' /mnt/usb'
            r = commands.getstatusoutput(cmdstr1)
            if r[0] == 0:
                print "usb mounted, ready to use"
            time.sleep(1)
            copyFile()

            cmdstr2 = 'sudo udisksctl unmount -b /dev/' + newusb
            r = commands.getstatusoutput(cmdstr2)
            print r

            if r[0] == 0:
                print "usb unmounted, safe to unplug"

        elif lastUSBStatus == True and USBStatus == False:
            print "usb unpluged"

        lastUSBStatus = USBStatus
        time.sleep(1)

def checkUart1():

    global cardID
    while True:
        x=ser1.read(14)
        if x:
            cardID=x[1]+x[2]+x[5]+x[6]+x[7]+x[8]+x[9]+x[10]
        time.sleep(0.5)

def main():

    global cardID
    thread1 = threading.Thread(target=checkUart1)
    thread1.start()
    thread2 = threading.Thread(target=checkUSB)
    thread2.start()

    time.sleep(1)

    while True:
        """
        check if any card reading is happening
        """
        if cardID:
            if cardID in open('/home/pi/projects/memorybox/students.lst').read():
                print cardID + " valid"
                #blinkGreenLED(3)
                turnOnGreenLED()
            else:
                print cardID + " invalid"
                #blinkRedLED(3)
                turnOnRedLED()
            cardID=''

        time.sleep(1)

if __name__ == '__main__':
    main()


