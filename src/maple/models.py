class Assertion:
    def __init__(self) -> None:
        self.param = ""
        self.assertion_type = ""
        self.value = None  # what will be compared to
        self.passed = []
        self.failed = []

    def it_passed(self, obj_id):
        self.passed.append(obj_id)

    def it_failed(self, obj_id):
        self.failed.append(obj_id)


class Result:
    def __init__(self, spec_name: str) -> None:
        self.spec_name = spec_name
        self.selected = {}
        self.assertions: list[Assertion] = []
