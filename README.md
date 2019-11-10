# GPS_LTE_tracker
Pycom's GPY &amp; PyTrack attached to a custom 12VDC charging board that houses a single 18650 battery. 

This device is supposed to be for tracking vehicles in case they get stolen. Once the location changes, the new location is sent over LTE to the specified address. You have to code your own server side of this because it's up to you what you do with this information and how you store it. In my case, I am using a php code to write into MySQL database.

Device also has a microSD card slot for memory card, which is used to log location history.

Case is 3D printed and is still work in progress. Once the design is finished, the source file will also be uploaded.

![image of a GPS tracker](https://raw.githubusercontent.com/sierramango/GPS_LTE_tracker/master/IMG_1889.jpg)

![charging circuit schematic](https://raw.githubusercontent.com/sierramango/GPS_LTE_tracker/master/charging_circuit.png)
