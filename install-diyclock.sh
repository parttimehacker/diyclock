#/usr/bin/bash
#
# Script: install-diyclock.sh
# Author: parttimehacker 
# Date:   2019 
# 
# Purpose:fresh install script for Raspberry Pi 
# 
# Notes: get the latest packages and set up file sharing
# 
#!/bin/bash

echo "Welcome to DIY Installation Script diyclock"
echo "This script was modified from a script by LearnOpenCV.com"
echo "================================"
echo "copy and install diyclock.service"
echo cp *.py ../systemd
echo mkdir ../logs
sudo cp diyclock.service /lib/systemd/system/diyclock.service
sudo chmod 644 /lib/systemd/system/diyclock.service
sudo systemctl daemon-reload
sudo systemctl enable diyclock.service
echo "diyclock.service installation complete"
echo "Reboot recommended"
echo "================================"
echo
