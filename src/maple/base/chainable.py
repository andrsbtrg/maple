from typing import Any, Callable, Self
from maple.models import Assertion, Result
from maple.ops import CompOp, ComparisonOps, deep_get, property_equal

import logging

logger = logging.getLogger(__name__)


class Chainable:
    def __init__(self, data, test_case: Result):
        self.content = data
        self.selector = ""
        self.assertion: Assertion = Assertion()
        self.current_test_case = test_case

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
        current = self.current_test_case
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
                logger.info(
                    f"Object id '{objs[i].id}'\n Expected {assertion_value}, got: {param_value}"
                )
                self.assertion.set_failed(objs[i].id)

        current = self.current_test_case
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
        self.assertion.comparer = func

        selected_values = self._select_parameters_values(self.selector)

        objs = self.content

        # store results in the last Results in test_cases
        for i, param_value in enumerate(selected_values):
            if func(param_value):
                self.assertion.set_passed(objs[i].id)
            else:
                logger.warning(f"object id '{objs[i].id}' - value: {param_value}")
                self.assertion.set_failed(objs[i].id)

        current = self.current_test_case
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
        self.current_test_case.selected[selector] = value

        selected = list(
            filter(lambda obj: property_equal(selector, value, obj), self.content)
        )
        logger.info("Elements after filter: %i", len(selected))
        self.content = selected
        return self

    def get(self, prop: str, value: str) -> Self:
        """
        Returns the selected items inside the Chainable object
        to start a chain of assertions

        Args:
            prop: The name of a property of a Speckle Object to select
                e.g: category, family
            value: The objects whose selector matches this value will be filtered

        Returns: Chainable

        Raises:
            Exception: If it was not possible to query a speckle object
        """
        if len(self.content) == 0:
            raise ValueError("Must first initialize with a valid list of objects")

        selected = list(
            filter(lambda obj: property_equal(prop, value, obj), self.content)
        )

        logger.info("Got %i %s", len(selected), value)
        self.current_test_case.selected[prop] = value
        self.content = selected
        return self
