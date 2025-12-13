from typing import Any, Callable, Dict, overload, List, Optional
from specklepy.objects import Base

from maple.base.chainable import Chainable
from maple.base_extensions import flatten_base

from acers import clash_detection, Collision


import logging

from maple.models import Result
from maple.ops import property_equal
from maple.speckle_utils import get_last_obj
from maple.utils import log_collision, print_results, serialize_set, print_info

logger = logging.getLogger(__name__)


class Maple:
    @overload
    def __init__(self, *, project_id: str, model_id: str): ...
    @overload
    def __init__(self, *, project_id: str, model_ids: List[str]): ...

    def __init__(
        self,
        *,
        project_id: str,
        model_id: Optional[str] = None,
        model_ids: Optional[list[str]] = None,
    ):
        if (model_id is None) == (model_ids is None):
            raise ValueError("Provide exactly one of model_id or model_ids")

        self._results: list[Result] = []

        self.project_id = project_id
        self.model_ids: list[str] = []

        if model_id:
            self.model_ids.append(model_id)
        if model_ids:
            self.model_ids.extend(model_ids)

        # model cache
        self.__model_store: Dict[str, Base] = {}

    @property
    def results(self):
        return self._results

    @property
    def current_test_case(self):
        if len(self.results) == 0:
            raise ValueError("Results array is empty")
        return self.results[-1]

    def get(self, prop: str, value: str):
        if len(self.model_ids) == 0:
            raise ValueError("model_id or model_ids is empty")
        if len(self.model_ids) > 1:
            logger.warning("multiple model_ids initialized. Please use 'from_model'")

        model_id = self.model_ids[0]

        speckle_obj = get_last_obj(
            project_id=self.project_id, model_id=model_id, logger=logger
        )

        objs = list(flatten_base(speckle_obj))
        logger.info("Received %i speckle objects", len(objs))
        logger.info("Filtering by %s = %s", prop, value)
        selected = list(filter(lambda obj: property_equal(prop, value, obj), objs))
        logger.info("Filtered %i where %s = %s", len(selected), prop, value)

        self.current_test_case.selected[prop] = value

        return Chainable(selected, self.current_test_case)

    def it(self, descr: str):
        logger.info("Running test: %s", descr)
        self.results.append(Result(descr))

    def from_model(self, model_id: str) -> Chainable:
        if model_id not in self.model_ids:
            raise ValueError("Model id has not been initialized")

        speckle_obj = get_last_obj(
            project_id=self.project_id, model_id=model_id, logger=logger
        )

        objs = list(flatten_base(speckle_obj))

        return Chainable(objs, self.current_test_case)

    def run(self, *specs: Callable):
        """
        Runs any number of spec functions passed by args
        Args:
            *specs: Callable
        """
        print_info(specs)

        for i, spec in enumerate(specs):
            if not callable(spec):
                print(
                    "Warning - parameter at position "
                    + f"{i}"
                    + " is not spec function."
                )
                continue
            spec()

        # print results
        print_results(self.results)

    def detect_collision(
        self, set_a: Chainable, set_b: Chainable, min_dist=0.0
    ) -> List[Collision]:
        """
        Check collision between all elements of two sets
        Args:
            set_a: Chainable
            set_b: Chainable
            min_dist: A distance between elements smaller than this will show as a clash.
                Default = 0. Elements whose face are touching don't register as a collision
        """

        results = self.current_test_case

        results.type = "collision"

        logger.info("Executing collision detection")
        set_a_string = serialize_set(set_a)
        set_b_string = serialize_set(set_b)
        collisions = clash_detection(set_a_string, set_b_string, min_dist)

        logger.info(f"Found {len(collisions)} collision(s)")

        results.collision_results = collisions

        if len(collisions) > 0:
            for c in collisions:
                log_collision(logger, c, set_a.content, set_b.content)

        return collisions

    def get_results(self) -> list[Any]:
        """
        Gets the flattened list of Results
        """

        total_results = []
        for result in self.results:
            total_results.extend(result.to_records())
        return total_results
