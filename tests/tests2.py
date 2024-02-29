import os

from cloudfloordns import Client, Record

# USERNAME = os.environ["CLOUDFLOOR_USERNAME"].strip()
# APIKEY = os.environ["CLOUDFLOOR_APIKEY"].strip()

DEFAULT_DOMAIN = os.environ["CLOUDFLOOR_DEFAULT_DOMAIN"].strip()
DEFAULT_NAME = os.environ["CLOUDFLOOR_DEFAULT_NAME"].strip()


def test_identity(client, domain, name, type, values, expected):
    records = [
        Record(
            name=name,
            type=type,
            data=v,
        )
        for v in values
    ]
    for r in records:
        client.records.create(domain, r)
    list_res = client.records.list(domain)
    newly_created = [r for r in list_res if (r.name, r.type) == (name, type)]
    for r in newly_created:
        client.records.delete(domain, r.id)
    if len(newly_created) != expected:
        print(f"Expecting  {expected}, found {len(newly_created)}: {newly_created}")
        return False
    print("Test OK")
    return True


# Values retrieved from environment variables
# client = Client(USERNAME, APIKEY)
client = Client()

TESTS = [
    (f"{DEFAULT_NAME}1", "TXT", "hello world"),
    (f"{DEFAULT_NAME}2", "TXT", "hello world 2"),
    (f"{DEFAULT_NAME}3", "A", "8.8.8.8"),
    (f"{DEFAULT_NAME}4", "A", "8.8.8.9"),
]
records = [
    Record(
        name=name,
        type=type,
        data=data,
    )
    for (name, type, data) in TESTS
]
for r in records:
    client.records.create(DEFAULT_DOMAIN, r)

list_res = client.records.list(DEFAULT_DOMAIN)
matching = [(r, [x for x in list_res if r.is_same(x)]) for r in records]

result = all(len(found) == 1 for _, found in matching)
print(result)
