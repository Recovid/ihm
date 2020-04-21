#!/bin/bash

sudo apt-get install libatlas-base-dev libjpeg-dev
python3.7 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt

echo "setxkbmap fr" >> ~/.bashrc

echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt
echo "enable_uart=1" | sudo tee -a /boot/config.txt
echo "lcd_rotate=2" | sudo tee -a /boot/config.txt
sudo sed -i -e 's/root=/console=serial0,115200 root=/' /boot/cmdline.txt

echo "Vous devez maintenant rebooter la raspberry"
