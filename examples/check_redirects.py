import json
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import urllib3
from pydantic import BaseModel, TypeAdapter

from cloudfloordns import Client, Record, Redirect, Zone

RECORDS_CACHE_FILE = Path(".secrets/all_records.json")
REDIRECT_CACHE_FILE = Path(".secrets/all_redirects.json")

client = Client()

SerializedMapping = TypeAdapter(List[Tuple[Zone, List[Record]]])
SerializedRedirects = TypeAdapter(Dict[str, List[Redirect]])

# records_mapping = client.all_domains_records()
# domain = domains_failed_lookup


def all_domains_records(client: Client, use_cache=True):
    file = RECORDS_CACHE_FILE
    if use_cache and file.is_file():
        try:
            serialized = json.loads(file.read_text())
            records_mapping = dict(SerializedMapping.validate_python(serialized))
            return records_mapping
        except Exception as e:
            print(f"An error occured when trying to read file {file}:\n{e}")
            print("Retrieving the data from the API")
    records_mapping = client.all_domains_records()
    serialized = [
        (z.model_dump(), [r.model_dump() for r in records])
        for z, records in records_mapping.items()
    ]
    with open(file, "w") as f:
        json.dump(serialized, f, indent=4)
    return records_mapping


def all_redirect_targets(client: Client, zones, use_cache=True):
    file = REDIRECT_CACHE_FILE
    if use_cache and file.is_file():
        try:
            serialized = json.loads(file.read_text())
            data = SerializedRedirects.validate_python(serialized)
            return data
        except Exception as e:
            print(f"An error occured when trying to read file {file}:\n{e}")
            print("Retrieving the data from the API")
    targets = {}
    for z in zones:
        _zone_targets = client.zones.list_redirects(z)
        if _zone_targets:
            targets[z] = _zone_targets
    serialized = {
        z: [r.model_dump() for r in redirects] for z, redirects in targets.items()
    }
    with open(file, "w") as f:
        json.dump(serialized, f, indent=4)
    return targets


def record_key(zone: str, record: Record):
    key = record.name.strip()
    if not key.endswith("."):
        key = f"{key}.{zone}"
    return key.lower()


class Redirection(BaseModel):
    zone: Zone
    key: str
    record: Optional[Record]
    redirection: Optional[Redirect]


DEFAULT_TIMEOUT = 15


def simplify_url(url):
    return url.lower().removeprefix("http://").removeprefix("https://").rstrip("/.")


def get_all_urls(url, timeout=DEFAULT_TIMEOUT):
    response = requests.get(url, allow_redirects=True, timeout=timeout)
    urls = [r.url for r in response.history] + [response.url]
    return urls


def _check_redirect(source, target, timeout=DEFAULT_TIMEOUT):
    try:
        if not source.startswith(("http://", "https://")):
            source = f"https://{source}"
        urls = get_all_urls(source, timeout)
        target = simplify_url(target)
        for u in urls:
            if target in simplify_url(u):
                return urls, "working"
        return urls, "wrong_redirection"
    except requests.exceptions.ConnectTimeout:
        return None, "timeout"
    except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError):
        return None, "not_working"
    except requests.RequestException:
        return None, "maybe"


# def check_redirect(source, target, timeout=DEFAULT_TIMEOUT):
#     source = simplify_url(source)
#     urls, status = _check_redirect(f"https://{source}", target, timeout=timeout)
#     # HTTPS might not work and fail => Retry with HTTP
#     if status != "working":
#         urls, status = _check_redirect(f"http://{source}", target, timeout=timeout)
#     # There is a difference when we add a trailing "/" in the url
#     if status != "working":
#         urls, status = _check_redirect(f"http://{source}/", target, timeout=timeout)
#     return urls, status


def check_redirect(source, target, timeout=DEFAULT_TIMEOUT):
    simplified_source = simplify_url(source)

    source = f"https://{simplified_source}"
    urls, status = _check_redirect(source, target, timeout=timeout)
    # HTTPS might not work and fail => Retry with HTTP
    if status != "working" and (not urls or len(urls) < 2):
        source = f"http://{simplified_source}"
        urls, status = _check_redirect(source, target, timeout=timeout)
    # There is a difference when we add a trailing "/" in the url
    if status != "working" and (not urls or len(urls) < 2):
        source = f"http://{simplified_source}/"
        urls, status = _check_redirect(source, target, timeout=timeout)
    return source, urls, status


def worker(redirect: Redirection):
    """
    Given a redirection, check if by targetting the redirection source
    if we reach at some point the defined target.
    NOTE: The target might itself do a redirection. We can therefore not only check the final url.
    """
    if redirect.redirection is None:
        raise Exception()
    source, target = redirect.key, redirect.redirection.dst
    source, urls, status = check_redirect(source, target)
    return redirect, source, target, urls, status


