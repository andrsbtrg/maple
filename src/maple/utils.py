from .models import Result


def print_results(test_cases: list[Result]):
    """
    Prints results to std-out
    """
    print("-------------------------------------------------------")
    print("---RESULTS---")
    print("-------------------------------------------------------")
    for case in test_cases:
        print(case.spec_name, end="")
        assertions = case.assertions
        for assertion in assertions:
            if len(assertion.failing) > 0:
                print(" - Failed")
                # print(">> ids:", assertion.failed)
            else:
                print(" - Passed")
