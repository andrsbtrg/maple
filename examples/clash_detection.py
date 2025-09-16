import maple as mp

import logging

logging.basicConfig(level=logging.INFO)

mp.init_model(project_id="21f8910cc7", model_id="f4a1103c37")


def clash_detection():
    mp.it("Clash detection between walls and windows")
    windows = mp.get("category", "Windows")
    walls = mp.get("category", "Walls")

    mp.detect_collision(windows, walls)


mp.run(clash_detection)

print(mp.get_results())
