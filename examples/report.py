# Add the path of src to sys.path
from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root) + "/src")
print(sys.path)
# end

from maple.report import HtmlReport

report = HtmlReport([""])

report.create("")
