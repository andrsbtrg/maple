import setup  # noqa
import logging

from maple.base import Maple

mp = Maple(model_id="53db0711db", project_id="1471fed2c0")

logging.basicConfig(level=logging.INFO)


def main():
    mp.run(test_check_door_height)
    # mp.generate_report(output_path="/tmp/")


def test_check_door_height():
    mp.it("Checks that the door height its at least 2.0 m")

    mp.get("ifcType", "IFCSPATIALZONE").its("ownerId").should("be.equal", 2)


if __name__ == "__main__":
    main()
