import maple as mp


def test_init():
    stream_id = "24fa0ed1c3"
    # pass None to force mp to use the stream id to get object
    mp.init(None)
    mp.stream(stream_id)
    mp.run(spec)
    assert mp._stream_id == stream_id
    return


# def test_fail_init():
#     import maple as mp
#     # NOTE: this test fails because mp.stream was called on another test,
#     # and it stores the stream inside of the module which is a singleton
#     mp.init(None)
#     with pytest.raises(Exception):
#         mp.run(spec)
#     return


def spec():
    mp.it("checks window height is greater than 2600 mm")

    mp.get('category', 'Windows')\
        .where('speckle_type',
               'Objects.Other.Instance:Objects.Other.Revit.RevitInstance')\
        .its('Height')\
        .should('be.greater', 2600)  # assert
