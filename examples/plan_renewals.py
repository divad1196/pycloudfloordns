"""
This script extract the domains with their expiration date and renewal price
"""


import csv
from dataclasses import dataclass
from datetime import date
from functools import partial
from pathlib import Path
from typing import Optional

from cloudfloordns import Client
from cloudfloordns.models import Domain, TLDPrice

DEFAULT_DATE = date(1900, 1, 1)


@dataclass
class Renewal:
    domain: str
    expires: Optional[date]
    price: Optional[float]
    currency: str

    @property
    def expiration_month(self) -> Optional[date]:
        if not self.expires:
            return None
        return self.expires.replace(day=1)


def _find_price(domain: Domain, pricelist: list[TLDPrice]) -> Optional[TLDPrice]:
    found: Optional[TLDPrice] = None
    domainname: str = domain.domainname.lower()
    for p in pricelist:
        if not domainname.endswith(p.tld.lower()):
            continue
        if found is None or len(p.tld) > len(found.tld):
            found = p
            continue
    return found


client = Client()
domains = client.domains.list()

pricelist = client.domains.pricelist()
find_price = partial(_find_price, pricelist=pricelist)

renewals: list[Renewal] = []
for d in domains:
    tldprice = find_price(d)
    renewals.append(
        Renewal(
            d.domainname.strip().lower(),
            d.expires,
            tldprice.price if tldprice is not None else None,
            tldprice.currency if tldprice is not None else "",
        )
    )
renewals = sorted(renewals, key=lambda r: r.expires or DEFAULT_DATE)


output = Path(".secrets/domain_renewals.csv")
with output.open("w") as f:
    writer = csv.writer(f)
    writer.writerow(["Domain", "Expiration", "Price", "Currency"])
    writer.writerows(
        [
            r.domain,
            r.expires.isoformat() if r.expires else "?",
            r.price or "?",
            r.currency or "?",
        ]
        for r in renewals
    )
