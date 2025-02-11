# from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field


class TLDPrice(BaseModel):
    """
    Pydantic model
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#case-sensitivity
        # case_sensitive = True
        # https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.validate_assignment
        validate_assignment=True,
    )

    tld: str
    currency: str
    registration_price: float = Field(alias="register")
    renewal_price: float = Field(alias="register")
    transfer_price: float = Field(alias="register")
    # maxyears: int
    # special: str
    # zone_info: str

    @property
    def price(self) -> float:
        return max((self.registration_price, self.renewal_price, self.transfer_price))


# Pricelist: TypeAlias = cast(TypeAdapter(list[TLDPrice]))  # from typing_extensions import TypeAlias, TypeAliasType
