import json
import logging
import os
from typing import Dict, Iterable, List, Tuple

import requests
from ratelimit import RateLimitException, limits, sleep_and_retry

from .domain import Domains
from .groups import Groups
from .record import Record, Records
from .zone import Zone, Zones

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

DEFAULT_BASE_URL = "https://apiv2.mtgsy.net/api/v1"


class BaseClient:
    def __init__(
        self, username=None, apikey=None, url=DEFAULT_BASE_URL, throttling=True
    ) -> None:
        if not username:
            username = os.environ.get("CLOUDFLOOR_USERNAME", "").strip()
        if not username:
            raise Exception("username required")

        if not apikey:
            apikey = os.environ.get("CLOUDFLOOR_APIKEY", "").strip()
        if not apikey:
            raise Exception("apikey required")
        self._username = username
        self._apikey = apikey
        self._url = url.rstrip("/")
        self._throttling = throttling

    def _request(self, method, url, data=None, timeout=None):
        if not url.startswith("/"):
            raise Exception(
                f"url '{url}' is invalid: must be a path with a leading '/' "
            )
        if not data:
            data = {}
        request_data = {
            **data,
            "username": self._username,
            "apikey": self._apikey,
        }
        url = f"{self._url}{url}"
        error_message = "Unknown error"
        response = requests.request(
            method,
            url,
            headers=DEFAULT_HEADERS,
            data=json.dumps(request_data),
            allow_redirects=True,
            timeout=timeout,
        )
        res = response.json()
        error = res.get("error")
        if not error:
            error = res.get("message")
        if error:
            logging.debug(error)
            error_message = error
            if isinstance(error, dict):
                error_message = error.get("description", "Unknown error")
            if not isinstance(error_message, str):
                error_message = str(error_message)
            if "Too Many Requests" in error_message:
                raise RateLimitException(error_message, 10)
            raise Exception(error_message)
        return res.get("data")

    def _get(self, url, data=None, timeout=None, throttling=None):
        return self._request("GET", url, data=data, timeout=timeout)

    def _post(self, url, data=None, timeout=None, throttling=None):
        return self._request("POST", url, data=data, timeout=timeout)

    def _patch(self, url, data=None, timeout=None, throttling=None):
        return self._request("PATCH", url, data=data, timeout=timeout)

    def _delete(self, url, data=None, timeout=None, throttling=None):
        return self._request("DELETE", url, data=data, timeout=timeout)

    # https://stackoverflow.com/questions/401215/how-to-limit-rate-of-requests-to-web-services-in-python
    # @sleep_and_retry
    # @limits(calls=200, period=60)
    # def _limited_request(self, method, url, data=None, timeout=None):
    #     return self._request(method, url, data=data, timeout=timeout)

    @sleep_and_retry
    @limits(calls=120, period=60)
    def _limited_get(self, url, data=None, timeout=None):
        return self._get(url, data=data, timeout=timeout)

    @sleep_and_retry
    @limits(calls=30, period=60)
    def _limited_post(self, url, data=None, timeout=None):
        return self._post(url, data=data, timeout=timeout)

    @sleep_and_retry
    @limits(calls=60, period=60)
    def _limited_patch(self, url, data=None, timeout=None):
        return self._patch(url, data=data, timeout=timeout)

    @sleep_and_retry
    @limits(calls=30, period=60)
    def _limited_delete(self, url, data=None, timeout=None):
        return self._delete(url, data=data, timeout=timeout)

    def get(self, url, data=None, timeout=None, throttling=None):
        if throttling is None:
            throttling = self._throttling
        if throttling:
            return self._limited_get(url, data=data, timeout=timeout)
        return self._get(url, data=data, timeout=timeout)

    def post(self, url, data=None, timeout=None, throttling=None):
        if throttling is None:
            throttling = self._throttling
        if throttling:
            return self._limited_post(url, data=data, timeout=timeout)
        return self._post(url, data=data, timeout=timeout)

    def patch(self, url, data=None, timeout=None, throttling=None):
        if throttling is None:
            throttling = self._throttling
        if throttling:
            return self._limited_patch(url, data=data, timeout=timeout)
        return self._patch(url, data=data, timeout=timeout)

    def delete(self, url, data=None, timeout=None, throttling=None):
        if throttling is None:
            throttling = self._throttling
        if throttling:
            return self._limited_delete(url, data=data, timeout=timeout)
        return self._delete(url, data=data, timeout=timeout)


class Client(BaseClient):
    def __init__(
        self, username=None, apikey=None, url=DEFAULT_BASE_URL, throttling=True
    ) -> None:
        super().__init__(
            username=username, apikey=apikey, url=url, throttling=throttling
        )
        self.records = Records(self)
        self.zones = Zones(self)
        self.domains = Domains(self)
        self.groups = Groups(self)

    # @property
    # def domains(self) -> Zones:
    #     logging.warning(f"Attribute 'domains' in class '{Client}' is deprecated. Use 'zones' instead")
    #     return self.zones

    def yield_all_domains_records(self) -> Iterable[Tuple[Zone, List[Record]]]:
        domains = self.zones.list()
        for d in domains:
            records = self.records.list(d.domainname)
            yield d, records

    def all_domains_records(self) -> Dict[Zone, List[Record]]:
        return dict(self.yield_all_domains_records())
