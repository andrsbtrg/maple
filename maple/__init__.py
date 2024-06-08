from typing import Self
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.api import operations
from specklepy.transports.server.server import ServerTransport
from .base_extensions import flatten_base


class Assertion:
    def __init__(self) -> None:
        self.param = ""  # selector like Height or Width
        self.type = ""  # assertion type "greater than"
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
        self.assertions = [Assertion]


test_cases = [Result]


class Chainable:
    def __init__(self, data):
        self.content = data
        self.selector = ""
        self.assertion: Assertion = None

    def should(self, *args) -> Self:
        """
        Assert something inside the Chainable
        """
        print('Asserting - should:', *args)
        comparer = args[0]
        assertion_value = args[1]
        self.assertion.value = assertion_value
        self.assertion.type = comparer

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
        global test_cases
        current = test_cases[-1]
        for i, param_value in enumerate(selected_values):
            if comparer == 'be.greater':
                if param_value > assertion_value:
                    self.assertion.it_passed(objs[i].id)
                else:
                    self.assertion.it_failed(objs[i].id)
        current.assertions.append(self.assertion)
        return Chainable(objs)

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
        test_cases[-1].selected[args[0]] = args[1]

        selected = list(filter(lambda obj: property_equal(
            args[0], args[1], obj), self.content))
        print("Got", len(selected), args[1])
        return Chainable(selected)


def get(*args) -> Chainable:
    """Mostly do speckle queries and then
    save them inside the Chainable object"""

    print("Getting", *args)
    global test_cases
    test_cases[-1].selected[args[0]] = args[1]

    # get something
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

    objs = list(flatten_base(last_obj))

    selected = list(filter(
        lambda obj: property_equal(args[0], args[1], obj), objs))
    print("Got", len(selected), args[1])

    return Chainable(selected)


def it(test_name):
    """
    Declare a Spec and log it in the console
    Also should create a new Queue of chainables
    """
    print("Running test:", test_name)
    global test_cases
    test_cases.append(Result(test_name))
    return


def run(*specs):
    for spec in specs:
        spec()


def property_equal(propName, value, obj):
    try:
        return getattr(obj, propName) == value
    except Exception:
        return False
