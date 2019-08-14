/boot/README.TXT

  AlarmDecoder network appliance image built notes using PiBakery.

FEATURES
  Generates a new unique https and sendmail tls key on first boot.

BUILD NOTES

  Original Image:
    2019-07-10-raspbian-buster-lite.img(md5:d363428c361e77965f2d03b9598fb579)

  Pi Bakery Recipe:
    /boot/AlarmDecoder_WebApp_PiBakery_Recipe.xml

  Pi Bakery every boot(/boot/PiBakery/everyBoot.sh):
     Place a file called newkeys.txt on the boot partition of the Raspberry
     Pi uSD with this image then reboot and new unique keys for https and
     sendmail TLS will be generated.

  Customization to compress image for distribution:
     This is not needed for building a personal image unless you wish to keep
     a compressed version for archival. In order to keep the disk small a
     modification was needed for the stock Raspbian resize script.

     Modify TARGET_END to a fixed size 5859375*512 = 3,000,000,000 bytes before
     the first boot of the Pi Bakery image. After the image is finished and it
     shuts down the uSD is placed into a Linux development system and the
     modification is then reverted back to the original so it will properly
     resize on the first full boot after image to a new uSD.

       /usr/lib/raspi-config/init_resize.sh
         -TARGET_END=$((ROOT_DEV_SIZE - 1))
         +TARGET_END=$((5859375))

     Modify /boot/cmdline.txt to force a disk resize by appending
     'quiet init=/usr/lib/raspi-config/init_resize.sh' to the end of
     /boot/cmdline.txt so the normal Raspbian resize process will happen on the
     next boot.

     Clear with 0x0h all unused space on the Linux partition using zerofree.
     This will help the image compress and keep any junk out of the image.
       Ex. zerofree /dev/sdX2

     Extract the image to a binary file and zip it.
       Ex. dd if=/dev/sdX of=PIBAKERY-AD2PIBOOT-RASPBIAN-XX-YYYYYY-YYYYMMDD.ZIP

EASY WIFI SETUP

   Place a file called wpa_supplicant.txt on the boot partition of the Raspberry
  Pi uSD with this image then reboot and it will copy that file to
  /etc/wpa_supplicant/ and replace the existing file.

Example wpa_supplicant.txt content.

  ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=«your_ISO-3166-1_two-letter_country_code»

network={
    ssid="«your_SSID»"
    psk="«your_PSK»"
    key_mgmt=WPA-PSK
}
