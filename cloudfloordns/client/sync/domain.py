# from dataclasses import dataclass, field
from collections import ChainMap
from typing import List, Optional, Union

from cloudfloordns.models import Contact, Domain, DomainPayload

DEFAULT_PRIMARY_NS = "ns1.g02.cfdns.net"
DEFAULT_LIMIT = 99999


class Domains:
    def __init__(self, client) -> None:
        self.client = client

    def raw_list(self, limit=None, offset=None, timeout=None) -> List[Domain]:
        """
        List all domains
        """
        data = {"limit": limit or DEFAULT_LIMIT}
        if offset:
            data["offset"] = offset
        url = "/domain"
        return self.client.get(
            url,
            data=data,
            timeout=timeout,
        )

    def list(self, limit=None, offset=None, timeout=None) -> List[Domain]:
        """
        List all domains
        """
        res = self.raw_list(limit=limit, offset=offset, timeout=timeout)
        return [Domain.model_validate(d) for d in res]

    def get_by_name(self, domainname, zone_enabled=None, timeout=None):
        res = self.list(
            zone_enabled=zone_enabled,
            timeout=timeout,
        )
        return next((r for r in res if r.domainname == domainname), None)

    def delete(self, domain: str, timeout=None):
        url = f"/domain/{domain}/delete_domain"
        return self.client.delete(
            url,
            timeout=timeout,
        )

    def raw_get(self, domain, timeout=None) -> Domain:
        url = f"/domain/{domain}"
        return self.client.get(
            url,
            timeout=timeout,
        )

    def get(self, domain, timeout=None) -> Domain:
        res = self.raw_get(domain, timeout=timeout)
        return Domain.model_validate(res)

    def raw_register(self, payload: DomainPayload, timeout=None) -> dict:
        """
        This will register a domain on CloudfloorDNS.
        The registration can be cancelled during a short period (to be confirmed)
        """
        url = "/domain"
        return self.client.post(
            url,
            data=payload.model_dump(by_alias=True),
            timeout=timeout,
        )

    def raw_registry_info(self, domain, timeout=None) -> dict:
        url = f"/domain/{domain}/get_registry_info"
        return self.client.get(
            url,
            timeout=timeout,
        )

    def registry_info(self, domain, timeout=None) -> Domain:
        """
        Return the data currently stored in the registry.
        NOTE:
        - The result may differ from `get` method (e.g. if the data push failed)
        - This is not similar as a WHOIS command since it retrieves redacted data as well
        """
        res = self.raw_registry_info(domain, timeout=timeout)
        return Domain.model_validate(res)

    def raw_status(self, domain, timeout=None) -> dict:
        url = f"/domain/{domain}/status"
        return self.client.get(
            url,
            timeout=timeout,
        )

    def raw_update(
        self, domain: str, payload: Union[Domain, DomainPayload], timeout=None
    ):
        if isinstance(payload, Domain):
            payload = payload.register_payload()
        # print(f"Trying to update domain {domain} with payload:\n{json.dumps(payload, indent=4)}")
        url = f"/domain/{domain}"
        data = payload.dump_for_update()
        return self.client.patch(
            url,
            data=data,
            timeout=timeout,
        )

    # Only updating contacts does not seem to work
    def update_contact(
        self,
        domain: str,
        owner: Optional[Contact] = None,
        admin: Optional[Contact] = None,
        tech: Optional[Contact] = None,
        bill: Optional[Contact] = None,
        timeout=None,
    ):
        """
        This method works according to the documentation, but some required parameters might be missing.
        """
        converted = (
            d
            for d in (
                owner and owner.as_owner(),
                admin and admin.as_admin(),
                tech and tech.as_tech(),
                bill and bill.as_bill(),
            )
            if d
        )
        payload = dict(ChainMap(*converted))
        # print(f"Trying to update domain {domain} with payload:\n{json.dumps(payload, indent=4)}")
        url = f"/domain/{domain}"
        return self.client.patch(
            url,
            data=payload,
            timeout=timeout,
        )
