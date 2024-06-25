import maple as mp


def test_success_run():
    stream_id = "24fa0ed1c3"
    mp.stream(stream_id)
    mp.run(spec)
    assert mp._stream_id == stream_id
    test_case = mp.get_current_test_case()

    assert test_case is not None
    assert len(test_case.assertions) == 1
    assert not test_case.assertions[0].passed()
    assert test_case.assertions[0].failed()

    return


def test_error_run():
    some = "hello"
    other = {"name": "i'm a function"}
    mp.run(spec, some, other)  # type: ignore


def spec():
    mp.it("checks window height is greater than 2600 mm")

    mp.get("category", "Windows").where(
        "speckle_type", "Objects.Other.Instance:Objects.Other.Revit.RevitInstance"
    ).its("Height").should("be.greater", 2600)  # assert
