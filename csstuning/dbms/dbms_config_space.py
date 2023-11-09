import json
from importlib import resources
from csstuning.config_space import ConfigSpace


class MySQLConfigSpace(ConfigSpace):
    def __init__(self, config_file=None):
        config_data = None

        if config_file is not None:
            # Try to load the user-provided config file
            try:
                with open(config_file, "r") as file:
                    config_data = json.load(file)
            except Exception as e:
                raise FileNotFoundError(f"Unable to load the configuration file: {e}")
        else:
            # Fallback to the package resource
            config_package = "cssbench.dbms.config.mysql"
            resource_path = "mysql_all_197.json"
            try:
                config_data = json.loads(resources.read_text(config_package, resource_path))
            except Exception as e:
                raise FileNotFoundError(f"Unable to load the internal configuration resource: {e}")

        super().__init__(config_data)

    def generate_config_file(self, output_file_path): 
        config_lines = ["[mysqld]"]
        for key, value in self.get_current_config().items():
            config_line = f"{key} = {value}"
            config_lines.append(config_line)
        
        config_content = "\n".join(config_lines)

        with open(output_file_path, 'w') as config_file:
            config_file.write(config_content)
