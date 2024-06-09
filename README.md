# Maple

### Automate your model Quality Check with Speckle and Maple

### About:

Maple is a library designed to write simple code that can check different attributes of a Model in Speckle.

Using Maple you can write `test specs` that check any parameter or quantity inside the project model.

`Maple` can be integrated into [Speckle Automate]() to run the quality check tests on a continuous integration and ensure project standards.

### Get started:
To run locally:

```py
import maple as mp

def spec_a():
    mp.it("checks window height is greater than 2600 mm")

    mp.get('category', 'Windows')\
        .where('speckle_type',
               'Objects.Other.Instance:Objects.Other.Revit.RevitInstance')\
        .its('Height')\
        .should('be.greater', 2600)

mp.run(spec_a)
``
