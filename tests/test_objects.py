from maple.ops import deep_get


def test_deep_get():
    obj = {"outer": {"inner": {"value": 10}}}

    value = deep_get(obj, "outer")
    assert value is not None
    assert value == {"inner": {"value": 10}}

    value = deep_get(obj, "outer.inner")
    assert value is not None
    assert value == {"value": 10}

    value = deep_get(obj, "outer.inner.value")
    assert value is not None
    assert value == 10

    value = deep_get(obj, "outer.inner.value.x")
    assert value is None
