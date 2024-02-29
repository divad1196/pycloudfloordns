from typing import List

from cloudfloordns.models import Group


class Groups:
    def __init__(self, client) -> None:
        self.client = client

    def list(self, timeout=None) -> List[Group]:
        url = "/manage/groups"
        res = self.client.get(
            url,
            timeout=timeout,
        )
        return [Group(**d) for d in res]

    def get(self, group_id, timeout=None):
        res = self.list(
            timeout=timeout,
        )
        return next((r for r in res if r.id == group_id), None)

    def get_by_name(self, name, timeout=None):
        res = self.list(
            timeout=timeout,
        )
        return next((r for r in res if r.name == name), None)
