from typing import (
    Annotated,
    ItemsView,
    Iterator,
    KeysView,
    Optional,
    SupportsIndex,
    ValuesView,
)

from pydantic import (
    BaseModel,
    Field,
    IPvAnyAddress,
    RootModel,
    StringConstraints,
    ValidationInfo,
    field_validator,
)


class DnsRecord(BaseModel):
    # Display name for this DNS record (1–50 characters)
    name: Annotated[str, StringConstraints(min_length=1, max_length=50)] = Field(
        description="Short display name for this DNS entry"
    )

    # Required primary DNS server address (IPv4 or IPv6)
    primary: IPvAnyAddress = Field(description="Primary DNS server IP (IPv4 or IPv6)")

    # Optional backup DNS server address (IPv4 or IPv6)
    secondary: Optional[IPvAnyAddress] = Field(
        None, description="Secondary DNS server IP (IPv4 or IPv6)"
    )

    # Optional human-readable service description (max 200 characters)
    desc: Annotated[Optional[str], StringConstraints(max_length=200)] = Field(
        None, description="A short description of the service"
    )

    # Optional tags for grouping/search, defaults to an empty list
    tags: list[str] = Field(
        default_factory=list, description="List of tags for categorization/search"
    )

    @field_validator("secondary", mode="after")
    @classmethod
    def secondary_neq_to_primary(
        cls, v: Optional[IPvAnyAddress], info: ValidationInfo
    ) -> Optional[IPvAnyAddress]:
        """
        Ensure the secondary DNS is not identical to the primary.
        Prevents redundant configuration.
        """
        if v and v == info.data.get("primary"):
            raise ValueError("Secondary DNS must be different from primary DNS")
        return v


# Represents a DNS profile: a simple list of DNS records
class DnsCollection(RootModel[list[DnsRecord]]):
    root: list[DnsRecord] = Field(
        default_factory=list, description="List of DNS records for this profile"
    )

    # Make DnsList iterable like a normal list
    def __iter__(self) -> Iterator[DnsRecord]:
        return iter(self.root)

    # Support indexing (e.g., dns_list[0])
    def __getitem__(self, i: SupportsIndex) -> DnsRecord:
        return self.root[i]

    # Support len(dns_list)
    def __len__(self) -> int:
        return len(self.root)


# The complete collection: mapping of profile name -> profile's DNS records
class DnsList(RootModel[dict[str, DnsCollection]]):
    root: dict[str, DnsCollection] = Field(
        default_factory=dict,
        description="Mapping from profile name to list of DNS records",
    )

    # Dict-like access to keys, values, and items
    def keys(self) -> KeysView[str]:
        return self.root.keys()

    def values(self) -> ValuesView[DnsCollection]:
        return self.root.values()

    def items(self) -> ItemsView[str, DnsCollection]:
        return self.root.items()

    # Support indexing by key (e.g., dns_collection["work"])
    def __getitem__(self, key: str) -> DnsCollection:
        return self.root[key]

    # Support len(dns_collection)
    def __len__(self) -> int:
        return len(self.root)
