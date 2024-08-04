from . import sync
from .sync import (
    Client,
    client,
    domain,
    groups,
    record,
    zone,
)

__all__ = [
    "client",
    "domain",
    "groups",
    "record",
    "zone",
    "Client",
    "sync",
]
