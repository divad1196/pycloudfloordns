# from dataclasses import dataclass, field
from typing import List, Optional

from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

DEFAULT_PRIMARY_NS = "ns1.g02.cfdns.net"


class Group(BaseModel):
    """
    Pydantic model
    """

    id: Optional[str] = None
    name: Annotated[str, StringConstraints(strip_whitespace=True)]
    description: Optional[str] = None
    dnsservers: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        extra = "allow"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, op):
        if isinstance(op, Group):
            op = Group.name
        return self.name == op
