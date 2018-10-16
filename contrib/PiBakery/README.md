# PiBakery AlarmDecoder WebApp recipe

PiBakery is a program that allows super-easy presetup of Raspberry Pi SD cards. Customization is done using a Scratch-style interface, where each block represents a script to run on startup.

The process of building a new image can take several hours so we have made available a pre-built image on the AlarmDecoder.com downloads page. If you wish to build your own image with all of the latest patches and some customizations or want to configure the WiFi settings on an existing image then you first need to get PiBakery 2.0 installed on a computer with a uSD card reader.

## Setup PiBakery 2.0 https://www.pibakery.org/
* Currently the binary distributions of 2.0 is old and broken. Download the source master branch on github and unzip it to your desktop or preferred workspace. https://github.com/davidferguson/pibakery/archive/v2.0.0.zip

* Windows/macOS
 * download and install the latest nodjs from https://nodejs.org/en/download/
* Linux
 * Install from your distributions repository ex. '''sudo apt-get install nodejs''' or per your distributions howto for nodejs.

* Download Raspbian Stretch lite zip file and unzip the img file to your desktop or preferred workspace. https://www.raspberrypi.org/downloads/raspbian/ 2018-10-09-raspbian-stretch-lite.img

* Open a shell and go to the pibakery-master folder
  * Windows
    * Run the '''Node.js command prompt''' from programs.
    * cd C:\Users\foo\Desktop\pibakery-master\
  * Linux/macOS
    * open a shell
    * cd ~/Desktop/pibakery-master/
* install the PiBakery node app.
  * npm install
    * May need to run a few times if downloads fail or glitches happen.
* Lanuch the PiBakery app
  * npm start

## Building a new image with the latest patches
* Launch PiBakery 2.0 and Import AlarmDecoder_WebApp_PiBakery_Recipe.xml
* Select Write
  * SD Card: Pick the uSD card be sure it is correct all data will be lost.
  * Operating system: select the Raspbian image on your desktop or workspace ex. 2018-10-09-raspbian-stretch-lite.img.
  * Press the "Write" button.
* Once the disk is flashed place it into a Raspberry Pi that has a physical connection to the Internet and power it on. This process will take as much as an hour to complete. Once it is is done the Pi will shutdown.
* Now you can power the Pi back up and it will be running all of the AlarmDecoder web services and ser2sock. To complete the appliance install see the quick start guide here https://www.alarmdecoder.com/wiki/index.php/Getting_Started .

## Modify PiBakery AlarmDecoder WebApp image
* To add WiFi to an existing image made with PiBakery simply insert the pre-flashed uSD card into your workstation and run the PiBakery 2.0 app.
* Click on "Startup"
  * Click once on "On First Boot" to add to your recipe.
* Next click on "Network"
  * Click on "Setup WiFi" and drag and connect this block to "On First Boot"
  * Set your Wifi settings and your Country code to "US". note: all fields case sensitive.
Select "Other" and "Reboot" and connect this block to the "Setup WiFi" block.
* Click "Update" at the top Right menu and select the SD Card with the pre-loaded image you flashed earlier on it and click the "Update" button and select the uSD disk.



Updates and more information on this project can be found on [the AlarmDecoder.com wiki](https://www.alarmdecoder.com/wiki/index.php/PiBakery).
