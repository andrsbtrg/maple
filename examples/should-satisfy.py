import setup  # noqa
import maple as mp

import logging

logging.basicConfig(level=logging.INFO)


def main():
    mp.init_model(project_id="71930218fb", model_id="7afea205ae")
    mp.run(test_check_door_width_ext)


def test_check_door_width_ext():
    mp.it("Checks that the door level width is between 900 and 1500 mm")

    mp.get("ifcType", "IFCDOOR").its("properties.BaseQuantities.Width").should_satisfy(
        lambda x: x > 900 and x <= 1500
    )


if __name__ == "__main__":
    main()
