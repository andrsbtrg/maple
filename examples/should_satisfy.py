import setup  # noqa
import maple as mp

import logging

logging.basicConfig(level=logging.INFO)


def main():
    mp.init_model(project_id="71930218fb", model_id="7afea205ae")
    mp.run(test_check_door_width_ext)


def test_check_door_width():
    mp.it("Checks that the door level width is greater than 900")

    mp.get("ifcType", "IFCDOOR").its("properties.BaseQuantities.Width").should(
        "be.greater", 900
    )


def test_check_door_width_ext():
    mp.it("Checks that the door level width is between 900 and 1500 mm")

    mp.get("ifcType", "IFCDOOR").its("properties.BaseQuantities.Width").should_satisfy(
        lambda x: x > 900 and x <= 1500
    )


def test_height_with_function():
    mp.it("Checks that the door level width is between 900 and 1500 mm")

    mp.get("category", "Windows").where("level", "L2").its("location").should_satisfy(
        between_level_1_2
    )


def between_level_1_2(location) -> bool:
    # The object's location is an object that contains {x, y, y}
    height = location.z
    return height > 3 and height < 6


if __name__ == "__main__":
    main()
