import os
from jinja2 import Environment, FileSystemLoader


def generate_config(template_path, output_path, config_dict):
    working_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(working_dir, output_path)

    env = Environment(loader=FileSystemLoader(working_dir))
    template = env.get_template(template_path)
    config = template.render(config_dict)

    with open(output_path, "w") as file:
        file.write(config)

    