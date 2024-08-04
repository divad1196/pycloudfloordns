import logging
import os

from cloudfloordns import Client

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    USERNAME = os.environ["CLOUDFLOOR_USERNAME"].strip()
    APIKEY = os.environ["CLOUDFLOOR_APIKEY"].strip()

    client = Client(USERNAME, APIKEY)

    ADMIN_GROUPNAME = "Admin"
    # We cannot manage groups on domains without a zone enabled
    domains = client.zones.list()
    group = client.groups.get_by_name(ADMIN_GROUPNAME)

    if group is None:
        logging.error(f"Group '{ADMIN_GROUPNAME}' does not exist")
        exit(1)

    for d in domains:
        if d.group_ids is None:
            d.group_ids = []
        elif group.id in d.group_ids:
            continue
        logging.info(
            f"Adding group '{group.name}' (ID: {group.id}) to domain {d.domainname} (ID: {d.id}, Groups: {d.group_ids})"
        )
        d.group_ids.append(group.id)
        client.zones.update(d)
