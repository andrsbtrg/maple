import maple
from typing import Any, Callable


class Assertion:
    """
    Contains parameters and result of performing an assertion on
    Speckle objects and its values

    Attributes:
        comparer: Comparison Operation used to check assertion
        value: Value used to assert
        passing: List of Ids that passed assertion
        failing: List of Ids that failed assertion

    """

    def __init__(self) -> None:
        self.comparer: maple.CompOp | Callable | None = None
        self.value: Any = None  # what will be compared to
        self.passing: list[str] = []
        self.failing: list[str] = []
        self.selector = ""

    def get_description(self):
        return {
            "selector": self.selector,
            "comparer": self.comparer,
            "value": self.value,
        }

    def set_passed(self, obj_id: str):
        self.passing.append(obj_id)

    def set_failed(self, obj_id: str):
        self.failing.append(obj_id)

    def passed(self) -> bool:
        """
        True if not any failing value
        """
        return len(self.failing) == 0

    def failed(self) -> bool:
        """
        True if any failing value
        """
        return len(self.failing) > 0


class Result:
    """
    Contains the Results of one Assertion

    Attributes:
        spec_name: name of the spec mp.it('name') who expects a result
        selected: Dict with selector:value
        assertions: List of assertions

    """

    def __init__(self, spec_name: str) -> None:
        self.spec_name = spec_name
        self.selected = {}
        self.assertions: list[Assertion] = []
