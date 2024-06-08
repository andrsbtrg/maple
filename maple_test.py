import maple as mp


def spec_a():
    mp.it("checks window height is greater than 2600 mm")

    mp.get('category', 'Windows')\
        .where('speckle_type',
               'Objects.Other.Instance:Objects.Other.Revit.RevitInstance')\
        .its('Height')\
        .should('be.greater', 2600)  # assert

def spec_b():
    mp.it("validates SIP 202mm wall type area is greater than 50 m2")

    mp.get('family', 'Basic Wall')\
        .where('type', 'SIP 202mm Wall - conc clad')\
        .its('Area')\
        .should('be.greater', 43)

def spec_c():
    mp.it("checks pipe radius")

    mp.get('FamilyType', 'Rohr-PVC').its('Radius').should('be.equal', 20.0)

def spec_d():
    mp.it("validates basic roof`s thermal mass")

    mp.get('family', 'Basic Roof').its('Thermal Mass').should('be.equal', 20.512)

def spec_e():
    mp.it("validates columns assembly type.")

    mp.get('family', 'M_Concrete-Round-Column with Drop Caps').its('Assembly Code').should('be.equal', 'B10')

def spec_f():
    mp.it("validates ceiling thickness is 50")

    mp.get('category', 'Ceilings')\
        .where('type',  '3000 x 3000mm Grid')\
        .its('Absorptance').should('be.equal', 0.1)

mp.run(spec_a, spec_b)
