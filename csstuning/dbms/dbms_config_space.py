import json
from pathlib import Path
from csstuning.config_space import ConfigSpace
from csstuning.config import config_loader


class MySQLConfigSpace(ConfigSpace):
    def __init__(self):
        config_data = None

        env_conf = config_loader.get_config()
        conf_dir = Path(env_conf.get("database", "dbms_config_dir"))

        config_space_file = conf_dir / "mysql_all_197.json"
        try:
            with open(config_space_file, "r") as file:
                config_data = json.load(file)
        except Exception as e:
            raise FileNotFoundError(f"Unable to load the configuration file: {e}")

        super().__init__(config_data)

    def set_current_config(self, config):
        if config is None:
            return

        for name, value in config.items():
            self.set_option_value(name, value)

    def generate_config_file(self, output_file_path):
        config_lines = ["[mysqld]"]
        for key, value in self.get_current_config().items():
            config_line = f"{key} = {value}"
            config_lines.append(config_line)

        config_content = "\n".join(config_lines)

        with open(output_file_path, "w") as config_file:
            config_file.write(config_content)
