from .models import Result
from jinja2 import Template, Environment, FileSystemLoader


class HtmlReport:
    def __init__(self, results: list[Result]) -> None:
        pass

    def create(self, output_path: str) -> None:
        """

        Args:
            output_path (str): _description_
        """

        file_loader = FileSystemLoader("templates")
        env = Environment(loader=file_loader)
        template = env.get_template("report.html")

        output = template.render(name="gizem")
        print(output)
