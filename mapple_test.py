import mapple as mp


def spec_a():
    mp.it("Windows should be at least 1.70 m")

    mp.get('category', 'Window').its('Height').should('be.greater', 1.70)


def spec_b():
    mp.it("validate geometry by id")

    mp.get('id', 'adf38u9asf8').should('not.touch', '19283908f')


def spec_c():
    mp.it("checks collision between pipes")
    mp.get('FamilyType', 'Rohr-PVC').its('Radius').should('be.equal', 20.0)
    mp.get('Family')

spec_a()