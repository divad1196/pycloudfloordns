from . import client, domain, groups, record, zone
from .client import Client
from .domain import Domains
from .groups import Groups
from .record import Records
from .zone import Zones

__all__ = [
    "client",
    "domain",
    "groups",
    "record",
    "zone",
    "Client",
]
