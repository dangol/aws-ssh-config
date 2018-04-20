#!/usr/bin/env bash
# Put me in /etc/cron.hourly; chmod ug+rx
AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
TODAY=$(date +%F-%H)
/usr/local/bin/awsssh.py --private --white-list-region ${AZ:0:-1} --tags Name | tee /etc/ssh/${TODAY}_config > /dev/null
RES=$(cmp -s /etc/ssh/${TODAY}_config /etc/ssh/ssh_config || echo yes)
if [ "$RES" == yes ]; then
  if [ -h /etc/ssh/ssh_config ]; then rm /etc/ssh/ssh_config; fi
  ln -s /etc/ssh/${TODAY}_config /etc/ssh/ssh_config;
fi
