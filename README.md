# Raspberry PinWeb
## _Control GPIO pin's output via web interface, lan api or telegram bot_

This is a simple web app that allows you to switch on/off GPIO pins using webpage or additional telegram bot. Also wide schedule or temperature/humidity triggers can be used (yes, it supports dht11/21/22 sensor). All this easy to set up in comfortable  admin web-panel. Supports English and Russian language.
## Features
- Set up pins (name, ordering, etc.) and control them remotely from lan
- Set up telegram bot (just token and your id) and control pins form anywhere
- Set up sheduled pin tasks in admin panel and enable-disable them remotely 
- Connect  sensor to gpio4 (board7) - see actual data and set up pin triggers

All this features (except basic web app) can be easy disabled in settings if you don't need them.

App uses Django's built-in devserver with forced single-thread mode, to avoid possibly conflicts with pin commands. Works fast enough.

Usage with full mode (app and 3 background processes) ~ 35Mb RAM

## Installation

Requires installed locales ru_RU.UTF-8 and/or en_US.UTF-8 (you can install them in raspi-config)

Also don't forget set up timezone (in raspi-config)

After that reboot and start to install

Tested on PiZero, Pi4B (Raspbian OS) and PC (Ubuntu 20.04)
```
cd ~/
wget https://github.com/nallan-dev/PinWeb/archive/master.zip
unzip master.zip
rm master.zip
mv PinWeb-master/ PinWeb
cd PinWeb
```

PinWeb requires to run just python3,7+ and some pip-libraries.


```sudo apt update```

```sudo apt install python3-pip```

```sudo apt-get install python3-venv```

With some extras for paspberry pi:
- for pins and DHT sensor support:
```sudo apt install pigpio python-pigpio python3-pigpio```

Make venv then install python dependencies and start the app:
(if you want to test this app on PC - use python3.7+_requirements_PC.txt)

```
python3 -m venv ../pin_web_env
source ../pin_web_env/bin/activate
pip install -r python3.7+_requirements_Pi.txt
```

Then check settings, set up appropriate for you:

```
nano main/settings.py
```

If you test this app on PC, don't forget to set FAKE_GPIO to True.
Then save changes, close settings.py (cntrl+o, then cntrl+x for nano)
And start the app (may take several seconds to start):

```
python run_app.py
```
If you see message like:
Django version 3.1.5, using settings 'main.settings'
Starting development server at http://0.0.0.0:8080/

So app is working and you can check it  with browser.
To stop app push cntrl+c keyboard interrupt (maybe several times)

Admin panel - User admin password 123454321
## Run app as service

Open systemctl sample:
```
nano systemctl_samples/PinWeb.service
```
Make sure that params WorkingDirectory and ExecStart is valid for your folders.
For virtual enviroment it must looks like:
ExecStart=/home/pi/pin_web_env/bin/python run_app.py

If all correct, then:

```
sudo cp systemctl_samples/PinWeb.service /etc/systemd/system/PinWeb.service
sudo systemctl daemon-reload
```
Now you can control this app like:

sudo systemctl enable PinWeb  # add to autostart on boot

sudo systemctl start PinWeb

sudo systemctl stop PinWeb

sudo systemctl restart PinWeb

sudo systemctl disable PinWeb  # remove from autostart after boot

sudo systemctl status PinWeb

Restart required after any changes in settings.py or changing bot token via admin panel.

## Api

It's very simple - you can get all information about configured pins (and schedules etc.) in JSON by GET '/get_report' url. To make action just send POST to '/' with data:
- state=1 (or 0) pin state and
- board_num=int (pin board num);

or

- state=1 (or 0) state and
- sched_id=int (schedule task id);

or

- state=1 (or 0) state and
- temper_id=int (sensor task id).

POST action returns in response renewed JSON same as '/get_report'

The end

