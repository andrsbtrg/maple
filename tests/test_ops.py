from maple.ops import CompOp, ComparisonOps
from typing import get_args


def test_enum():
    comp = "be.equal"
    assert comp == CompOp.BE_EQUAL


def test_literal():
    """
    Assert that all the enum values in CompOp are covered in
    the type ComparisonOps
    """
    for opt in CompOp:
        assert opt.value in get_args(ComparisonOps)
