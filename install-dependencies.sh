#!/bin/bash

#get python an pip
sudo apt-get install python3-setuptools python3-pip --yes

#get flask
sudo python3 -m pip install Flask

pip install av
pip install pillow

sudo apt-get install libavformat-dev libavdevice-dev --yes

