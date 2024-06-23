from typing_extensions import Self, Callable
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.api import operations
from specklepy.transports.server.server import ServerTransport
from specklepy.objects import Base

# maple imports
from .base_extensions import flatten_base
from .utils import print_results
from .ops import evaluate, property_equal, CompOp
from .models import Result, Assertion


# GLOBALS
# TODO: Refactor to remove globals
_test_cases: list[Result] = []  # NOTE: this contains the results of the runs
_current_object: Base = None
_stream_id: str = ""


def init(obj: Base) -> None:
    """
    Sets the obj as current object
    """
    global _current_object
    _current_object = obj
    return


def stream(id: str) -> None:
    """
    Set the stream_id
    """
    global _stream_id
    _stream_id = id
    return


def get_token():
    """
    Get the token to authenticate with Speckle.
    The token should be under the env variable 'SPECKLE_TOKEN'
    """
    import os

    token = os.getenv("SPECKLE_TOKEN")
    if token is None:
        raise Exception("Expected `SPECKLE_TOKEN` env variable to be set")
    return token


def get_stream_id() -> str:
    """
    Gets the stream_id provided with mp.stream()
    """
    global _stream_id
    if _stream_id == "":
        raise Exception("Please provide a Stream id using mp.stream()")
    return _stream_id


def get_current_obj() -> Base:
    """
    Get the current object specified with mp.init()
    """
    global _current_object
    return _current_object


def get_current_test_case() -> Result:
    """
    Get the current test case
    """
    global _test_cases
    current = _test_cases[-1]
    return current


def get_test_cases() -> [Result]:
    """
    Gets the list of Test Cases
    """
    global _test_cases
    return _test_cases

# endof GLOBALS


class Chainable:
    def __init__(self, data):
        self.content = data
        self.selector = ""
        self.assertion: Assertion = None

    def _should_have_length(self, length: int) -> Self:
        """
        Use to check wether the content has length equal to length

        Args:
            length (int): length to compare

        """
        objs = self.content
        if len(objs) == length:
            self.assertion.it_passed(True)
        else:
            self.assertion.it_failed(True)
        current = get_current_test_case()
        current.assertions.append(self.assertion)

    def should(self, comparer: CompOp, assertion_value) -> Self:
        """
        Assert something inside the Chainable
        Args:
            comparer: one of CompOp possible enum values
            assertion_value: value to assert

        """
        # NOTE: using is instance since member not in Enum raises error until python 3.12
        print("Asserting - should:", comparer, assertion_value)
        if not self.assertion:
            self.assertion = Assertion()
        self.assertion.value = assertion_value
        self.assertion.assertion_type = comparer

        if comparer == CompOp.HAVE_LENGTH:
            return self._should_have_length(assertion_value)

        # Asserts:
        objs = self.content

        selected_values = []
        # store results in the last Results in test_cases
        for obj in objs:
            parameters = getattr(obj, "parameters")
            if parameters is None:
                raise AttributeError("no parameters")
            params = [
                a
                for a in dir(parameters)
                if not a.startswith("_") and not callable(getattr(parameters, a))
            ]
            for p in params:
                attr = getattr(parameters, p)
                if hasattr(attr, "name"):
                    if getattr(parameters, p)["name"] == self.selector:
                        selected_values.append(attr.value)
        for i, param_value in enumerate(selected_values):
            if evaluate(comparer, param_value, assertion_value):
                self.assertion.it_passed(objs[i].id)
            else:
                self.assertion.it_failed(objs[i].id)

        current = get_current_test_case()
        current.assertions.append(self.assertion)
        return self

    def its(self, property: str) -> Self:
        """
        Selector of a parameter inside the Chainable object

        Args:
            property: name of parameter to select from content

        Returns: Chainable

        Raises:
            AttributeError: if the parameter name does not match in the
            inner object selected with get
        """
        print("Selecting", property)
        self.selector = property
        self.assertion = Assertion()
        self.assertion.param = property

        objs = self.content
        for obj in objs:
            parameters = getattr(obj, "parameters")
            if parameters is None:
                raise AttributeError("no parameters")
            params = [
                a
                for a in dir(parameters)
                if not a.startswith("_") and not callable(getattr(parameters, a))
            ]
            found = False
            for p in params:
                attr = getattr(parameters, p)
                if hasattr(attr, "name"):
                    if getattr(parameters, p)["name"] == self.selector:
                        found = True
            if not found:
                self.assertion.it_failed(obj.id)
        return self

    def where(self, *args) -> Self:
        """
        filters more the Chainable
        """
        print("Filtering by:", *args)
        current = get_current_test_case()
        current.selected[args[0]] = args[1]

        selected = list(
            filter(lambda obj: property_equal(
                args[0], args[1], obj), self.content)
        )
        print("Got", len(selected))
        self.content = selected
        return self


def it(test_name: str):
    """
    Declare a Spec and log it in the console
    Also should create a new Queue of chainables

    Args:
        test_name: name of the test case

    Returns: None
    """
    print("-------------------------------------------------------")
    print("Running test:", test_name)
    get_test_cases().append(Result(test_name))
    return


def get(*args) -> Chainable:
    """Mostly do speckle queries and then
    save them inside the Chainable object"""

    print("Getting", *args)
    current_test = get_current_test_case()
    current_test.selected[args[0]] = args[1]

    speckle_obj = get_current_obj()
    if not speckle_obj:
        speckle_obj = get_last_obj()
    if speckle_obj is None:
        raise Exception("Could not get a Base object to query.")

    objs = list(flatten_base(speckle_obj))

    selected = list(
        filter(lambda obj: property_equal(args[0], args[1], obj), objs))
    print("Got", len(selected), args[1])

    return Chainable(selected)


def get_last_obj() -> Base:
    """
    Gets the last object for the specified stream_id
    """
    client = SpeckleClient(host="https://latest.speckle.systems")
    # authenticate the client with a token
    account = get_default_account()
    if account:
        client.authenticate_with_account(account)
    else:
        token = get_token()
        client.authenticate_with_token(token)

    stream_id = get_stream_id()
    transport = ServerTransport(client=client, stream_id=stream_id)

    last_obj_id = client.commit.list(stream_id)[0].referencedObject
    last_obj = operations.receive(
        obj_id=last_obj_id, remote_transport=transport)
    return last_obj


def run(*specs: Callable):
    """
    Runs any number of spec functions passed by args
    Args:
        *specs: Callable
    """
    for spec in specs:
        spec()

    # print results
    print_results(get_test_cases())
