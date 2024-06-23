"""
Contains functions to handle operations between Base and comparisons
"""

from specklepy.objects import Base
from enum import StrEnum


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


class CompOp(StrEnum):
    """
    Enum with possible comparison operations
    """
    BE_GREATER = 'be.greater'
    BE_SMALLER = 'be.smaller'
    BE_EQUAL = 'be.equal'
    HAVE_VALUE = 'have.value'
    HAVE_LENGTH = 'have.length'


def evaluate(comparer: CompOp, param_value, assertion_value):
    try:
        if comparer == CompOp.BE_GREATER:
            return param_value > assertion_value
        elif comparer == CompOp.BE_SMALLER:
            return param_value < assertion_value
        elif comparer == CompOp.HAVE_VALUE:
            return str(param_value).lower() == str(assertion_value).lower()
        elif comparer == CompOp.BE_EQUAL:  # numbers or floats
            return round(float(param_value), 2) == round(float(assertion_value), 2)
    except Exception:
        return False
