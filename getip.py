import os
import requests


def get_external_ip(external_site="http://icanhazip.com/"):
    '''
    Gets the external IP for computer

    Many computer connect to a router which is connected to the internet
    So the local IP is not the external IP of the router.  So we use and
    external service which provides a simple text external IP
    :param external_site: Site providing simple text external IP
    :type external_iste: string
    :returns: the external IP of the computer
    :rtype: string
    '''
    try:
        ip = requests.get(external_site).text.strip()
    except Exception as e:
        print("Error while getting external IP - {}".format(e))
        ip = ''
    return ip
    
