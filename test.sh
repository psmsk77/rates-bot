#!/bin/bash

if ps uax | grep "[b]ot_v01.py";
then echo "Bot is working";
else echo "Bot has been REstarted" &&
source /home/user/bot_rate/venv/bin/activate &&
sudo python3 /home/user/bot_rate/bot_v01.py;
fi
