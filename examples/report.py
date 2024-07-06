import setup  # noqa
from maple.models import Result
from maple.report import HtmlReport

results = [Result("a test case")]
report = HtmlReport(results)

report.create("")
