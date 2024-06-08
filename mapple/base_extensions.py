from collections.abc import Iterable, Mapping
from specklepy.objects import Base


def flatten_base(base: Base) -> Iterable[Base]:
    """Flatten a base object into an iterable of bases.

    This function recursively traverses the `elements` or `@elements` attribute of the 
    base object, yielding each nested base object.

    Args:
        base (Base): The base object to flatten.

    Yields:
        Base: Each nested base object in the hierarchy.
    """
    # Attempt to get the elements attribute, fallback to @elements if necessary
    elements = getattr(base, "elements", getattr(base, "@elements", None))

    if elements is not None:
        for element in elements:
            yield from flatten_base(element)

    yield base


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
