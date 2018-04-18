aws-ssh-config
======

Description
---

A very simple script that queries the AWS EC2 API with boto and generates a SSH config file ready to use. 
There are a few similar scripts around but I couldn't find one that would satisfy all my wish list:

- Connect to all regions at once
- Do AMI -> user lookup (regexp-based)
- Support public/private IP addresses (for VPNs and VPCs)
- Support multiple instances with same tags (e.g. autoscaling groups) and provide an incremental count for duplicates based on instance launch time
- Support multiple customizable tags concatenations in a user-provided order
- Support region (with AZ) in the host name concatenation
- Properly leverage tab completion

Usage
---

This assumes boto is installed and configured. Also, private ssh keys must be copied under `~/.ssh/`

Supported arguments:

```
usage: aws-ssh-config.py [-h] [--default-user DEFAULT_USER] [--keydir KEYDIR]
                         [--no-identities-only] [--prefix PREFIX] [--private]
                         [--profile PROFILE] [--region]
                         [--strict-hostkey-checking] [--tags TAGS]
                         [--user USER]
                         [--white-list-region WHITE_LIST_REGION [WHITE_LIST_REGION ...]]

optional arguments:
  -h, --help            show this help message and exit
  --default-user DEFAULT_USER
                        Default ssh username to use if it can't be detected
                        from AMI name
  --keydir KEYDIR       Location of private keys
  --no-identities-only  Do not include IdentitiesOnly=yes in ssh config; may
                        cause connection refused if using ssh-agent
  --prefix PREFIX       Specify a prefix to prepend to all host names
  --private             Use private IP addresses (public are used by default)
  --profile PROFILE     Specify AWS credential profile to use
  --region              Append the region name at the end of the concatenation
  --ssh-key-name        Override the ssh key to use
  --strict-hostkey-checking
                        Do not include StrictHostKeyChecking=no in ssh config
  --tags TAGS           A comma-separated list of tag names to be considered
                        for concatenation. If omitted, all tags will be used
  --user USER           Override the ssh username for all hosts
  --white-list-region WHITE_LIST_REGION [WHITE_LIST_REGION ...]
                        Which regions must be included. If omitted, all
                        regions are considered
```

By default, it will name hosts by concatenating all tags:

```
dan@bastion-test:~$ python awsssh.py --private --white-list-region us-west-2 --tags Name > ~/.ssh/config or /etc/ssh/ssh_config
dan@bastion-test:~$ cat ~/.ssh/config
Host dev-worker-1
  HostName 172.2.3.1
    
Host dev-worker-2
  HostName 172.2.3.2
    
Host deployr
  HostName 172.2.3.3
  ForwardAgent yes