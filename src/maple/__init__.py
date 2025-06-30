# maple import

from os import getenv
from typing import Any, Dict, Literal, overload

import sys
from deprecated import deprecated
from specklepy.api import operations
from specklepy.api.client import Account, SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.core.api.models.current import ModelWithVersions, Version
from specklepy.objects import Base
from specklepy.transports.server.server import ServerTransport
from typing_extensions import Callable, Self

from .base_extensions import flatten_base
from .models import Assertion, Result
from .ops import CompOp, ComparisonOps, deep_get, property_equal
from .report import HtmlReport
from .utils import print_results

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logging.getLogger("specklepy").setLevel(logging.WARNING)
logging.getLogger("gql.transport.requests").setLevel(logging.WARNING)


Status = Literal["pass", "fail"]


# GLOBALS
# TODO: Refactor to remove globals
_test_cases: list[Result] = []  # Contains the results of the runs
_current_object: Base | None = None
_project_id: str = ""
_model_id: str = ""


def init(obj: Base) -> None:
    """
    Caches the speckle object obj in the global _current_object
    so it can be reused in the next tests

    Args:
        obj: a speckle Base object

    Returns: None
    """
    global _current_object
    _current_object = obj
    return


def set_logging(f: bool) -> None:
    """
    Set log to std out. Default is True

    Args:
        f: bool
    """
    global _log_out
    _log_out = f


@deprecated(
    reason="Starting with maple 0.1 please use mp.init_model to specify a project and model id."
)
def stream(id: str) -> None:
    """
    Sets the current stream_id to be used to query the base object

    Args:
        id: a speckle stream (project) id

    Returns: None
    """
    global _project_id
    _project_id = id
    global _current_object
    _current_object = None
    return


def init_model(project_id: str, model_id: str) -> None:
    """
    Sets the global variables project id and model id for the
    current test until reset.


    Args:
        project_id: a project id
        model_id: the model id to test

    """
    # set the model and project id
    global _project_id
    _project_id = project_id
    global _model_id
    _model_id = model_id
    # clear the current object
    global _current_object
    _current_object = None
    # clear previous test runs
    global _test_cases
    _test_cases.clear()
    return


def get_token() -> str | None:
    """
    Get the token to authenticate with Speckle.
    The token should be under the env variable 'SPECKLE_TOKEN'
    """

    token = getenv("SPECKLE_TOKEN")
    return token


def get_model_id() -> str:
    """
    Gets the Model id provided with mp.init_model
    """
    global _model_id
    if _model_id == "":
        raise Exception("Please provide a Model Id to test using mp.init_model()")
    return _model_id


def get_project_id() -> str:
    """
    Gets the Model id provided with mp.init_model
    """
    global _project_id
    if _project_id == "":
        raise Exception("Please provide a Project Id to test using mp.init_model()")
    return _project_id


def get_current_obj() -> Base | None:
    """
    Get the current object specified with mp.init()
    """
    global _current_object
    return _current_object


def get_current_test_case() -> Result | None:
    """
    Get the current test case
    """
    global _test_cases
    if len(_test_cases) < 1:
        return None
    current = _test_cases[-1]
    return current


def get_test_cases() -> list[Result]:
    """
    Gets the list of Test Cases
    """
    global _test_cases
    return _test_cases


def get_results() -> list[Any]:
    """
    Gets the list of Results
    """
    results = get_test_cases()

    total_results = []
    for result in results:
        result_per_elem: Dict[str, Status] = {}
        select = []
        for selector in result.selected.keys():
            select.append(f"{selector} = {result.selected[selector]}")

        for a in result.assertions:
            descr = a.get_description()
            for id in a.passing:
                result_per_elem[id] = "pass"
            for id in a.failing:
                result_per_elem[id] = "fail"
            overall: Status = "pass" if a.passed() else "fail"
            total_results.append(
                {
                    "spec_name": result.spec_name,
                    "get": select,
                    "spec": descr,
                    "result": overall,
                    "elements": result_per_elem,
                }
            )
    return total_results


# endof GLOBALS


