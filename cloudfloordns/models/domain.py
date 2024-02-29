# from dataclasses import dataclass, field
import logging
from collections import ChainMap
from typing import Any, List, Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from cloudfloordns.constants import NS1, NS2, NS3, NS4


class DomainDescription(BaseModel):
    status: Optional[str]
    status_extended: Optional[str]

    class Config:
        extra = "allow"


class Contact(BaseModel):
    firstname: Optional[str] = Field(alias="FirstName", default=None)
    lastname: Optional[str] = Field(alias="LastName", default=None)
    companyname: Optional[str] = Field(alias="Organization", default=None)
    streetaddress: Optional[str] = Field(alias="Address", default=None)
    city: Optional[str] = Field(alias="City", default=None)
    state: Optional[str] = Field(alias="State", default=None)
    postalcode: Optional[str] = Field(alias="PostalCode", default=None)
    country: Optional[str] = Field(alias="Country", default=None)
    phone: Optional[str] = Field(alias="Phone", default=None)
    fax: Optional[str] = Field(alias="Fax", default=None)
    email: Optional[str] = Field(alias="Email", default=None)

    class Config:
        populate_by_name = True
        extra = "ignore"

    def dump_as(self, prefix, by_alias=False):
        prefix = prefix.title() if by_alias else prefix.lower()
        return {
            f"{prefix}{k}": v for k, v in self.model_dump(by_alias=by_alias).items()
        }

    def as_owner(self, by_alias=False):
        return self.dump_as("owner", by_alias=by_alias)

    def as_admin(self, by_alias=False):
        return self.dump_as("admin", by_alias=by_alias)

    def as_tech(self, by_alias=False):
        return self.dump_as("tech", by_alias=by_alias)

    def as_bill(self, by_alias=False):
        return self.dump_as("bill", by_alias=by_alias)


