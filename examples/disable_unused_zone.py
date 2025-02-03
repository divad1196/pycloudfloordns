import cloudfloordns as cf

DRY_RUN = True

ns = {ns.strip().strip(".") for ns in cf.constants.ALL_AMESERVERS}
client = cf.Client()

domains = client.domains.list()
ext_dns = [
    d
    for d in domains
    if d.nameserver and not ({ns.strip().strip(".") for ns in d.nameserver or []} & ns)
]
to_deactivate = [d for d in ext_dns if d.editzone != "0"]

print({ns for d in to_deactivate for ns in d.nameserver})
for domain in sorted(d.domainname for d in to_deactivate):
    print(domain)
    if not DRY_RUN:
        client.zones.disable(domain)
