#!/bin/bash

chmod +x $(pwd)/run.sh
crontab -e
# write out current crontab
crontab -l > cronfile
# echo new cron into cron file
echo "@reboot cd $(pwd) && $(pwd)/run.sh" >> cronfile
# install new cron file
crontab cronfile
rm cronfile