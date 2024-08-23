from os import path
import maple as mp
from maple import HtmlReport


def test_report(tmp_path):
    dir = tmp_path / "sub"
    dir.mkdir()
    results = mp.get_test_cases()
    report = HtmlReport(results)
    output_path = report.create(dir)
    assert path.exists(output_path)
    with open(output_path) as file:
        assert file.read() != ""
