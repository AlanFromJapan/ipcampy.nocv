#!/bin/bash

#get python an pip
sudo apt install python3-setuptools python3-pip --yes

#libs fo building
sudo apt install libavformat-dev libavdevice-dev python3-dev --yes
sudo apt install libjpeg-dev libtiff-dev zlibc zlib1g-dev --yes

#get flask and other libs
sudo python3 -m pip install -r requirements.txt


