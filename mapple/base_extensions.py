from collections.abc import Iterable, Mapping
from specklepy.objects import Base


def flatten(obj, visited=None):

    # Avoiding pesky circular references
    if visited is None:
        visited = set()

    if obj in visited:
        return

    visited.add(obj)

    # Define a logic for what objects to include in the diff
    should_include = any(
        [
            hasattr(obj, "displayValue"),
            hasattr(obj, "speckle_type")
            and obj.speckle_type == "Objects.Organization.Collection",
            hasattr(obj, "displayStyle"),
        ]
    )

    if should_include:
        yield obj

    props = obj.__dict__

    # traverse the object's nested properties -
    # which may include yieldable objects
    for prop in props:
        value = getattr(obj, prop)

        if value is None:
            continue

        if isinstance(value, Base):
            yield from flatten(value, visited)

        elif isinstance(value, Mapping):
            for dict_value in value.values():
                if isinstance(dict_value, Base):
                    yield from flatten(dict_value, visited)

        elif isinstance(value, Iterable):
            for list_value in value:
                if isinstance(list_value, Base):
                    yield from flatten(list_value, visited)
