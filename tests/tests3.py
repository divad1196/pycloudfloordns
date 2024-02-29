import os

from cloudfloordns import Client

USERNAME = os.environ["CLOUDFLOOR_USERNAME"].strip()
APIKEY = os.environ["CLOUDFLOOR_APIKEY"].strip()

DEFAULT_DOMAIN = os.environ["CLOUDFLOOR_DEFAULT_DOMAIN"].strip()
DEFAULT_NAME = os.environ["CLOUDFLOOR_DEFAULT_NAME"].strip()

client = Client(USERNAME, APIKEY)
