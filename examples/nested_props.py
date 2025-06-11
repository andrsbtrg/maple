import setup  # noqa
import maple as mp


def main():
    mp.init_model(project_id="920aec4a8c", model_id="365ae0527b")
    mp.set_logging(True)
    mp.run(test_check_door_height)


def test_check_door_height():
    mp.it("Checks that the windows have correct U-value")

    mp.get("ifcType", "IFCSLAB").its("properties.Qto_SlabBaseQuantities.Depth").should(
        "be.greater", 55
    )


if __name__ == "__main__":
    main()
