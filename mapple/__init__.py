from typing import Self


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


def get(*args) -> Chainable:
    """Mostly do speckle queries and then
    save them inside the Chainable object"""
    # get something

    something = "some data to assert"
    print(args)
    return Chainable(something)


def it(test_name):
    """
    Declare a Spec and log it in the console
    Also should create a new Queue of chainables
    """
    print(test_name)
    pass
