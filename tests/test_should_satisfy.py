import maple as mp
from dotenv import load_dotenv

load_dotenv()


def test_success_run():
    project_id = "21f8910cc7"
    mp.init_model(project_id=project_id, model_id="f4a1103c37")
    mp.run(spec)
    results = mp.get_results()
    assert len(results) == 1


def spec():
    min_height = 900
    mp.it(f"checks window height is greater than {min_height} mm")

    mp.get("category", "Windows").where(
        "speckle_type", "Objects.Other.Instance:Objects.Other.Revit.RevitInstance"
    ).its("Height").should_satisfy(lambda x: x > min_height)
