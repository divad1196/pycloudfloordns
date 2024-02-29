from itertools import chain
from typing import Literal, Optional

from pydantic import BaseModel

TYPES_VALUES = Literal[
    "A",
    "AAAA",
    "ALIAS",
    "CNAME",
    "HINFO",
    "MX",
    "NS",
    "PTR",
    "RP",
    "SRV",
    "CAA",
    "TXT",
    "REDIRECT://",
    # For comparison, the following are valid on Cloudflare
    # "SOA",
    # "DS",
    # "DNSKEY",
    # "LOC",
    # "NAPTR",
    # "SSHFP",
    # "SVCB",
    # "TSLA",
    # "URI",
    # "SPF",
]

FULL_COMPARISON = {
    "A",
    "AAAA",
    "ALIAS",
    "CNAME",
}

UNIQUE_BY_NAME = {"HINFO", "MX", "NS", "PTR", "RP", "SRV", "CAA", "TXT", "REDIRECT://"}

REDIRECT_SERVERS = [
    "dforward.mtgsy.net.",
]
REDIRECT_SERVERS_IP = [
    "50.31.0.12",
]

REDIRECT_VALUES = list(
    chain(
        (("CNAME", value) for value in REDIRECT_SERVERS),
        (("A", ip) for ip in REDIRECT_SERVERS_IP),
    )
)


class Record(BaseModel):
    name: str
    type: str
    data: str
    id: Optional[str] = None
    zone: Optional[str] = None
    aux: str = "0"
    ttl: int = 3600
    active: Literal["Y", "N"] = "Y"
    # isfwd: str = "0"
    # cc: str = None
    # lbType: str = "0"

    class Config:
        populate_by_name = True
        extra = "allow"

    @property
    def identifier(self) -> str:
        """
        This method returns an identifer for the record that does not depend on its remote id
        """
        identifier = f"{self.name}/{self.type}"
        if self.type in FULL_COMPARISON:
            identifier = f"{identifier}/{self.data}"
        return identifier

    def __hash__(self):
        return hash(self.identifier)

    def is_same(self, right: "Record") -> bool:
        """
        This method check the identity (e.g. same id if defined, or same name/name+value)
        """
        if not isinstance(right, Record):
            return NotImplemented
        if self.id and right.id:
            return self.id == right.id
        if (self.name, self.type) != (right.name, right.type):
            return False
        if self.type in FULL_COMPARISON:
            return self.data == right.data
        return True

    @property
    def contains_spf_definition(self) -> bool:
        # RFC states that we only have one spf record on the APEX
        # But we may defined other records with spf definition to be included elsewhere.
        return all((self.type == "TXT", "v=spf" in self.data.lower()))

    @property
    def is_apex(self) -> bool:
        name = self.name.strip()
        return name in ("", "@")  # or name.endswith(".")

    @property
    def is_redirect(self) -> bool:
        data = (self.type.strip(), self.data.strip())
        return data in REDIRECT_VALUES

    @property
    def is_spf(self) -> bool:
        # RFC:
        # https://www.rfc-editor.org/rfc/rfc6242#section-4.1
        # https://datatracker.ietf.org/doc/html/rfc7208#section-4.5
        # NOTE: There should be only 1 apex spf record,
        # but we can create other spf record (e.g. spf1.mydomain.com) and include it in the apex
        # (alternatively, we can define spf records with CNAME or even NS records)
        return all((not self.name, self.contains_spf_definition))

    @property
    def is_dkim(self) -> bool:
        return all(
            (
                "._domainkey" in self.name,
                self.type == "TXT",
                "v=dkim" in self.data.lower(),
            )
        )

    @property
    def is_dmarc(self) -> bool:
        return all(
            ("_dmarc" in self.name, self.type == "TXT", "v=dmarc" in self.data.lower())
        )

    @property
    def is_null_mx(self) -> bool:
        return (
            self.type.upper() == "MX"
            and (self.name.endswith(".") or self.name in ("", "@"))
            and self.data in ("", ".")
        )

    @property
    def is_standard(self) -> bool:
        """
        Return True if the record is a standard one, False otherwise.
        A record is a standard one if it it:
        - A mail hardening record (SPF/DKIM/DMARC/Null MX)
        - An apex NS record
        """
        return any(
            (
                self.is_null_mx,
                self.is_spf,
                self.is_dkim,
                self.is_dmarc,
                (self.type.upper() == "NS" and self.is_apex),
            )
        )
