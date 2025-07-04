"""
Contains functions to handle operations between Base and comparisons
"""

from specklepy.objects import Base
from enum import StrEnum
from typing import Any, Literal


def deep_get(obj, path: str):
    for part in path.split("."):
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            obj = getattr(obj, part, None)
        if obj is None:
            break
    return obj


def property_equal(propName: str, value: str, obj: Base):
    """
    Evaluates if an object <obj> propName has value equal to value
    Args:
        propName: the name of the property to find.
            it accepts a property path separated by '.'
            Example: 'properties.quantities.area'
        value: the value to equalize
        obj: the object to extract the poperty

    Returns: true if equal or False if not equal or does not exist
    """
    try:
        return deep_get(obj, propName) == value
    except Exception as e:
        print(e)
        return False


ComparisonOps = Literal[
    "be.greater",
    "be.smaller",
    "be.equal",
    "not.be.equal",
    "have.value",
    "not.have.value",
    "have.length",
]


class CompOp(StrEnum):
    """
    Comparison (assertion) operations
    """

    BE_GREATER = "be.greater"
    BE_SMALLER = "be.smaller"
    BE_EQUAL = "be.equal"
    NOT_BE_EQUAL = "not." + BE_EQUAL
    HAVE_VALUE = "have.value"
    NOT_HAVE_VALUE = "not." + HAVE_VALUE
    HAVE_LENGTH = "have.length"

    def evaluate(self, param_value: Any, assertion_value: Any) -> bool:
        """
        Checks if the param_value evaluates to the assertion_value
        accordinf to the CompOp

        Args:
            param_value:
            assertion_value:

        Returns: True or False
        """
        try:
            if self == CompOp.BE_GREATER:
                return param_value >= assertion_value
            elif self == CompOp.BE_SMALLER:
                return param_value < assertion_value
            elif self == CompOp.HAVE_VALUE:
                return str(param_value).lower() == str(assertion_value).lower()
            elif self == CompOp.NOT_HAVE_VALUE:
                return str(param_value).lower() != str(assertion_value).lower()
            elif self == CompOp.BE_EQUAL:  # numbers or floats
                return are_equal_numeric(param_value, assertion_value)
            elif self == CompOp.NOT_BE_EQUAL:  # numbers or floats
                return not are_equal_numeric(param_value, assertion_value)
        except Exception as e:
            print("Could not assert: ", e)
            return False
        return False


def are_equal_numeric(param_value: Any, assertion_value: Any) -> bool:
    if not isinstance(assertion_value, float) and not isinstance(assertion_value, int):
        raise ValueError(
            "be.equal expects a numeric assertion value. Got: ",
            assertion_value,
        )
    try:
        float_value = float(param_value)
    except ValueError:
        raise ValueError(f"Could not parse {param_value}.")
    return round(float_value, 2) == round(float(assertion_value), 2)
