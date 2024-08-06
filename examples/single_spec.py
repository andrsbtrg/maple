import setup  # noqa
import maple as mp


def main():
    mp.init_model(project_id="62bd771c0e", model_id="28e03dc3c7")
    mp.set_logging(True)
    mp.run(test_check_door_height)
    mp.generate_report(output_path=".")


def test_check_door_height():
    mp.it("Checks that the door height its at least 2.0 m")

    mp.get("type", "IFCDOOR").its("OverallHeight").should("be.greater", 2.0)


if __name__ == "__main__":
    main()
