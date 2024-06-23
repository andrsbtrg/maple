class Assertion:
    """
    Contains parameters and result of performing an assertion on
    Speckle objects and its values

    Attributes:
        assertion_type:
        value:
        passed:
        failed:

    """

    def __init__(self) -> None:
        self.assertion_type = ""
        self.value = None  # what will be compared to
        self.passed = []
        self.set_failed = []

    def set_passed(self, obj_id):
        self.passed.append(obj_id)

    def set_failed(self, obj_id):
        self.set_failed.append(obj_id)


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
