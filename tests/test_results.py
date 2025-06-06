import maple as mp
from dotenv import load_dotenv

from maple.ops import CompOp

load_dotenv()

min_height = 900
spec_name = f"checks window height is greater than {min_height} mm"


def test_results():
    stream_id = "24fa0ed1c3"
    mp.init_model(project_id=stream_id, model_id="2696b4a381")
    mp.run(spec)
    results = mp.get_results()
    assert len(results) == 1
    result = results[0]
    assert result["spec_name"] == spec_name
    assert result["get"] == [
        "category = Windows",
        "speckle_type = Objects.Other.Instance:Objects.Other.Revit.RevitInstance",
    ]
    assert result["spec"]["selector"] == "Height"
    assert result["spec"]["comparer"] == CompOp.BE_GREATER
    assert result["spec"]["value"] == min_height
    assert result["result"] == "pass"


def spec():
    mp.it(spec_name)

    mp.get("category", "Windows").where(
        "speckle_type", "Objects.Other.Instance:Objects.Other.Revit.RevitInstance"
    ).its("Height").should("be.greater", min_height)
