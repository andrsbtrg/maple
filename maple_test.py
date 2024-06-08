import maple as mp


def spec_a():
    mp.it("Windows should be at least 1.70 m")

    mp.get('category', 'Windows')\
        .where('speckle_type',
               'Objects.Other.Instance:Objects.Other.Revit.RevitInstance')\
        .its('Height')\
        .should('be.greater', 2800)  # assert


def spec_b():
    mp.it("validate geometry by id")

    mp.get('family', 'Basic Wall')\
        .where('type', 'SIP 202mm Wall - conc clad')\
        .its('Area')\
        .should('be.greater', 0)


def spec_c():
    mp.it("checks collision between pipes")
    mp.get('FamilyType', 'Rohr-PVC').its('Radius').should('be.equal', 20.0)
    mp.get('Family')


mp.run(spec_a, spec_b)
