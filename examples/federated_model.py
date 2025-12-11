from maple.base import Maple
from maple.utils import print_results
import logging

logging.basicConfig(level=logging.INFO)

arch_model = "045cdb6d44"
str_model = "df3fa4e97d"
mp = Maple(
    project_id="566869f9e6",
    model_ids=[arch_model, str_model],
)


def clash():
    mp.it("Clash detection between multiple models")
    windows = mp.from_model(arch_model).get("properties.ifcType", "IfcWindow")
    walls = mp.from_model(str_model).get("ifcType", "IfcColumn")

    mp.detect_collision(windows, walls)


def other_test():
    mp.it("other test")
    windows = mp.from_model(arch_model).get("properties.ifcType", "IfcWindow")
    windows.its("properties.ifcType").should("have.value", "ifcWindow")

    columns = mp.from_model(str_model).get("ifcType", "IfcColumn")
    columns.its("ifcType").should("have.value", "ifcColumn")


mp.run(other_test, clash)
