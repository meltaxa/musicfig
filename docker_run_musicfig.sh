#!/bin/bash -xv

if [[ "$1" = "local" ]]; then
  # This assumes you have built a docker image locally using the command:
  # sudo docker build -t musicfig:local .
  image="musicfig:local"
else
  image="meltaxa/musicfig"
fi

lego_usb_device=$(lsusb | grep LEGO)
lego_bus=$(echo $lego_usb_device | awk '{print $2}')
lego_device=$(echo $lego_usb_device | cut -d: -f1 | awk '{print $4'})

sudo docker run -v $(pwd):/config -p 5000:5000 --device=/dev/bus/usb/$lego_bus/$lego_device --device=/dev/snd $image
