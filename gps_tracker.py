import math
from network import LTE
import os
import time
import utime
import gc
from machine import RTC
from machine import SD
from L76GNSS import L76GNSS
from pytrack import Pytrack
import socket
import ssl
import ussl
import pycom
import urequests

#setup global variables
NTP_SERVER = "ca.pool.ntp.org"
remote_address_base = "https://myremotewebsite.com"
sleeptime = 300 #time between GPS updates in seconds

#mount SD card
sd = SD()
os.mount(sd, '/sd')

#disable LED blinking
pycom.heartbeat(False)
pycom.rgbled(0xFFFFFF)

time.sleep(1)
gc.enable()

#establishing global variables with initial GPS values
latitude = float(1.0)
longitude = float(1.1)

latitude_previous = float(1.2)
longitude_previous = float(1.3)


# Need to use global variables.
# If in each function you delare a new reference, functionality is broken
lte = LTE()
rtc = RTC()

# Returns a network.LTE object with an active Internet connection.
def getLTE():

    # If already used, the lte device will have an active connection.
    # If not, need to set up a new connection.
    if lte.isconnected():
        return lte

    # Modem does not connect successfully without first being reset.
    print("Resetting LTE modem ... ", end='')
    lte.send_at_cmd('AT^RESET')
    print("OK")
    time.sleep(1)

    # While the configuration of the CGDCONT register survives resets,
    # the other configurations don't. So just set them all up every time.
    print("Configuring LTE ", end='')
    lte.send_at_cmd('AT+CGDCONT=1,"IP","hologram"')
    print(".", end='')
    lte.send_at_cmd('AT!="RRC::addscanfreq"')
    print(".", end='')
    lte.send_at_cmd('AT+CFUN=1')
    print(" OK")

    # If correctly configured for carrier network, attach() should succeed.
    if not lte.isattached():
        print("Attaching to LTE network ", end='')
        lte.attach()
        while(True):
            if lte.isattached():
                print(" OK")
                break
            print('.', end='')
            time.sleep(1)

    # Once attached, connect() should succeed.
    if not lte.isconnected():
        print("Connecting on LTE network ", end='')
        lte.connect()
        while(True):
            if lte.isconnected():
                print(" OK")
                pycom.rgbled(0x0000FF)
                break
            print('.', end='')
            time.sleep(1)

    # Once connect() succeeds, any call requiring Internet access will
    # use the active LTE connection.
    return lte

# Clean disconnection of the LTE network is required for future
# successful connections without a complete power cycle between.
def endLTE():

    print("Disconnecting LTE ... ", end='')
    lte.disconnect()
    print("OK")
    time.sleep(1)
    print("Detaching LTE ... ", end='')
    lte.dettach()
    print("OK")
    pycom.rgbled(0x000000)

# Sets the internal real-time clock.
# Needs LTE for Internet access.
def setRTC():

    print("Updating RTC from {} ".format(NTP_SERVER), end='')
    rtc.ntp_sync(NTP_SERVER)
    utime.timezone(-14400)
    while not rtc.synced():
        print('.', end='')
        time.sleep(1)
    print(' OK')

# Only returns an RTC object that has already been synchronised with an NTP server.
def getRTC():

    if not rtc.synced():
        setRTC()

    return rtc

def getGPS():
    py = Pytrack()
    l76 = L76GNSS(py, timeout=30)
    global coord
    coord = l76.coordinates()
    
    global latitude
    global longitude

    try:
        print(coord)

        if type(coord[1]) == "NoneType":
            pycom.rgbled(0xFF0000)
            latitude = round(0, 5)
        else:
            latitude = round(coord[1], 5)

        if type(coord[0]) == "NoneType":
            pycom.rgbled(0xFF0000)
            longitude = round(0, 5)
        else:
            longitude = round(coord[0], 5)
    except:
        pass
        print("can't get signal")
        longitude = 999
        latitude = 999

    global remote_address
    remote_address = remote_address_base
    remote_address += "?lat="
    remote_address += str(latitude) 
    remote_address += "&lon="
    remote_address += str(longitude)

def uploadDATA():
    #upload current position to the database
    print(remote_address)
    notify = urequests.get(remote_address)
    print("Uploading data to the server")
    notify.close()

def saveToSD():
    #save location to the SD card
    f = open('/sd/gps-record.txt', 'a')
    print("saving location to the SD card")
    f.write("{} , {}\n".format(coord, utime.localtime() ))
    f.close()

# Program starts here.

#connect to LTE
lte = getLTE()

#get real time clock
rtc = getRTC()

#get the current position
getGPS()

#upload current position to the database
uploadDATA()

#change color to red
pycom.rgbled(0xFF0000)

#close LTE connection
endLTE()

print("entering the main loop")
time.sleep(1)

#main loop
while True:

    #get current coordinates
    getGPS()

    #change color to green
    pycom.rgbled(0x008000)

    #print current coordinates and time
    print("GPS Location:", latitude,",",longitude)
    print("Current Time:", utime.localtime())

    #check if the position has changed
    global lat_difference
    global lon_difference

    lat_difference = latitude - latitude_previous
    lon_difference = longitude - longitude_previous

    if abs(lat_difference) > 0.00022 and abs(lon_difference) > 0.00022 and longitude != 999:

        #if the position has changed from the previous one, save to SD
        print("new location different from the previous one")
        saveToSD()
        getLTE()
        uploadDATA()
        pycom.rgbled(0xFF0000)
        endLTE()

    else:
        print("Tracker has NOT moved, no update neccessary")
        print("GPS Location:", latitude,",",longitude)
        print("Current Time:", utime.localtime())

    latitude_previous = latitude
    longitude_previous = longitude

    #turn the LED off to save power
    pycom.rgbled(0x000000)
    
    #wait X seconds
    time.sleep(sleeptime)

