'''
Provides functions for interacting with slack
'''
import json
import os
import requests
import datetime
import re
from slack import WebClient
from slack.errors import SlackApiError

# Auth token for the bot.  This should be obtained from the
# slack apit pannel
# The bot should have the following scopes
#   channels:history
#   channels:read
#   chat:write
#   groups:history
#   groups:read
#   im:history
#   mpim:history
# The token should be set in the shell as a variable BOT_TOKEN
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Channel name and ID for the boxerip channel
CHANNEL_NAME='boxerip'
CHANNEL_ID='C015GKF2B17'
SLACK_URL = 'https://slack.com/api/'
IP_PATTERN = re.compile('^(\d{1,3}\.){3}\d{1,3}$')

# Maximum seconds before which we should consider the message history
# in the channel as stale.  This indicates that the boxer license
# computer did not update the channel recently
REQUIRED_FRESHNESS = 1000

def get_client():
    '''
    Returns the web client
    '''
    return WebClient(BOT_TOKEN)

def update_slack(message):
    '''
    Pushes the given message to the default channel
    :param message: message to push
    :type message: string
    :returns: success
    :rtype: bool
    '''
    client = get_client()
    try:
        resp = client.chat_postMessage(
            channel=CHANNEL_NAME,
            text=message)
    except SlackApiError as ex:
        print("Unable to update slack - {}".format(ex))
        return False
    return True

def _get_response_from_slack(cursor='', limit=10):
    '''
    Reads the messages from the default channel

    Slack read api supprts a cursor instance to handle pagination
    :param cursor: cursor which marks the last read position
    :type cursor: string
    :param limit: number of messages to be read in a single call
    :type limit: int
    :returns: json response from the api call
    :rtype: dict
    '''
    headers = {'content-type': 'x-www-form-urlencoded'}
    data = {'token': BOT_TOKEN,
            'channel': CHANNEL_ID,
            'limit': limit,
            'cursor': cursor}
    url = SLACK_URL + 'conversations.history'
    resp = requests.post(url, data, headers)
    resp_data = json.loads(resp.text)
    return resp_data

def _get_recursive_messages(limit=10):
    '''
    Recursively fetches messages from the default channel and yields them

    This function will keep calling read on the channel till all the messages
    are exhausted
    :param limit: number of messages to be read in a single call
    :type limit: int
    :returns: json response from the api call
    :rtype: dict
    '''
    cursor = ''
    has_more = True
    while has_more:
        current = _get_response_from_slack(cursor, limit)
        # This flag is set True by the API if there are more messages
        # unread in the channel after the last call
        has_more = current['has_more']
        try:
            cursor = current['response_metadata'].get('next_cursor', '')
            for message in current['messages']:
                yield message
        except:
            continue


def get_from_slack():
    '''
    Gets the latest IP from slack

    The function does not just returns the latest IP.  It makes sure that the
    IP is within the freshness period.  It does this by picking the timestamp
    of the last message in the slack, whether an IP or a heartbeat, and ensures
    that it is within the freshness period
    :returns: the latest valid IP
    :rtype: string
    '''
    latest_time = None
    detected_ip = ''
    # Store the current time to compare this with the last message time
    now = datetime.datetime.now()
    for message in _get_recursive_messages():
        # The value under ts is the timestamp format
        message_time = datetime.datetime.fromtimestamp(int(message['ts'].split('.')[0]))
        
        # Take only the time of the latest message
        latest_time = latest_time or message_time
        time_gap = (now - latest_time).total_seconds()
        message_text = message['text'].strip()
        if time_gap > REQUIRED_FRESHNESS:
            # The latest message time is older than the required freshness of 1000s
            print("The last message was {} seconds ago at {} - {}".format(
                time_gap, latest_time, message_text))
            break
        if IP_PATTERN.match(message_text):
            try:
                detected_ip = message_text
                break
            except GeneratorExit:
                pass
    return detected_ip


