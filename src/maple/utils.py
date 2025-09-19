import logging
from acers import Collision
from specklepy.objects import Base
from .models import Result
from typing import Tuple, List

import os


def use_colors() -> bool:
    no_color = os.getenv("NO_COLOR")
    return no_color is None or no_color != "1"


if use_colors():
    RED = "\033[1;31m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    REVERSE = "\033[;7m"
    ENDC = "\033[0m"
else:
    RED = BLUE = CYAN = GREEN = RESET = BOLD = REVERSE = ENDC = ""


def print_title(text: str):
    character = "="
    max_length = 64
    padded = f" {text} "
    n = int((max_length - len(padded)) / 2)
    print(f"{character * n}{padded}{character * n}")


def print_results(test_cases: list[Result]):
    """
    Prints results to std-out
    """

    print()
    print_title("Test results")
    print()
    table = []
    for case in test_cases:
        for assertion in case.assertions:
            row = [case.spec_name]
            if len(assertion.failing) > 0:
                row.append(RED + "Failed" + ENDC)
            else:
                row.append(GREEN + "Passed" + ENDC)
            table.append(row)
        if case.type == "collision":
            row = [case.spec_name]
            if len(case.collision_results) > 0:
                row.append(RED + "Failed" + ENDC)
            else:
                row.append(GREEN + "Passed" + ENDC)
            table.append(row)

    for row in table:
        print("| {:<55} | {:<6} |".format(*row))


def log_collision(
    logger: logging.Logger, c: Collision, set_a: List[Base], set_b: List[Base]
):
    # element_1 = next((base for base in set_a if base.id == c[0]), None)
    # if element_1 is None:
    #     element_1 = next(base for base in set_a if base.id == c[1])
    #     element_2 = next(base for base in set_b if base.id == c[0])
    # else:
    #     element_2 = next(base for base in set_b if base.id == c[1])

    logger.info(f"Clash between {c.ids[0]} and {c.ids[1]}")
