import setup  # noqa
import maple as mp

import logging

logging.basicConfig(level=logging.INFO)


def main():
    mp.init_model(project_id="21f8910cc7", model_id="f4a1103c37")
    mp.run(test_height_with_function)
    print(mp.get_results())


def test_height_with_function():
    mp.it("Checks that the windows markes as L2 have a correct location")

    mp.get(
        "speckle_type", "Objects.Data.DataObject:Objects.Data.RevitObject"
    ).should_satisfy(naming_convention)


def naming_convention(name) -> bool:
    # The object's location is a Speckle object that contains {x, y, y}
    print(name)
    return True


if __name__ == "__main__":
    main()
