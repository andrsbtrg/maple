from time import strftime
import os
from .models import Result
from jinja2 import Environment, FileSystemLoader


class HtmlReport:
    def __init__(self, results: list[Result]) -> None:
        self.results = results
        self.template_file = "report.html"
        return

    def create(self, output_path: str) -> int:
        """
        Generates a HTML report at the output_path directory.

        Filename is `maple_report_YYYY-mm-dd_HH-MM-ss`

        Args:
            output_path (str): Destination directory
        Returns:
            int: number of bytes written
        """

        file_loader = FileSystemLoader("src/maple/templates")
        env = Environment(loader=file_loader)
        template = env.get_template(self.template_file)

        output = template.render(results=self.results)
        time = strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"maple_report_{time}.html"
        output_path = os.path.join(output_path, filename)
        with open(output_path, "w") as file:
            return file.write(output)
