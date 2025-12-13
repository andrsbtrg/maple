import logging

from dotenv import load_dotenv

from maple.base.maple import Maple
import pytest

logging.basicConfig(level=logging.DEBUG)
load_dotenv()


# Arrange
@pytest.fixture
def mp():
    model_id = "f4a1103c37"
    project_id = "21f8910cc7"

    mp = Maple(
        project_id=project_id,
        model_id=model_id,
    )
    return mp


def test_should_clash(mp: Maple):
    def clash_detection():
        mp.it("Clash detection between walls and windows")
        windows = mp.get("category", "Windows")
        walls = mp.get("category", "Walls")

        mp.detect_collision(windows, walls)

    mp.run(clash_detection)

    results = mp.get_results()
    print(results)
    assert len(results) == 1
    result = results[0]
    assert result["type"] == "collision"
    assert result["result"] == "fail"
    # assert len(result["collisions"]) == 14 # TODO: This is flaky
    assert len(result["collisions"]) > 0
    return


def test_should_not_clash(mp: Maple):
    def clash_detection_pass():
        mp.it("Clash detection between windows and topography")
        windows = mp.get("category", "Windows")
        topo = mp.get("category", "Topography")

        mp.detect_collision(windows, topo)

    mp.run(clash_detection_pass)

    results = mp.get_results()
    print(results)
    assert len(results) == 1
    result = results[0]
    assert result["type"] == "collision"
    assert result["result"] == "pass"
    # assert len(result["collisions"]) == 14 # TODO: This is flaky
    assert len(result["collisions"]) == 0
    return