class Chainable:
    def __init__(self, data):
        self.content = data
        self.selector = ""
        self.assertion: Assertion = Assertion()

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
        # check on base object
        for obj in objs:
            value = deep_get(obj, parameter_name)
            if not value:
                break
            parameter_values.append(value)

        if len(parameter_values) > 0:
            return parameter_values

        return parameter_values

    def _should_have_length(self, length: int) -> Self:
        """
        Use to check wether the content has length equal to length

        Args:
            length (int): length to compare

        """
        objs = self.content
        self.assertion.selector = "Collection"
        if len(objs) == length:
            self.assertion.set_passed("have.length")
        else:
            self.assertion.set_failed("have.length")
        current = get_current_test_case()
        if current is None:
            raise Exception("Expected current test case not to be None")
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
                logger.warning(f"object id '{objs[i].id}' - value: {param_value}")
                self.assertion.set_failed(objs[i].id)

        current = get_current_test_case()
        if current is None:
            raise Exception("Expected current test case not to be None")
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
        logger.info("Asserting - should: %s %s", comparer, assertion_value)
        comparer_op = CompOp(comparer)
        self.assertion.value = assertion_value
        self.assertion.comparer = comparer_op

        if comparer_op == CompOp.HAVE_LENGTH:
            return self._should_have_length(assertion_value)
        else:
            return self._should_have_param_value(comparer_op, assertion_value)

    def should_satisfy(self, func: Callable[[Any], bool]) -> Self:
        """
        Asserts using a custom condition.
        Args:
            func: a function that takes one argument and returns true or false
        Returns: Chainable
        """
        logger.info("Asserting - should satisfy")

        if not isinstance(func, Callable):
            raise TypeError(
                "Argument to should_satisfy must be a function. Got " + type(func)
            )
        selected_values = self._select_parameters_values(self.selector)

        objs = self.content

        # store results in the last Results in test_cases
        for i, param_value in enumerate(selected_values):
            if func(param_value):
                self.assertion.set_passed(objs[i].id)
            else:
                logger.warning(f"object id '{objs[i].id}' - value: {param_value}")
                self.assertion.set_failed(objs[i].id)

        current = get_current_test_case()
        if current is None:
            raise Exception("Expected current test case not to be None")
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
        logger.info("Selecting %s", property)
        self.selector = property
        self.assertion.selector = property

        objs = self.content
        # check on base object
        for obj in objs:
            value = deep_get(obj, property)
            if not value:
                self.assertion.set_failed(obj.id)
                logger.warning(f"object id: '{obj.id}' has no property '{property}'")
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
        logger.info("Filtering by: %s - %s", selector, value)
        current = get_current_test_case()
        if current is None:
            raise Exception("Expected current test case not to be None")
        current.selected[selector] = value

        selected = list(
            filter(lambda obj: property_equal(selector, value, obj), self.content)
        )
        logger.info("Elements after filter: %i", len(selected))
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
    logger.info("Running test: %s", spec_name)
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

    logger.info("Getting %s %s", selector, value)
    current_test = get_current_test_case()
    if current_test is None:
        raise Exception("Expected current test case not to be None")
    current_test.selected[selector] = value

    speckle_obj = get_current_obj()
    if not speckle_obj:
        speckle_obj = get_last_obj()
    if speckle_obj is None:
        raise Exception("Could not get a Base object to query.")

    objs = list(flatten_base(speckle_obj))

    selected = list(filter(lambda obj: property_equal(selector, value, obj), objs))
    logger.info("Got %i %s", len(selected), value)

    return Chainable(selected)


def get_last_obj() -> Base:
    """
    Gets the last object for the specified stream_id
    """
    logger.info("Getting object from speckle")
    host = getenv("SPECKLE_HOST")
    if not host:
        host = "https://app.speckle.systems"
    logger.info("Using Speckle host: %s", host)
    client = SpeckleClient(host)
    # authenticate the client with a token
    account = get_default_account()
    token = get_token()
    if token:
        logger.debug("Auth with token")
        client.authenticate_with_token(token)
    elif account and account_match_host(account, host):
        logger.debug("Auth with default account")
        client.authenticate_with_account(account)
    else:
        logger.warning("No auth present")

    project_id = get_project_id()
    model_id = get_model_id()
    transport = ServerTransport(client=client, stream_id=project_id)

    models = client.model.get_models(project_id=project_id)
    found_model = next(filter(lambda x: x.id == model_id, models.items), None)
    if not found_model:
        raise Exception("Model not found: ", model_id)

    model: ModelWithVersions = client.model.get_with_versions(
        project_id=project_id, model_id=found_model.id
    )

    versions = model.versions.items
    if len(versions) == 0:
        raise Exception("Model contains no versions.")
    if type(versions[0]) is not Version:
        raise Exception("Type of element is not Model: ", type(versions[0]))
    last_obj_id = versions[0].referenced_object

    if not last_obj_id:
        raise Exception("No object_id")
    last_obj = operations.receive(obj_id=last_obj_id, remote_transport=transport)

    # cache the current obj
    init(last_obj)
    return last_obj


def run(*specs: Callable):
    """
    Runs any number of spec functions passed by args
    Args:
        *specs: Callable
    """
    print_info(specs)

    for i, spec in enumerate(specs):
        if not callable(spec):
            print(
                "Warning - parameter at position " + f"{i}" + " is not spec function."
            )
            continue
        spec()

    # print results
    print_results(get_test_cases())


def print_info(specs):
    from importlib_metadata import version

    from .utils import print_title

    print_title("Test session")

    v = version("maple-spec")
    print("Maple -", v)
    print("collected", len(specs), "specs")
    print()


def generate_report(output_path: str) -> str:
    """
    Generats a report file with the test cases after.
    mp.run()

    Returns:
        The path of the file created

    Args:
        output_path: directory to save reports. It must be an
        existing directory.
    """
    logger.info("Creating report")
    results = get_test_cases()
    if len(results) == 0:
        raise Exception("mp.run must be called before generating report")
    report = HtmlReport(results)
    file_created = report.create(output_path)
    logger.info("Report created on %s", file_created)
    return file_created


def account_match_host(account: Account, host: str) -> bool:
    url = account.serverInfo.url
    host_url = host.replace("https://", "")
    host_url = host_url.replace("/", "")
    return url == host_url
