# photo_stuff
This repo holds the code on a radxa zero w3 with emmc and serverside code to handle photos with exif information

TODO:
 - [ ] create a server side script to move the photos to
 - [ ] create a server config
 - [ ] create a gphoto service to ?move? the files to the radxa and then to the 'server' 


WONT DO (for now):
 - [ ] ~~create ap mode if there are no ssid's configured~~
 - [ ] ~~create a web service to configure the radxa~~
 - [ ] ~~make it start/stop on the config on the sdcard~~

## AP mode

Install

```
apt-get install hostapd dnsmasq
```

After installing disable and stop the `hostapd` and `dnsmasq` 
services:

```
systemctl stop hostapd.service
systemctl disable hostapd.service

systemctl stop dnsmasq.service
systemctl disable dnsmasq.service
```

It can be enabled later when there are no ssids active or available. Will decide later.

