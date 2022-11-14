# allskypi
## Setup

````shell
sudo raspi-config
````
- set hostname to allskypi


set timezone
````shell
sudo timedatectl set-timezone Europe/Berlin
````

sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade
sudo apt install git php python3 fail2ban python3-pip ntpdate -y
pip3 install RPi.GPIO Adafruit-DHT flask python-telegram-bot ephem python-dotenv
````

````shell
git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
cd RPi_Cam_Web_Interface
cd bin
mv raspimjpeg raspimjpeg-buster
mv raspimjpeg-stretch raspimjpeg
cd ..
./install.sh
cd $HOME

rm -rf RPi_Cam_Web_Interface

sudo chmod 777 /var/www/html/index.html
````

````shell
# timeserver is the local router (fritzbox)
sudo crontab -e
@reboot ntpdate -s 192.168.1.1
0 */6 * * * ntpdate -s 192.168.1.1
````

create service for python script
````shell
sudo nano /etc/systemd/system/allsky.service

# paste into the editor
# ---------------
[Unit]
Description=allsky dome raspi
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/allskypi/
ExecStart=python3 tempControl.py
Restart=always

[Install]
WantedBy=multi-user.target
# -----------

````

ctrl+o to save
ctrl+x to close nano

```` shell
sudo systemctl daemon-reload && sudo systemctl enable allsky && sudo systemctl start allsky
````

http://<ip or name>:8080
