# Building the AlarmDecoder appliance for the odroid-c4 board using Armbian Bionic LTS

## Summary

These files are used to build Armbian Bionic LTS disk image with the AlarmDecoder services pre installed to create an *AlarmDecoder webapp appliance* using an [odroid-c4](https://www.hardkernel.com/shop/odroid-c4/) board.

![Keypad Screenshot](http://github.com/nutechsoftware/alarmdecoder-webapp/raw/master/screenshot.png "Keypad Screenshot")


The odroid-c4 has several advantages over the Raspberry Pi.
* 3 TTL serial UARTS
* Lower power than Pi3B+
* ~Performance of the Pi4
* ~The heat profile of a Pi3B
* uSD or eMMC boot
* DC Wide input range 5.5V ~ 15.5V using standard 5.5mm DC connector
* IR receiver
* 4G DDR4 ram
* Gigabit Ethernet

## Installation
First prepare a build environment per this document.
 [Armbian: Developer-Guide Build Preperation](https://docs.armbian.com/Developer-Guide_Build-Preparation/)

Next place the files "customize-image.sh" and "config-alarmdecoder-webapp.conf" into the userpatches folder "./build/userpatches/".

To build the Armbian image from the ./build folder run this command. This can take several hours especially the first time it is run.
> ./compile.sh alarmdecoder-webapp
