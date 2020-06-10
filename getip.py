import os
import requests


def get_external_ip(external_site="http://icanhazip.com/"):
    try:
        ip = requests.get(external_site).text.strip()
    except Exception as e:
        print("Error while getting external IP - {}".format(e))
        ip = ''
    return ip
    
