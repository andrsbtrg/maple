import maple as mp


def test_success_run():
    stream_id = "24fa0ed1c3"
    mp.stream(stream_id)
    mp.run(spec)
    assert mp._stream_id == stream_id
    test_case = mp.get_current_test_case()

    assert test_case is not None
    assert len(test_case.assertions) == 1
    assert test_case.assertions[0].passed()
    assert not test_case.assertions[0].failed()

    return


def test_error_run():
    some = "hello"
    other = {"name": "i'm a function"}
    mp.run(spec, some, other)  # type: ignore


def test_multiple_streams():
    stream_id = "24fa0ed1c3"
    mp.stream(stream_id)
    mp.run(spec)

    # We set the stream id to another, it doesn't
    # matter that is not valid since we will not use it to query
    mp.stream("other")

    # Setting the stream should reset the current object
    assert mp.get_current_obj() is None


def spec():
    min_height = 900
    mp.it(f"checks window height is greater than {min_height} mm")

    mp.get("category", "Windows").where(
        "speckle_type", "Objects.Other.Instance:Objects.Other.Revit.RevitInstance"
    ).its("Height").should("be.greater", min_height)
