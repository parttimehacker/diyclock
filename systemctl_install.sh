#!/bin/bash
sudo cp $1 /lib/systemd/system/$1
sudo chmod 644 /lib/systemd/system/$1
sudo systemctl daemon-reload
sudo systemctl enable $1 

