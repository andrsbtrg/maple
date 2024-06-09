from typing import Self
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.api import operations
from specklepy.transports.server.server import ServerTransport
from .base_extensions import flatten_base
from specklepy.objects import Base


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


"""
Important: this contains the results of the runs
"""
test_cases: list[Result] = []
current_object: Base = None


class Chainable:
    def __init__(self, data):
        self.content = data
        self.selector = ""
        self.assertion: Assertion = None

    def should_have_length(self, length) -> Self:
        objs = self.content
        if len(objs) == length:
            self.assertion.it_passed(True)
        else:
            self.assertion.it_failed(True)
        global test_cases
        current = test_cases[-1]
        current.assertions.append(self.assertion)

    def should(self, *args) -> Self:
        """
        Assert something inside the Chainable
        """
        print('Asserting - should:', *args)
        comparer = args[0]
        assertion_value = args[1]
        if not self.assertion:
            self.assertion = Assertion()
        self.assertion.value = assertion_value
        self.assertion.assertion_type = comparer

        if comparer == 'have.length':
            return self.should_have_length(assertion_value)

        # Asserts:
        objs = self.content

        selected_values = []
        # store results in the last Results in test_cases
        for obj in objs:
            parameters = getattr(obj, "parameters")
            if parameters is None:
                raise AttributeError("no parameters")
            params = [a for a in dir(parameters) if not a.startswith(
                '_') and not callable(getattr(parameters, a))]
            for p in params:
                attr = getattr(parameters, p)
                if hasattr(attr, 'name'):
                    if getattr(parameters, p)['name'] == self.selector:
                        selected_values.append(attr.value)
        for i, param_value in enumerate(selected_values):
            if evaluate(comparer, param_value, assertion_value):
                self.assertion.it_passed(objs[i].id)
            else:
                self.assertion.it_failed(objs[i].id)

        global test_cases
        current = test_cases[-1]
        current.assertions.append(self.assertion)
        return self

    def its(self, property: str) -> Self:
        """
        Selector of what is inside the Chainable object
        """
        print('Selecting', property)
        self.selector = property
        self.assertion = Assertion()
        self.assertion.param = property

        objs = self.content
        for obj in objs:
            parameters = getattr(obj, "parameters")
            if parameters is None:
                raise AttributeError("no parameters")
            params = [a for a in dir(parameters) if not a.startswith(
                '_') and not callable(getattr(parameters, a))]
            found = False
            for p in params:
                attr = getattr(parameters, p)
                if hasattr(attr, 'name'):
                    if getattr(parameters, p)['name'] == self.selector:
                        found = True
            if not found:
                self.assertion.it_failed(obj.id)
        return self

    def where(self, *args) -> Self:
        """
        filters more the Chainable
        """
        print("Filtering by:", *args)
        global test_cases
        current = test_cases[-1]
        current.selected[args[0]] = args[1]

        selected = list(filter(lambda obj: property_equal(
            args[0], args[1], obj), self.content))
        print("Got", len(selected))
        self.content = selected
        return self


def init(obj: Base):
    global current_object
    current_object = obj
    return


def get(*args) -> Chainable:
    """Mostly do speckle queries and then
    save them inside the Chainable object"""

    print("Getting", *args)
    global test_cases
    test_cases[-1].selected[args[0]] = args[1]

    global current_object
    if current_object is None:
        last_commit = get_last_obj()
    else:
        last_commit = current_object

    objs = list(flatten_base(last_commit))

    selected = list(filter(
        lambda obj: property_equal(args[0], args[1], obj), objs))
    print("Got", len(selected), args[1])

    return Chainable(selected)


def get_last_obj():
    # get some objets
    client = SpeckleClient(host='https://latest.speckle.systems')
    # authenticate the client with a token
    account = get_default_account()
    client.authenticate_with_account(account)

    stream_id = "24fa0ed1c3"
    # print(client)
    # stream = client.stream.get(id=stream_id)

    transport = ServerTransport(client=client, stream_id=stream_id)

    last_obj_id = client.commit.list(stream_id)[0].referencedObject
    last_obj = operations.receive(
        obj_id=last_obj_id, remote_transport=transport)
    return last_obj


def it(test_name):
    """
    Declare a Spec and log it in the console
    Also should create a new Queue of chainables
    """
    print("-------------------------------------------------------")
    print("Running test:", test_name)
    global test_cases
    test_cases.append(Result(test_name))
    return


def run(*specs):
    for spec in specs:
        spec()
    print_results()


def print_results():
    print("-------------------------------------------------------")
    print("---RESULTS---")
    print("-------------------------------------------------------")
    global test_cases
    for case in test_cases:
        print(case.spec_name, end='')
        assertions = case.assertions
        for assertion in assertions:
            if len(assertion.failed) > 0:
                print(" - Failed")
                # print(">> ids:", assertion.failed)
            else:
                print(" - Passed")


def property_equal(propName, value, obj):
    try:
        return getattr(obj, propName) == value
    except Exception:
        return False


def evaluate(comparer, param_value, assertion_value):
    try:
        if comparer == 'be.greater':
            return param_value > assertion_value
        elif comparer == 'be.smaller':
            return param_value < assertion_value
        elif comparer == 'have.value':
            return str(param_value).lower() == str(assertion_value).lower()
        elif comparer == 'be.equal':  # numbers or floats
            return round(float(param_value), 2) == round(float(assertion_value), 2)
    except Exception:
        return False
