from typing import Self
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.api import operations
from specklepy.transports.server.server import ServerTransport
from .base_extensions import flatten_base


class Chainable:
    def __init__(self, data):
        self.content = data

    def should(self, *args) -> Self:
        """
        Assert something inside the Chainable
        """
        print(args)
        return Chainable('should')

    def its(self, *args) -> Self:
        """
        Selector of what is inside the Chainable object
        """
        print(args)
        return Chainable('its')

    def where(self, *args) -> Self:
        """
        filters more the Chainable
        """
        print("Filtering by:", *args)

        print(self.content)
        selected = list(filter(lambda obj: property_equal(
            args[0], args[1], obj), self.content))
        print("Got", len(selected), args[1])
        return Chainable(selected)


def get(*args) -> Chainable:
    """Mostly do speckle queries and then
    save them inside the Chainable object"""

    print("Getting", *args)

    # get something
    client = SpeckleClient(host='https://latest.speckle.systems')
    # authenticate the client with a token
    account = get_default_account()
    client.authenticate_with_account(account)

    stream_id = "24fa0ed1c3"
    # print(client)
    # stream = client.stream.get(id=stream_id)

    transport = ServerTransport(client=client, stream_id=stream_id)

    last_obj_id = client.commit.list(stream_id)[0].referencedObject
    last_obj = operations.receive(
        obj_id=last_obj_id, remote_transport=transport)

    objs = list(flatten_base(last_obj))

    selected = list(filter(
        lambda obj: property_equal(args[0], args[1], obj), objs))
    print("Got", len(selected), args[1])

    return Chainable(selected)


def it(test_name):
    """
    Declare a Spec and log it in the console
    Also should create a new Queue of chainables
    """
    print("Running test:", test_name)
    return


def property_equal(propName, value, obj):
    try:
        return obj[propName] == value
    except Exception:
        return False
