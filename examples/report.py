# Add the path of src to sys.path
from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root) + "/src")
# end

from maple.models import Result
from maple.report import HtmlReport

results = [Result("a test case")]
report = HtmlReport(results)

report.create("")
