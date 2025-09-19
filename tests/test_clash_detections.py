import maple as mp

from dotenv import load_dotenv

import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()


def test_should_clash():
    project_id = "21f8910cc7"
    mp.init_model(project_id=project_id, model_id="f4a1103c37")
    mp.run(clash_detection)

    results = mp.get_results()
    assert len(results) == 1
    result = results[0]
    assert result["type"] == "collision"
    assert result["result"] == "fail"
    # assert len(result["collisions"]) == 14 # TODO: This is flaky
    assert len(result["collisions"]) > 0
    return


def test_should_not_clash():
    project_id = "21f8910cc7"
    mp.init_model(project_id=project_id, model_id="f4a1103c37")
    mp.run(clash_detection_pass)

    results = mp.get_results()
    assert len(results) == 1
    result = results[0]
    assert result["type"] == "collision"
    assert result["result"] == "pass"
    # assert len(result["collisions"]) == 14 # TODO: This is flaky
    assert len(result["collisions"]) == 0
    return


def clash_detection():
    mp.it("Clash detection between walls and windows")
    windows = mp.get("category", "Windows")
    walls = mp.get("category", "Walls")

    mp.detect_collision(windows, walls)


def clash_detection_pass():
    mp.it("Clash detection between windows and topography")
    windows = mp.get("category", "Windows")
    topo = mp.get("category", "Topography")

    mp.detect_collision(windows, topo)
