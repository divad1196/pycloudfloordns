import logging
from typing import Dict, List

from cloudfloordns import Client
from cloudfloordns.models import Record, Redirect, Zone

logging.getLogger().setLevel(logging.INFO)


def get_redirect_records(client: Client) -> Dict[Zone, List[Record]]:
    """
    Return all records that are supposed to be redirection.
    If a redirect record exists, it does not mean the redirection works
    There might be falst positive => We need to get the effective redirections
    client.zones.raw_list_redirects(...)
    """
    return {
        zone: [r for r in records if r.is_redirect]
        for zone, records in client.yield_all_domains_records()
    }


def get_redirections(client: Client) -> Dict[Zone, List[Redirect]]:
    """
    Return all active redirections
    """
    zones = client.zones.list()
    zone_redirections = {z: client.zones.list_redirects(z.domainname) for z in zones}
    redirections = {
        z: redirects for z, redirects in zone_redirections.items() if redirects
    }
    return redirections


if __name__ == "__main__":
    client = Client()
    redirections_mapping = get_redirections(client)
    rules = sorted(
        (r for redirects in redirections_mapping.values() for r in redirects),
        key=lambda r: r.src,
    )

    print("Number of zones:", len(redirections_mapping))
    print("Number of redirections:", len(rules))

    for r in rules:
        print(f"{r.src} -> {r.dst}")
