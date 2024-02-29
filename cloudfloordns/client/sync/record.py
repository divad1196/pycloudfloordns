# from dataclasses import dataclass, field
from typing import List

from cloudfloordns.models import Record


class Records:
    def __init__(self, client) -> None:
        self.client = client

    def create(self, domain: str, record: Record, timeout=None):
        url = f"/dns/zone/{domain}/record"
        return self.client.post(
            url,
            data=record.model_dump(),
            timeout=timeout,
        )

    def update(self, domain: str, record_id: str, record: Record, timeout=None):
        url = f"/dns/zone/{domain}/record/{record_id}"
        return self.client.patch(
            url,
            data=record.model_dump(exclude_unset=True),
            timeout=timeout,
        )

    def delete(self, domain: str, record_id: str, timeout=None):
        url = f"/dns/zone/{domain}/record/{record_id}"
        return self.client.delete(
            url,
            timeout=timeout,
        )

    def raw_list(self, domain: str, timeout=None) -> List[dict]:
        url = f"/dns/zone/{domain}/record"
        try:
            return self.client.get(
                url,
                timeout=timeout,
            )
        except Exception as e:
            if "No record available for this domain" in str(e):
                return []
            raise

    def list(self, domain: str, timeout=None) -> List[Record]:
        res = self.raw_list(domain, timeout=timeout)
        return [Record(**d) for d in res]

    def raw_get(self, domain: str, record_id, timeout=None):
        res = self.raw_list(
            domain,
            timeout=timeout,
        )
        return next((r for r in res if r["id"] == record_id), None)

    def get(self, domain: str, record_id, timeout=None):
        res = self.list(
            domain,
            timeout=timeout,
        )
        return next((r for r in res if r.id == record_id), None)
