from slack import WebClient
from slack.errors import SlackApiError


BOT_TOKEN='xoxb-2358815231-1180219263748-3BbsdJWyAQNB9w52Jhml7bfP'
CHANNEL_NAME='boxerip'
CHANNEL_ID='C015GKF2B17'


def get_client():
    return WebClient(BOT_TOKEN)

def update_slack(message):
    client = get_client()
    try:
        resp = client.chat_postMessage(
            channel=CHANNEL_NAME,
            text=message)
    except SlackApiError as ex:
        print("Unable to update slack - {}".format(ex))
        return False
    return True

def get_from_slack():
    client = get_client()
