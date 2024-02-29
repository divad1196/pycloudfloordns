import logging
import os

from cloudfloordns import Client

logging.getLogger().setLevel(logging.INFO)


USERNAME = os.environ["CLOUDFLOOR_USERNAME"].strip()
APIKEY = os.environ["CLOUDFLOOR_APIKEY"].strip()

client = Client(USERNAME, APIKEY)

# # enabled_domains = client.domains.list(zone_enabled=True)
# # not_enabled_domains = client.domains.list(zone_enabled=False)
client.domains.enable_all()
