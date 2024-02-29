import os

from cloudfloordns import Client, Record

USERNAME = os.environ["CLOUDFLOOR_USERNAME"].strip()
APIKEY = os.environ["CLOUDFLOOR_APIKEY"].strip()

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


# The key is a type, the value is the records values
# The goal is to check the equality behaviour
IDENTITY_TESTS = [
    {
        "type": "A",
        "values": [
            "8.8.8.8",
            "8.8.8.8",
        ],
        "expected": 1,
    },
    {
        "type": "A",
        "values": [
            "8.8.8.8",
            "8.8.8.9",
        ],
        "expected": 2,
    },
    {
        "type": "CNAME",
        "values": [
            "hello-world",
            "hello-world",
        ],
        "expected": 1,
    },
    {
        "type": "CNAME",
        "values": [
            "hello-world",
            "goodbye-world",
        ],
        "expected": 2,
    },
    {
        "type": "TXT",
        "values": [
            "this is a test",
            "this is a test",
        ],
        "expected": 1,
    },
    {
        "type": "TXT",
        "values": [
            "this is a test",
            "this is another test",
        ],
        "expected": 2,
    },
]


client = Client(USERNAME, APIKEY)


result = True
for t in IDENTITY_TESTS:
    name = t.get("name", DEFAULT_NAME)
    domain = t.get("domain", DEFAULT_DOMAIN)
    type = t["type"]
    values = t["values"]
    expected = t["expected"]
    result &= test_identity(client, domain, name, type, values, expected)


if not result:
    print("Tests failed")
    exit(1)


list_res = client.records.list(domain)
garbage = [r for r in list_res if r.name == DEFAULT_NAME]
print(garbage)

# found = next((r for r in list_res if r.name == record.name), None)

# print(res.content.decode())

# rec = Record(
#     "myrecord",  # name
#     "A", # type
#     "8.8.8.8"  # DATA
# )


# res = create_record("mydomain.com", rec)
# print(res.content.decode())
