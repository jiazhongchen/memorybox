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

VERSION=10 #1.0

STUDENTSLIST=100
ZIPFILE=101
HEARTBEAT=102
CARDID=177

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
    dst2 = '/home/pi/projects/tmp/tsmemory.tar.gz'
    if os.path.isfile(src1) == True:
        print "find the students list"
        copyfile(src1, dst1)
        print "file copied, now you can safely unplug the usb"
        blinkGreenLED(2)
        eventType=STUDENTSLIST
        eventCode=1
        sendEventCalamp(ser2, eventType, eventCode)
    else:
        print "students list not found"
        blinkRedLED(2)
        eventType=STUDENTSLIST
        eventCode=2
        sendEventCalamp(ser2, eventType, eventCode)

    time.sleep(5)
    if os.path.isfile(src2) == True:
        print "find the memory file"
        if os.path.isdir('home/pi/projects/tmp') == False:
            os.system('mkdir -p /home/pi/projects/tmp')
        copyfile(src2, dst2)

        eventType=ZIPFILE
        eventCode=0
        sendEventCalamp(ser2, eventType, eventCode)
        
        print "file copied, now you can safely unplug the usb"
        blinkGreenLED(10, 0.5)
    else:
        print "zip file not found"
        blinkRedLED(10, 0.5)
    time.sleep(5)

def blinkRedLED(sec, freq=1):
    print "blink Red LED for " + str(sec) + " seconds"
    for x in range(0, sec):
        redLED.on()
        time.sleep(freq)
        redLED.off()
        time.sleep(freq)

def blinkGreenLED(sec, freq=1):
    print "blink Green LED for " + str(sec) + " seconds"
    for x in range(0, sec):
        greenLED.on()
        time.sleep(freq)
        greenLED.off()
        time.sleep(freq)

def turnOnRedLED():
    greenLED.off()
    redLED.on()

def turnOnGreenLED():
    redLED.off()
    greenLED.on()

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

def sendEventCalamp(calampPort, eventType, eventCode, payload=''):
    str = "at$app msg "
    str += "ZZ"
    str += "%02X"%eventType
    str += "%02X"%eventCode
    str += payload
    str += " 1\r\n"
    print str
    calampPort.write(str)

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
        now = time.time()

        if cardID:
            eventType = CARDID
            if cardID in open('/home/pi/projects/memorybox/students.lst').read():
                print cardID + " valid"
                eventCode = 1
                turnOnGreenLED()
            else:
                print cardID + " invalid"
                eventCode = 0
                turnOnRedLED()
            payload = cardID
            sendEventCalamp(ser2, eventType, eventCode, payload)
            cardID=''

        time.sleep(1)

        if time.time() - now > 300:
            print '5 min passed'
            """
            send heart beat event
            """
            eventType = HEARTBEAT
            eventCodd = 0
            payload = VERSION
            sendEventCalamp(ser2, eventType, eventCode, payload)
            now = time.time()

if __name__ == '__main__':
    main()


