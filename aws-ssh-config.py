#!/usr/bin/env python

import argparse
import re
import sys
import time
import boto.ec2


AMI_NAMES_TO_USER = {
    'amzn' : 'ec2-user',
    'ubuntu' : 'ubuntu',
    'CentOS' : 'root',
    'DataStax' : 'ubuntu',
    'CoreOS' : 'core'
}

AMI_IDS_TO_USER = {
    'ami-ada2b6c4' : 'ubuntu'
}

AMI_IDS_TO_KEY = {
    'ami-ada2b6c4' : 'custom_key'
}

BLACKLISTED_REGIONS = [
    'cn-north-1',
    'us-gov-west-1'
]


def generate_id(instance, tags_filter, region):
    instance_id = ''

    if tags_filter is not None:
        for tag in tags_filter.split(','):
            value = instance.tags.get(tag, None)
            if value:
                if not instance_id:
                    instance_id = value
                else:
                    instance_id += '-' + value
    else:
        for tag, value in instance.tags.iteritems():
            if not tag.startswith('aws'):
                if not instance_id:
                    instance_id = value
                else:
                    instance_id += '-' + value

    if not instance_id:
        instance_id = instance.id

    if region:
        instance_id += '-' + instance.placement

    return instance_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--default-user', help='Default ssh username to use if it can\'t be detected from AMI name')
    parser.add_argument('--keydir', default='~/.ssh/', help='Location of private keys')
    parser.add_argument('--no-identities-only', action='store_true', help='Do not include IdentitiesOnly=yes in ssh config; may cause connection refused if using ssh-agent')
    parser.add_argument('--prefix', default='', help='Specify a prefix to prepend to all host names')
    parser.add_argument('--private', action='store_true', help='Use private IP addresses (public are used by default)')
    parser.add_argument('--profile', help='Specify AWS credential profile to use')
    parser.add_argument('--region', action='store_true', help='Append the region name at the end of the concatenation')
    parser.add_argument('--ssh-key-name', default='', help='Override the ssh key to use')
    parser.add_argument('--strict-hostkey-checking', action='store_true', help='Do not include StrictHostKeyChecking=no in ssh config')
    parser.add_argument('--tags', help='A comma-separated list of tag names to be considered for concatenation. If omitted, all tags will be used')
    parser.add_argument('--user', help='Override the ssh username for all hosts')
    parser.add_argument('--white-list-region', default='', help='Which regions must be included. If omitted, all regions are considered', nargs="+")

    args = parser.parse_args()

    instances = {}
    counts_total = {}
    counts_incremental = {}
    amis = AMI_IDS_TO_USER.copy()

    print "# Generated on " + time.asctime(time.localtime(time.time()))
    print "# " + " ".join(sys.argv)
    print "# "
    print

    for region in boto.ec2.regions():
        if args.white_list_region and region.name not in args.white_list_region:
            continue
        if region.name in BLACKLISTED_REGIONS:
            continue
        if args.profile:
            conn = boto.ec2.connect_to_region(region.name, profile_name=args.profile)
        else:
            conn = boto.ec2.connect_to_region(region.name)

        for instance in conn.get_only_instances():
            if instance.state != 'running':
                continue

            if instance.platform == 'windows':
                continue

            if instance.key_name is None:
                continue

            if instance.launch_time not in instances:
                instances[instance.launch_time] = []

            instances[instance.launch_time].append(instance)

            instance_id = generate_id(instance, args.tags, args.region)

            if instance_id not in counts_total:
                counts_total[instance_id] = 0
                counts_incremental[instance_id] = 0

            counts_total[instance_id] += 1

    for k in sorted(instances):
        for instance in instances[k]:
            if args.private:
                if instance.private_ip_address:
                    ip_addr = instance.private_ip_address
            else:
                if instance.ip_address:
                    ip_addr = instance.ip_address
                elif instance.private_ip_address:
                    ip_addr = instance.private_ip_address
                else:
                    sys.stderr.write('Cannot lookup ip address for instance %s, skipped it.' % instance.id)
                    continue

            instance_id = generate_id(instance, args.tags, args.region)

            if counts_total[instance_id] != 1:
                counts_incremental[instance_id] += 1
                instance_id += '-' + str(counts_incremental[instance_id])

            hostid = args.prefix + instance_id
            hostid = hostid.replace(' ', '_') # get rid of spaces

            if instance.id:
                print '# id: ' + instance.id
            print 'Host ' + hostid
            print '    HostName ' + ip_addr
            print


if __name__ == '__main__':
    main()
