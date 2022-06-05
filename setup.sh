#!/bin/bash

#creates the user in the Raspberry pi
sudo adduser webuser

#make user forbiddent to log in 
sudo passwd -l webuser

