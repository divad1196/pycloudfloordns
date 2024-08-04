import logging
import os

from cloudfloordns import Client

logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":
    # We can explicitly retrieve the credentials
    USERNAME = os.environ["CLOUDFLOOR_USERNAME"].strip()
    APIKEY = os.environ["CLOUDFLOOR_APIKEY"].strip()
    client = Client(USERNAME, APIKEY)

    # Or retrieve them implicitly
    client = Client()

    # # enabled_domains = client.domains.list(zone_enabled=True)
    # # not_enabled_domains = client.domains.list(zone_enabled=False)
    client.zones.enable_all()
