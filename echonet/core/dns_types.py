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
        Ensure the secondary DNS is:
        - Not identical to the primary
        - Of the same address type (IPv4 or IPv6)
        """
        primary = info.data.get("primary")
        if v:
            if v == primary:
                raise ValueError("Secondary DNS must be different from primary DNS")
            if type(v) is not type(primary):
                raise ValueError(
                    "Primary and secondary DNS must be the same address family"
                )
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Normalize tags to lowercase and remove duplicates."""
        if v:
            return list(sorted(set(tag.lower() for tag in v)))
        return v

    def __str__(self) -> str:
        sec = f", secondary={self.secondary}" if self.secondary else ""
        return f"{self.name} (primary={self.primary}{sec})"


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

    def add(self, record: DnsRecord) -> None:
        """Add a DNS record to the collection."""
        self.root.append(record)

    def remove(self, name: str) -> None:
        """Remove a DNS record by its display name."""
        self.root = [r for r in self.root if r.name != name]

    def to_dict(self) -> list[dict]:
        """Return a list of DNS records as plain dictionaries."""
        return [r.model_dump() for r in self.root]

    def to_json(self) -> str:
        """Return the collection as a JSON string."""
        return self.model_dump_json()


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

    def add_collection(self, name: str, collection: DnsCollection) -> None:
        """Add a new DNS collection/profile."""
        self.root[name] = collection

    def remove_collection(self, name: str) -> None:
        """Remove a DNS collection/profile by name."""
        self.root.pop(name, None)

    def to_dict(self) -> dict:
        """Return the entire DNS list as a plain dictionary."""
        return {name: coll.to_dict() for name, coll in self.root.items()}

    def to_json(self) -> str:
        """Return the entire DNS list as a JSON string."""
        return self.model_dump_json()
