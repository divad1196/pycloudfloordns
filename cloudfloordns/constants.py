# Default Name Servers

NS1 = "ns1.g02.cfdns.net"
NS2 = "ns2.g02.cfdns.biz"
NS3 = "ns3.g02.cfdns.info"
NS4 = "ns4.g02.cfdns.co.uk"

NS5 = "dns0.mtgsy.com"
NS6 = "dns1.name-s.net"
NS7 = "dns2.name-s.net"
NS8 = "dns3.mtgsy.com"
NS9 = "dns4.mtgsy.com"

MAIN_NAMESERVERS = [NS1, NS2, NS3, NS4]
ADDITIONAL_NAMESERVERS = [NS5, NS6, NS7, NS8, NS9]


NAMESERVERS = MAIN_NAMESERVERS
ALL_AMESERVERS = [
    *MAIN_NAMESERVERS,
    *ADDITIONAL_NAMESERVERS,
]
