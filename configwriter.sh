#!/usr/bin/env bash
# Put me in /etc/cron.hourly; chmod ug+rx
AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
VPC=Enter a VPCID here e.g. vpc-d633e6b3
TODAY=$(date +%F-%H)
LNK=$(readlink -f /etc/ssh/ssh_config)
/usr/local/bin/aws-ssh-config.py --private --white-list-region ${AZ:0:-1} --tags Name --vpc_id ${VPC} | tee /etc/ssh/${TODAY}_config > /dev/null
RES=$(cmp -s /etc/ssh/${TODAY}_config /etc/ssh/ssh_config)
if [ "$?" > 0 ]; then
  ln -fs /etc/ssh/${TODAY}_config /etc/ssh/ssh_config
  rm $LNK
fi
