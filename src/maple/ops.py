"""
Contains functions to handle operations between Base and comparisons
"""

from specklepy.objects import Base
from enum import StrEnum
from typing import Any, Literal


def property_equal(propName: str, value: str, obj: Base):
    """
    Evaluates if an object <obj> propName has value equal to value
    Args:
        propName: the name of the property to find
        value: the value to equalize
        obj: the object to extract the poperty

    Returns: true if equal or False if not equal or does not exist
    """
    try:
        return getattr(obj, propName) == value
    except Exception:
        return False


ComparisonOps = Literal[
    "be.greater", "be.smaller", "be.equal", "have.value", "have.length"
]


class CompOp(StrEnum):
    """
    Comparison (assertion) operations
    """

    BE_GREATER = "be.greater"
    BE_SMALLER = "be.smaller"
    BE_EQUAL = "be.equal"
    HAVE_VALUE = "have.value"
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
                return param_value > assertion_value
            elif self == CompOp.BE_SMALLER:
                return param_value < assertion_value
            elif self == CompOp.HAVE_VALUE:
                return str(param_value).lower() == str(assertion_value).lower()
            elif self == CompOp.BE_EQUAL:  # numbers or floats
                return round(float(param_value), 2) == round(float(assertion_value), 2)
        except Exception:
            # log error
            print("Could not assert")
            return False
        return False
