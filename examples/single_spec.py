import setup  # noqa
import maple as mp


def main():
    mp.init_model(project_id="1471fed2c0", model_id="53db0711db")
    mp.set_logging(True)
    mp.run(test_check_door_height)
    mp.generate_report(output_path="/tmp/")


def test_check_door_height():
    mp.it("Checks that the door height its at least 2.0 m")

    mp.get("ifcType", "IFCSPATIALZONE").its("ownerId").should("be.equal", 1)


if __name__ == "__main__":
    main()