def check_redirects(redirections: List[Redirection]):
    with ThreadPool(len(redirections)) as pool:
        results = pool.map(worker, redirections)
    return results


def filter_parked(to_check, parked_domains):
    to_check = {name.strip().lower() for name in to_check}
    all_parked = {z.domainname.strip().lower() for z in parked_domains}
    parked, used = (set(to_check) & all_parked, set(to_check) - all_parked)
    return parked, used


def filter_externally_managed(client, to_check):
    domains = [client.domains.get(d) for d in sorted(to_check)]
    externally_managed = []
    locally_managed = []
    for d in domains:
        name = d.domainname
        if d.is_externally_managed:
            externally_managed.append(name)
        else:
            locally_managed.append(name)
    return externally_managed, locally_managed


###################################################################################

all_records_mapping = all_domains_records(client, use_cache=True)
used_domains = {}
parked_domains = []
for domain, records in all_records_mapping.items():
    _recs = [r for r in records if not (r.is_standard or r.is_redirect)]
    if _recs:
        used_domains[domain] = _recs
    else:
        parked_domains.append(domain)

redirects = {}
types = set()
for z, records in all_records_mapping.items():
    _zone_redirects = []
    for r in records:
        types.add(r.type)
        if r.is_redirect:
            _zone_redirects.append(r)
    if _zone_redirects:
        redirects[z] = _zone_redirects

all_targets = all_redirect_targets(
    client, [z.domainname for z in redirects], use_cache=True
)


# List that link a redirect to its record
zone_redirect_record = [
    # zone, key, record, redirect
]
for z, zone_records in redirects.items():
    zone_name = z.domainname
    zone_targets = all_targets.get(zone_name) or []

    # The usual scenario is to have either 1 target or 1 record
    # In this case, the association is straight forward
    # NOTE: it is still possible that the matching are wron
    #   But we only try to make the association for now
    if len(zone_targets) == 1:
        red = zone_targets[0]
        for rec in zone_records:
            key = record_key(zone_name, rec)
            zone_redirect_record.append(
                Redirection(
                    zone=z,
                    key=key,
                    record=rec,
                    redirection=red,
                )
            )
        continue
    if len(zone_records) == 1:
        rec = zone_records[0]
        key = record_key(zone_name, rec)
        for red in zone_targets:
            zone_redirect_record.append(  # noqa: PERF401
                Redirection(
                    zone=z,
                    key=key,
                    record=rec,
                    redirection=red,
                )
            )
        continue

    # Prepare map to consolidate both target and record information
    _rec_map = {record_key(zone_name, r): r for r in zone_records}
    _redirect_map = {simplify_url(r.name): r for r in zone_targets}
    # Group elements with the same keys from both map
    common_keys = set(_rec_map) & set(_redirect_map)
    for k in common_keys:
        rec, red = _rec_map.pop(k, None), _redirect_map.pop(k, None)
        zone_redirect_record.append(
            Redirection(
                zone=z,
                key=k,
                record=rec,
                redirection=red,
            )
        )
    # Create entries for element without match
    for k, rec in _rec_map.items():
        zone_redirect_record.append(
            Redirection(
                zone=z,
                key=k,
                record=rec,
                redirection=None,
            )
        )
    for k, red in _redirect_map.items():
        zone_redirect_record.append(
            Redirection(
                zone=z,
                key=k,
                record=None,
                redirection=red,
            )
        )

zone_redirect_record.sort(key=lambda r: (r.zone.domainname, r.key))

# Filter out the broken redirections (without record or without target)
missing_records = [t for t in zone_redirect_record if not t.record]
missing_redirect = [t for t in zone_redirect_record if not t.redirection]
redirections = [t for t in zone_redirect_record if t.record and t.redirection]

# for r in redirections:
#     print(f"{r.key} -> {r.redirection.dst}")

#######################################################
########## Check redirection availability #############
#######################################################

# Check if a redirection is active or not and
# if it works as expected
results = check_redirects(redirections)

grouped = {}
for redirect, source, target, urls, status in results:
    g = grouped.setdefault(status, [])
    g.append((redirect, source, target, urls))

# Print statistics
for k, v in grouped.items():
    print(f"{k}: {len(v)}")


# These redirections exists but reach nothing
not_working = sorted(t[1] for t in grouped["not_working"])

working_redirections = grouped.get("working") or []
print("Working redirections:")
for redirect, source, target, urls in working_redirections:
    usage = "<unknown>"
    name = redirect.zone.domainname
    if name in used_domains:
        usage = "USED"
    elif name in parked_domains:
        usage = "PARKED"
    print(f"{redirect.zone.domainname} (usage: {usage}): {source} -> {target}")

# # print(json.dumps([r.model_dump() for r in redirects[domain]], indent=4))

# # records = client.records.list(domain)
# # for r in client.records.list(domain):
# #     print(r.type, r.data, r.is_redirect)
