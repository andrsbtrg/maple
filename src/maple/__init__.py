from typing_extensions import Self, Callable
from typing import Any
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.api import operations
from specklepy.transports.server.server import ServerTransport
from specklepy.objects import Base

# maple imports
from .base_extensions import flatten_base
from .utils import print_results
from .ops import ComparisonOps, property_equal, CompOp
from .models import Result, Assertion


# GLOBALS
# TODO: Refactor to remove globals
_test_cases: list[Result] = []  # Contains the results of the runs
_current_object: Base | None = None
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


def get_current_obj() -> Base | None:
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


def get_test_cases() -> list[Result]:
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
        self.assertion: Assertion

    def _select_parameters_values(self, parameter_name: str) -> list[Any]:
        """
        Gets a list of the values of each object in self.content
        where the parameter_name matches

        Args:
            parameter_name:

        Returns: a list of the value of the parameter matching

        Raises:
            AttributeError:

        """
        parameter_values = []
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
            for p in params:
                attr = getattr(parameters, p)
                if hasattr(attr, "name"):
                    if getattr(parameters, p)["name"] == parameter_name:
                        parameter_values.append(attr.value)
        return parameter_values

    def _should_have_length(self, length: int) -> Self:
        """
        Use to check wether the content has length equal to length

        Args:
            length (int): length to compare

        """
        objs = self.content
        if len(objs) == length:
            self.assertion.set_passed("have.length")
        else:
            self.assertion.set_failed("have.length")
        current = get_current_test_case()
        current.assertions.append(self.assertion)
        return self

    def _should_have_param_value(self, comparer: CompOp, assertion_value: Any) -> Self:
        """
        Using the comparer will get the parameter given by the self.selector
        for each object and compare each one against assertion_value

        Args:
            comparer: CompOp
            assertion_value: any value to compare

        Returns: Chainable
        """
        selected_values = self._select_parameters_values(self.selector)

        objs = self.content

        # store results in the last Results in test_cases
        for i, param_value in enumerate(selected_values):
            if comparer.evaluate(param_value, assertion_value):
                self.assertion.set_passed(objs[i].id)
            else:
                self.assertion.set_failed(objs[i].id)

        current = get_current_test_case()
        current.assertions.append(self.assertion)
        return self

    def should(self, comparer: ComparisonOps, assertion_value) -> Self:
        """
        Assert something inside the Chainable
        Args:
            comparer: one of CompOp possible enum values
            assertion_value: value to assert
        Raises: ValueError if comparer is not a defined CompOp
        Returns: Chainable
        """
        print("Asserting - should:", comparer, assertion_value)
        comparer_op = CompOp(comparer)
        if not self.assertion:
            self.assertion = Assertion()
        self.assertion.value = assertion_value
        self.assertion.comparer = comparer_op

        if comparer_op == CompOp.HAVE_LENGTH:
            return self._should_have_length(assertion_value)
        else:
            return self._should_have_param_value(comparer_op, assertion_value)

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
                self.assertion.set_failed(obj.id)
        return self

    def where(self, selector: str, value: str) -> Self:
        """
        Filters the current Speckle objects aquired by mp.get()
        where the object's own property 'selector' is equal to 'value'
        Args:
            selector: The name of a property of a Speckle Object to select
                e.g: type
            value: The name of the value of the property to be filtered

        Returns: Chainable
        """
        print("Filtering by:", selector, value)
        current = get_current_test_case()
        current.selected[selector] = value

        selected = list(
            filter(lambda obj: property_equal(selector, value, obj), self.content)
        )
        print("Got", len(selected))
        self.content = selected
        return self


def it(spec_name: str):
    """
    Declares a new Spec and stores it globally in the test cases.
    The next time mp.get() is called, it will be part of this spec name

    Args:
        test_name: name of the test case

    Returns: None
    """
    print("-------------------------------------------------------")
    print("Running test:", spec_name)
    get_test_cases().append(Result(spec_name))


def get(selector: str, value: str) -> Chainable:
    """
    Does a speckle queries and then filters by 'selector'.
    Returns the selected items inside the Chainable object
    to start a chain of assertions

    Args:
        selector: The name of a property of a Speckle Object to select
            e.g: category, family
        value: The objects whose selector matches this value will be filtered

    Returns: Chainable

    Raises:
        Exception: If it was not possible to query a speckle object
    """

    print("Getting", selector, value)
    current_test = get_current_test_case()
    current_test.selected[selector] = value

    speckle_obj = get_current_obj()
    if not speckle_obj:
        speckle_obj = get_last_obj()
    if speckle_obj is None:
        raise Exception("Could not get a Base object to query.")

    objs = list(flatten_base(speckle_obj))

    selected = list(filter(lambda obj: property_equal(selector, value, obj), objs))
    print("Got", len(selected), value)

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
    if not last_obj_id:
        raise Exception("No object_id")
    last_obj = operations.receive(obj_id=last_obj_id, remote_transport=transport)
    return last_obj


def run(*specs: Callable):
    """
    Runs any number of spec functions passed by args
    Args:
        *specs: Callable
    """
    for i, spec in enumerate(specs):
        if not callable(spec):
            print(
                "Warning - parameter at position " + f"{i}" + " is not spec function."
            )
            continue
        spec()

    # print results
    print_results(get_test_cases())
