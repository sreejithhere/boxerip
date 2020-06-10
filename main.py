#!python
import os
import sys
import time
import datetime
from slack_functions import update_slack
from getip import get_external_ip
from pdb import set_trace


IP_CACHE = "C:\Temp\slackip\.current_ip"
SUCCESS_SLEEP_DELAY = 300
FAILURE_SLEEP_DELAY = 60
HEARTBEAT_INTERVAL = 900


def do_setup():
    if not os.path.exists(os.path.dirname(IP_CACHE)):
        os.makedirs(os.path.dirname(IP_CACHE))

def get_cached_ip():
    try:
        with open(IP_CACHE, 'r') as fp:
            ip = fp.read()
    except:
        ip = ''
    return ip 

def clear_cache():
    try:
        os.remove(IP_CACHE)
    except Exception as ex:
        print("Unable to remove cache file due to {}".format(ex))

def put_cached_ip(ip):
    try:
        with open(IP_CACHE, 'w') as fp:
            fp.write(ip)
    except Exception as e:
        print("Unable to write to cache - {}".format(e))

def heartbeat(last, force=False):
    diff = (datetime.datetime.now() - last).total_seconds()
    if force or diff > HEARTBEAT_INTERVAL:
        update_slack("UpdateIP Bot is alive at    {}".format(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")))
    else:
        print("Not sending heartbeat since only {} seconds since last heartbeat".format(diff))


def push_current_ip():
    do_setup()
    last_heartbeat = datetime.datetime.now()
    heartbeat(last_heartbeat, True)
    while(True):
        cached = get_cached_ip()
        new = get_external_ip()
        if not new:
            print("Unable to get external IP")
            time.sleep(FAILURE_SLEEP_DELAY)
            continue
        elif not cached or cached != new:
            print("Cached IP ({}) is different from cached IP ({}). Updating slack".format(cached, new))
            success = update_slack(new)
            if success:
                put_cached_ip(new)
                time.sleep(SUCCESS_SLEEP_DELAY)
            else:
                time.sleep(FAILURE_SLEEP_DELAY)
            continue
        else:
            print("Cached IP is same as current IP")
            heartbeat(last_heartbeat)
            last_heartbeat = datetime.datetime.now()
            time.sleep(SUCCESS_SLEEP_DELAY)

def pull_current_ip():
    pass

if __name__ == '__main__':
    print("Starting the application")
    ops = 'push'
    if len(sys.argv) > 1:
        ops = sys.argv[1].lower()
    if ops == 'push':
        push_current_ip()
    elif ops == 'pull':
        pull_current_ip()
    else:
        print("Sytax is 'python ./main.py push/pull")
        sys.exit(1)

        