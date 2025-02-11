"""
    Check the contact information directly in the registry
    and compare it with
"""


import logging

from cloudfloordns import Client
from cloudfloordns.models import Contact, Domain

client = Client()

# Only updating contacts does not seem to work

NO_OWNER_NAME = "<no owner>"


def make_name(firstname, lastname) -> str:
    owner_name = f"{firstname or ''} {lastname or ''}".strip()
    return owner_name or NO_OWNER_NAME


def get_name(info):
    if isinstance(info, Contact):
        return make_name(info.firstname, info.lastname)
    if isinstance(info, Domain):
        return make_name(info.ownerfirstname, info.ownerlastname)
    raise NotImplementedError()


domains_data = client.domains.list()
domains = [d.domainname for d in domains_data]


for d in domains[:10]:
    try:
        registry_data = client.domains.registry_info(d)
        registrar_data = client.domains.get(d)
        # TODO: Compare that the information match on both sides

    # NOTE: "Slim Application Error" can be raised if an object is sent instead of a scalar (str, int, ...)
    except Exception as e:
        logging.error(e)
