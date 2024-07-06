import maple as mp
from maple import HtmlReport


def test_report(tmp_path):
    dir = tmp_path / "sub"
    dir.mkdir()
    results = mp.get_test_cases()
    report = HtmlReport(results)
    bytes_written = report.create(dir)
    assert bytes_written != 0
