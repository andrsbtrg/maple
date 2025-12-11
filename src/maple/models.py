from acers import Collision
from typing import Any, Callable, Dict, Literal

from maple.ops import CompOp

Status = Literal["pass", "fail"]


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
        self.comparer: CompOp | Callable | None = None
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
        self.selected: Dict[str, str] = {}
        self.assertions: list[Assertion] = []
        self.type: Literal["spec", "collision"] = "spec"
        self.collision_results: list[Collision] = []

    def to_records(self):
        total_selfs = []
        if self.type == "spec":
            self_per_elem: Dict[str, Status] = {}
            select = []
            for selector in self.selected.keys():
                select.append(f"{selector} = {self.selected[selector]}")

            for a in self.assertions:
                descr = a.get_description()
                for id in a.passing:
                    self_per_elem[id] = "pass"
                for id in a.failing:
                    self_per_elem[id] = "fail"
                overall: Status = "pass" if a.passed() else "fail"
                total_selfs.append(
                    {
                        "type": "spec",
                        "spec_name": self.spec_name,
                        "get": select,
                        "spec": descr,
                        "result": overall,
                        "elements": self_per_elem,
                    }
                )
        elif self.type == "collision":
            collisions = self.collision_results
            total_selfs.append(
                {
                    "type": "collision",
                    "spec_name": self.spec_name,
                    "result": "fail" if len(collisions) > 0 else "pass",
                    "collisions": [
                        {"ids": x.ids, "dist": x.dist, "point": x.point}
                        for x in collisions
                    ],
                }
            )
        return total_selfs
