import logging
import os

from cloudfloordns import Client

logging.getLogger().setLevel(logging.INFO)


USERNAME = os.environ["CLOUDFLOOR_USERNAME"].strip()
APIKEY = os.environ["CLOUDFLOOR_APIKEY"].strip()

client = Client(USERNAME, APIKEY)

# We cannot manage groups on domains without a zone enabled
domains = client.domains.list(zone_enabled=True)
group = client.groups.get_by_name("Admin")

for d in domains:
    if group.id in d.group_ids:
        continue
    logging.info(
        f"Adding group '{group.name}' (ID: {group.id}) to domain {d.domainname} (ID: {d.id}, Groups: {d.group_ids})"
    )
    d.group_ids.append(group.id)
    client.domains.update(d)