class DomainPayload(BaseModel):
    domainname: str
    organisation: Optional[str] = Field(default=None, alias="DomainOrganization")

    # Owner informations
    ownerfirstname: str = Field(alias="OwnerFirstName")
    ownerlastname: str = Field(alias="OwnerLastName")
    ownercompanyname: str = Field(alias="OwnerOrganization")
    ownerstreetaddress: str = Field(alias="OwnerAddress")
    ownercity: str = Field(alias="OwnerCity")
    ownerstate: str = Field(alias="OwnerState")
    ownerpostalcode: str = Field(alias="OwnerPostalCode")
    ownercountry: str = Field(alias="OwnerCountry")
    ownerphone: str = Field(alias="OwnerPhone")
    ownerfax: str = Field(alias="OwnerFax")
    owneremail: str = Field(alias="OwnerEmail")

    # Admin informations
    adminfirstname: str = Field(alias="AdminFirstName")
    adminlastname: str = Field(alias="AdminLastName")
    admincompanyname: str = Field(alias="AdminOrganization")
    adminstreetaddress: str = Field(alias="AdminAddress")
    admincity: str = Field(alias="AdminCity")
    adminstate: str = Field(alias="AdminState")
    adminpostalcode: str = Field(alias="AdminPostalCode")
    admincountry: str = Field(alias="AdminCountry")
    adminphone: str = Field(alias="AdminPhone")
    adminfax: str = Field(alias="AdminFax")
    adminemail: str = Field(alias="AdminEmail")

    # Billing Contact informations
    billfirstname: str = Field(alias="BillFirstName")
    billlastname: str = Field(alias="BillLastName")
    billcompanyname: str = Field(alias="BillOrganization")
    billstreetaddress: str = Field(alias="BillAddress")
    billcity: str = Field(alias="BillCity")
    billstate: str = Field(alias="BillState")
    billpostalcode: str = Field(alias="BillPostalCode")
    billcountry: str = Field(alias="BillCountry")
    billphone: str = Field(alias="BillPhone")
    billfax: str = Field(alias="BillFax")
    billemail: str = Field(alias="BillEmail")

    # Technical Contact informations
    techfirstname: str = Field(alias="TechFirstName")
    techlastname: str = Field(alias="TechLastName")
    techcompanyname: str = Field(alias="TechOrganization")
    techstreetaddress: str = Field(alias="TechAddress")
    techcity: str = Field(alias="TechCity")
    techstate: str = Field(alias="TechState")
    techcountry: str = Field(alias="TechCountry")
    techpostalcode: str = Field(alias="TechPostalCode")
    techphone: str = Field(alias="TechPhone")
    techfax: str = Field(alias="TechFax")
    techemail: str = Field(alias="TechEmail")

    # Other informations
    groups_ids: List[str] = Field(default_factory=list)
    assign_default_groups_nameserver: Literal[0, 1] = 1
    autorenew: Optional[str] = Field(
        validation_alias=AliasChoices("auto_renew", "autorenew"), default=None
    )
    reg_opt_out: Optional[str] = None
    nom_type: Optional[str] = None
    lock: Optional[str] = Field(
        validation_alias=AliasChoices("lock", "locked"), default=None
    )

    domain_ns1: Optional[str] = Field(alias="DomainNS1", default=NS1)
    domain_ns2: Optional[str] = Field(alias="DomainNS2", default=NS2)
    domain_ns3: Optional[str] = Field(alias="DomainNS3", default=NS3)
    domain_ns4: Optional[str] = Field(alias="DomainNS4", default=NS4)
    domain_ns1_ip: Optional[str] = Field(alias="DomainNS1IP", default=None)
    domain_ns2_ip: Optional[str] = Field(alias="DomainNS2IP", default=None)
    domain_ns3_ip: Optional[str] = Field(alias="DomainNS3IP", default=None)
    domain_ns4_ip: Optional[str] = Field(alias="DomainNS4IP", default=None)

    @field_validator("lock", mode="before")
    @classmethod
    def ensure_locked_as_string(cls, v: Any):
        if not isinstance(v, str):
            return str(v)
        return v

    def _setcontact(self, prefix, info: Contact):
        data = info.dump_as(prefix)
        for k, v in data.items():
            setattr(self, k, v)
        # Domain.model_validate(self)
        return self

    def set_owner(self, info: Contact):
        return self._setcontact("Owner", info)

    def set_admin(self, info: Contact):
        return self._setcontact("Admin", info)

    def set_bill(self, info: Contact):
        return self._setcontact("Bill", info)

    def set_tech(self, info: Contact):
        return self._setcontact("Tech", info)

    @classmethod
    def prepare(
        cls,
        domainname: str,
        owner: Contact,
        admin: Contact,
        bill: Contact,
        tech: Contact,
    ) -> "DomainPayload":
        contact_data = {
            k: v
            for prefix, c in (
                ("Owner", owner),
                ("Admin", admin),
                ("Bill", bill),
                ("Tech", tech),
            )
            for k, v in c.dump_as(prefix).items()
        }
        return cls.model_validate({"domainname": domainname, **contact_data})

    def dump_for_update(self):
        payload = self.model_dump(
            by_alias=True,
            exclude=[
                "domainname",
                # "domain_ns1",
                # "domain_ns2",
            ],
            exclude_none=True,
            exclude_unset=True,
        )
        payload = {
            k: v for k, v in payload.items() if not k.lower().startswith("owner")
        }
        payload = {k: v for k, v in payload.items() if not k.lower().endswith("fax")}
        return payload

    # https://docs.pydantic.dev/latest/concepts/config/
    # https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.validate_assignment
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        validate_assignment=True,
    )


CLOUDFLOORDNS_NAMESERVERS = (
    "dns1.name-s.net.",
    "dns2.name-s.net.",
    "dns0.mtgsy.com.",
    "dns3.mtgsy.com.",
    "dns4.mtgsy.com.",
    "ns1.g02.cfdns.net.",
    "ns1.g02.cfdns.net.",
    "ns2.g02.cfdns.biz.",
    "ns3.g02.cfdns.info.",
    "ns4.g02.cfdns.co.uk.",
)
CLOUDFLOORDNS_NAMESERVERS_DOMAINS = (
    "name-s.net.",
    "mtgsy.com.",
    "cfdns.net.",
    "cfdns.net.",
    "cfdns.biz.",
    "cfdns.info.",
    "cfdns.co.uk.",
)


