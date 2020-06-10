import os
import sys
import time
import datetime
import tempfile
from slack_functions import update_slack, get_from_slack
from getip import get_external_ip
from pdb import set_trace


# Location to save the last read IP address
IP_CACHE_FILE = "boxerip/.current_ip"
SUCCESS_SLEEP_DELAY = 300  # Every 5 minutes
FAILURE_SLEEP_DELAY = 123  # Every 2 minutes
HEARTBEAT_INTERVAL = 900   # Every 15 minutes

def get_ip_cache():
    # Joing the cache file name with the system temp folder
    return os.path.join(tempfile.gettempdir(), IP_CACHE_FILE)

def do_setup():
    # Create the temp folder if it does not exist
    if not os.path.exists(os.path.dirname(get_ip_cache())):
        os.makedirs(os.path.dirname(get_ip_cache()))

def get_cached_ip():
    '''
    Returns the cached IP
    '''
    try:
        with open(get_ip_cache(), 'r') as fp:
            ip = fp.read()
    except:
        ip = ''
    return ip 

def clear_cache():
    '''
    Clears the cache file
    '''
    try:
        os.remove(get_ip_cache())
    except Exception as ex:
        print("Unable to remove cache file due to {}".format(ex))

def put_cached_ip(ip):
    '''
    Saves the ip to the cache file
    '''
    try:
        with open(get_ip_cache(), 'w') as fp:
            fp.write(ip)
    except Exception as e:
        print("Unable to write to cache - {}".format(e))

def heartbeat(last, force=False):
    '''
    Sends a heartbeat message to the default channel

    Heartbeat message provides a check to make sure that the script is still running
    even when no IP change happened
    :param last: the last time when a hearbeat was sent
    :type last: datetime
    :param force: forces the function to send a hearbeat ignoring the last sent time
    :type force: bool
    :returns: True if a message was sent
    :rtype: bool
    '''
    diff = (datetime.datetime.now() - last).total_seconds()
    if force or diff > HEARTBEAT_INTERVAL:
        update_slack("UpdateIP Bot is alive at    {}".format(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")))
        return True
    else:
        print("Not sending heartbeat since only {} seconds since last heartbeat".format(diff))
        return False


def push_current_ip():
    '''
    Pushes the latest IP to slack

    If the latest detected IP is the same as the cached IP, then no message is sent
    '''
    do_setup()
    last_heartbeat = datetime.datetime.now()

    # Send a heartbeat on startup
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
                # Update the cache file with the new IP
                put_cached_ip(new)
                time.sleep(SUCCESS_SLEEP_DELAY)
            else:
                time.sleep(FAILURE_SLEEP_DELAY)
            continue
        else:
            print("Cached IP is same as current IP")
            if heartbeat(last_heartbeat):
                last_heartbeat = datetime.datetime.now()
            time.sleep(SUCCESS_SLEEP_DELAY)

def pull_current_ip():
    '''
    Gets the current IP from the default channel
    '''
    latest_ip = get_from_slack()
    return latest_ip

def save_ip_to_disk(latest_ip):
    print("Anujith will do this work")


if __name__ == '__main__':
    print("Starting the application")
    ops = 'push'
    if len(sys.argv) > 1:
        ops = sys.argv[1].lower()
    if ops == 'push':
        # Runs a while 1 loop to keep pushing the IP
        push_current_ip()
    elif ops == 'pull':
        latest_ip = pull_current_ip()
        if latest_ip:
            print("Latest IP is {}".format(latest_ip))
            save_ip_to_disk(latest_ip)
            sys.exit(0)
        else:
            print("Unable to get the latest IP")
            sys.exit(1)
    else:
        print("Sytax is 'python ./main.py push/pull")
        sys.exit(1)

        
