import setup  # noqa
import maple as mp


def main():
    mp.init_model(project_id="71930218fb", model_id="7afea205ae")
    mp.run(test_check_wall_area)


def test_check_wall_area():
    mp.it("Checks that the door height is at least 2.0 m")

    mp.get("properties.Constraints.Base Constraint", "Level: Level 1").its(
        "properties.Constraints.Base Constraint"
    ).should("have.value", "Level: Level 1")


if __name__ == "__main__":
    main()
