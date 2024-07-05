from .models import Result
from jinja2 import Environment, FileSystemLoader


class HtmlReport:
    def __init__(self, results: list[Result]) -> None:
        self.results = results
        return

    def create(self, output_path: str) -> None:
        """
        Generate a HTML report at the output_path

        Args:
            output_path (str): Destination directory
        """

        file_loader = FileSystemLoader("src/maple/templates")
        env = Environment(loader=file_loader)
        template = env.get_template("report.html")

        output = template.render(results=self.results)
        with open(output_path + "report.html", "a+") as file:
            file.write(output)

        return
