import maple as mp
import os
from dotenv import load_dotenv

load_dotenv()


def test_multiple_runs():
    project_id = "21f8910cc7"
    mp.init_model(project_id=project_id, model_id="f4a1103c37")
    mp.run(spec)
    assert len(mp.get_test_cases()) == 1
    assert mp.get_current_test_case() is not None
    # Initialize a second model to test should clear results
    mp.init_model(project_id=project_id, model_id="f4a1103c37")
    assert len(mp.get_test_cases()) == 0
    assert mp.get_current_test_case() is None
    mp.run(spec)

    assert len(mp.get_test_cases()) == 1


def spec():
    min_height = 900
    mp.it(f"checks window height is greater than {min_height} mm")

    mp.get("category", "Windows").where(
        "speckle_type", "Objects.Other.Instance:Objects.Other.Revit.RevitInstance"
    ).its("Height").should("be.greater", min_height)