def is_cloudlfoordns_ns(ns):
    # Ensure the nameserver ends with a single dot.
    ns = ns.strip().rstrip(".").lower() + "."
    return ns.endswith(CLOUDFLOORDNS_NAMESERVERS_DOMAINS)


class Domain(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#case-sensitivity
        # case_sensitive = True
        # https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.validate_assignment
        validate_assignment=True,
    )

    domainname: str = Field(validation_alias=AliasChoices("domainname", "domain"))

    id: Optional[str] = None
    epp: Optional[str] = Field(default=None, alias="EPP")
    organisation: Optional[str] = None

    # Owner informations
    ownerfirstname: Optional[str] = Field(default=None, alias="OwnerFirstName")
    ownerlastname: Optional[str] = Field(default=None, alias="OwnerLastName")
    ownercompanyname: Optional[str] = Field(default=None, alias="OwnerOrganization")
    ownerstreetaddress: Optional[str] = Field(default=None, alias="OwnerAddress")
    ownercity: Optional[str] = Field(default=None, alias="OwnerCity")
    ownerstate: Optional[str] = Field(default=None, alias="OwnerState")
    ownerpostalcode: Optional[str] = Field(default=None, alias="OwnerPostalCode")
    ownercountry: Optional[str] = Field(default=None, alias="OwnerCountry")
    ownerphone: Optional[str] = Field(default=None, alias="OwnerPhone")
    ownerfax: Optional[str] = Field(default=None, alias="OwnerFax")
    owneremail: Optional[str] = Field(default=None, alias="OwnerEmail")

    # Admin informations
    adminfirstname: Optional[str] = Field(default=None, alias="AdminFirstName")
    adminlastname: Optional[str] = Field(default=None, alias="AdminLastName")
    admincompanyname: Optional[str] = Field(default=None, alias="AdminOrganization")
    adminstreetaddress: Optional[str] = Field(default=None, alias="AdminAddress")
    admincity: Optional[str] = Field(default=None, alias="AdminCity")
    adminstate: Optional[str] = Field(default=None, alias="AdminState")
    adminpostalcode: Optional[str] = Field(default=None, alias="AdminPostalCode")
    admincountry: Optional[str] = Field(default=None, alias="AdminCountry")
    adminphone: Optional[str] = Field(default=None, alias="AdminPhone")
    adminfax: Optional[str] = Field(default=None, alias="AdminFax")
    adminemail: Optional[str] = Field(default=None, alias="AdminEmail")

    # Billing Contact informations
    billfirstname: Optional[str] = Field(default=None, alias="BillFirstName")
    billlastname: Optional[str] = Field(default=None, alias="BillLastName")
    billcompanyname: Optional[str] = Field(default=None, alias="BillOrganization")
    billstreetaddress: Optional[str] = Field(default=None, alias="BillAddress")
    billcity: Optional[str] = Field(default=None, alias="BillCity")
    # There is a typo in the returned value.
    billstate: Optional[str] = Field(
        default=None,
        alias="BillState",
        validation_alias=AliasChoices("billState", "BillState"),
    )
    billpostalcode: Optional[str] = Field(default=None, alias="BillPostalCode")
    billcountry: Optional[str] = Field(default=None, alias="BillCountry")
    billphone: Optional[str] = Field(default=None, alias="BillPhone")
    billfax: Optional[str] = Field(default=None, alias="BillFax")
    billemail: Optional[str] = Field(default=None, alias="BillEmail")

    # Technical Contact informations
    techfirstname: Optional[str] = Field(default=None, alias="TechFirstName")
    techlastname: Optional[str] = Field(default=None, alias="TechLastName")
    techcompanyname: Optional[str] = Field(default=None, alias="TechOrganization")
    techstreetaddress: Optional[str] = Field(default=None, alias="TechAddress")
    techcity: Optional[str] = Field(default=None, alias="TechCity")
    techstate: Optional[str] = Field(default=None, alias="TechState")
    techcountry: Optional[str] = Field(default=None, alias="TechCountry")
    techpostalcode: Optional[str] = Field(default=None, alias="TechPostalCode")
    techphone: Optional[str] = Field(default=None, alias="TechPhone")
    techfax: Optional[str] = Field(default=None, alias="TechFax")
    techemail: Optional[str] = Field(default=None, alias="TechEmail")

    # Other informations
    auto_renew: Optional[str] = None
    reg_opt_out: Optional[str] = None
    username: Optional[str] = None
    status: Optional[str] = None
    use_trustee: Optional[str] = None
    locked: Optional[str] = None
    editzone: Optional[str] = None
    expires: Optional[str] = None
    deleteonexpiry: Optional[str] = None
    companyregno: Optional[str] = None
    client_delete_prohibited_lock: Optional[str] = None
    client_update_prohibited_lock: Optional[str] = None
    client_transfer_prohibited_lock: Optional[str] = None
    registeredhere: Optional[str] = None
    nameserver: List[str] = Field(default_factory=list)
    domain_description: Optional[DomainDescription] = None

    @property
    def is_externally_managed(self):
        is_cfdns_ns = [is_cloudlfoordns_ns(ns) for ns in self.nameserver]
        if all(is_cfdns_ns):
            return False
        if not any(is_cfdns_ns):
            return True
        # Part of the nameserver are owned by CFDns, the rest is not
        # => The nameserver configuration is wrong
        ns_txt = ", ".join(self.nameserver)
        logging.warning(
            f"Domain {self.domainname} has inconsistant nameservers: {ns_txt}"
        )
        return False

    @field_validator("locked", mode="before")
    @classmethod
    def ensure_locked_as_string(cls, v: Any):
        if not isinstance(v, str):
            return str(v)
        return v

    # @model_validator(mode='before')
    # @classmethod
    # def check_card_number_omitted(cls, data: Any) -> Any:
    #     if isinstance(data, dict):
    #         assert (
    #             'card_number' not in data
    #         ), 'card_number should not be included'
    #     return data

    def _setcontact(self, prefix, info: Contact):
        data = info.dump_as(prefix)
        for k, v in data.items():
            setattr(self, k, v)
        # Domain.model_validate(self)
        return self

    def _getcontact(self, prefix: str) -> Contact:
        data = {k.removeprefix(prefix): v for k, v in self.model_dump().items()}
        return Contact.model_validate(data)

    def set_owner(self, info: Contact):
        return self._setcontact("owner", info)

    def set_admin(self, info: Contact):
        return self._setcontact("admin", info)

    def set_bill(self, info: Contact):
        return self._setcontact("bill", info)

    def set_tech(self, info: Contact):
        return self._setcontact("tech", info)

    def update_contact(
        self,
        owner: Optional[Contact] = None,
        admin: Optional[Contact] = None,
        tech: Optional[Contact] = None,
        bill: Optional[Contact] = None,
        timeout=None,
    ):
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
        data = dict(ChainMap(*converted))
        for k, v in data.items():
            setattr(self, k, v)
        # Domain.model_validate(self)
        return self

    def register_payload(self, use_default_ns: bool = True) -> DomainPayload:
        data = self.model_dump(by_alias=True)
        data.update(
            {
                # "groups_ids": ...,
                "assign_default_groups_nameserver": 1 if use_default_ns else 0,
            }
        )

        return DomainPayload.model_validate(data)

    def dump_for_update(self):
        return self.model_dump(
            by_alias=True,
            exclude=[
                "epp",
                "status",
                "use_trustee",
                "locked",
                "domain_description",
            ],
        )
