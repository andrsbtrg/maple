from dotenv import load_dotenv
import pytest
import logging

from maple.base.maple import Maple

logging.basicConfig(level=logging.DEBUG)

load_dotenv()


project_id = "21f8910cc7"


@pytest.fixture
def spec_fixture():
    mp = Maple(project_id=project_id, model_id="f4a1103c37")

    def spec():
        min_height = 900
        mp.it(f"checks window height is greater than {min_height} mm")

        mp.get("category", "Windows").where(
            "speckle_type", "Objects.Other.Instance:Objects.Other.Revit.RevitInstance"
        ).its("Height").should("be.greater", min_height)

    return mp, spec


def test_success_run(spec_fixture):
    mp: Maple = spec_fixture[0]
    spec = spec_fixture[1]
    mp.run(spec)
    assert mp.project_id == project_id
    test_case = mp.current_test_case

    assert test_case is not None
    assert len(test_case.assertions) == 1
    assert test_case.assertions[0].passed()
    assert not test_case.assertions[0].failed()

    return


def test_error_run(spec_fixture):
    mp: Maple = spec_fixture[0]
    spec = spec_fixture[1]

    some = "hello"
    other = {"name": "i'm a function"}
    mp.run(spec, some, other)  # type: ignore
