# from dataclasses import dataclass, field
from typing import List, Optional, Union

from pydantic import AliasChoices, BaseModel, Field, StringConstraints
from typing_extensions import Annotated

DEFAULT_PRIMARY_NS = "ns1.g02.cfdns.net"


class DomainDescription(BaseModel):
    status: Optional[str]
    status_extended: Optional[str]

    class Config:
        extra = "allow"


class Zone(BaseModel):
    domainname: Annotated[str, StringConstraints(strip_whitespace=True)]

    id: Optional[str] = None
    zone: Optional[str] = None
    registered: Optional[int] = None
    secondary: Optional[int] = None
    primary: Optional[int] = None
    domain_description: Optional[DomainDescription] = None
    group_ids: Optional[List[str]] = None

    class Config:
        populate_by_name = True
        extra = "allow"

    def __hash__(self):
        return hash(self.domainname)

    def __eq__(self, op):
        return self.is_same(op)

    def is_same(self, right: Union[str, "Zone"]) -> bool:
        """
        This method check the identity
        """
        if not isinstance(right, (Zone, str)):
            return NotImplemented
        if isinstance(right, Zone):
            right = right.domainname
        return self.domainname == right

    @property
    def normalized_name(self) -> Optional[str]:
        name = self.domainname
        return ".".join(p.strip() for p in name.lower().split("."))


class Redirect(BaseModel):
    name: str = Field(validation_alias=AliasChoices("name", "source", "src"))
    dst: str = Field(
        validation_alias=AliasChoices(
            "forwardto", "destination", "dst", "dest", "target"
        )
    )
    zone: Optional[str] = None
