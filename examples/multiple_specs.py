import setup  # noqa
import maple as mp


def main():
    stream_id = "24fa0ed1c3"
    mp.init_model(project_id=stream_id, model_id="2696b4a381")
    mp.set_logging(True)
    mp.run(spec_a, spec_b, spec_c, spec_d, spec_e, spec_f, spec_g)
    mp.generate_report(".")


def spec_a():
    mp.it("checks window height is greater than 2600 mm")

    mp.get("category", "Windows").where(
        "speckle_type", "Objects.Other.Instance:Objects.Other.Revit.RevitInstance"
    ).its("Height").should("be.greater", 2600)


def spec_b():
    mp.it("validates SIP 202mm wall type area is greater than 43 m2")

    mp.get("family", "Basic Wall").where("type", "SIP 202mm Wall - conc clad").its(
        "Area"
    ).should("be.greater", 43)


def spec_c():
    mp.it("checks pipe radius")

    mp.get("category", "Plumbing Fixtures").its("OmniClass Title").should(
        "have.value", "Bathtubs"
    )


def spec_d():
    mp.it("validates basic roof`s thermal mass")

    mp.get("family", "Basic Roof").where("type", "SG Metal Panels roof").its(
        "Thermal Mass"
    ).should("be.equal", 20.512)


def spec_e():
    mp.it("validates columns assembly type.")

    mp.get("family", "M_Concrete-Round-Column with Drop Caps").its(
        "Assembly Code"
    ).should("have.value", "B10")


def spec_f():
    mp.it("validates ceiling thickness is 50")

    mp.get("category", "Ceilings").where("type", "3000 x 3000mm Grid").its(
        "Absorptance"
    ).should("be.equal", 0.1)


def spec_g():
    mp.it("Checks there are exactly 55 walls")

    mp.get("category", "Walls").should("have.length", 55)


if __name__ == "__main__":
    main()
