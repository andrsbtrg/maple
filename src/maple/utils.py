from .models import Result


RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"
ENDC = "\033[0m"


def print_title(text: str):
    character = "="
    max_length = 73
    padded = f" {text} "
    n = int((max_length - len(padded)) / 2)
    print(f"{character*n}{padded}{character*n}")


def print_results(test_cases: list[Result]):
    """
    Prints results to std-out
    """

    print_title("Test results")
    print()
    table = []
    for case in test_cases:
        assertions = case.assertions
        for assertion in assertions:
            row = [case.spec_name]
            if len(assertion.failing) > 0:
                row.append(RED + "Failed" + ENDC)
            else:
                row.append(GREEN + "Passed" + ENDC)
            table.append(row)
    for row in table:
        print("| {:<60} | {:<6} |".format(*row))
