# allskypi
## Setup

````shell
sudo raspi-config
# set hostname to allskypi
````



set timezone
````shell
sudo timedatectl set-timezone Europe/Berlin
````

````shell
sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade
sudo apt install git php python3 fail2ban python3-pip ntpdate -y
pip3 install RPi.GPIO Adafruit-DHT flask python-telegram-bot ephem python-dotenv
````

````shell
cd /home/pi
git clone https://github.com/drevil75/allskypi.git
mv /home/pi/environment/allsky_template.env /home/pi/environment/allsky.env
nano /home/pi/environment/allsky.env

# edit the variables with your values/credentials
INFLUX_TOKEN=<access token of your influx db>
INFLUX_ORG=<bucket name>
INFLUX_BUCKET=allsky
INFLUX_URL="http://<url of your influxDB>:18086"
device_lat = <gps latitude 51.1234>
device_lng = <gps longitude 12.1234>
TELEGRAM_TOKEN=<token of yout telegram bot>
TELEGRAM_TO=<ID of the telegram recipient(s) - seperate with comma ... id1,id2,id3... >
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
# paste into the editor
0 */6 * * * ntpdate -s 192.168.1.1

# write CTRL+O and close CTRL+X the editor
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

open http://allskypi:8080 in your brwoser
