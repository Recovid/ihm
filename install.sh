#!/bin/bash

sudo apt-get install libatlas-base-dev libjpeg-dev
python3.7 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt

echo "setxkbmap fr" >> ~/.bashrc

sudo echo "dtoverlay=disable-bt" >> /boot/config.txt
sudo echo "enable_uart=1" >> /boot/config.txt
sudo echo "lcd_rotate=2" >> /boot/config.txt
sed -i -e 's/root=/console=serial0,115200 root=/' /boot/cmdline.txt

echo "Vous devez maintenant rebooter la raspberry"
