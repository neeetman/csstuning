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

        if self._validate_constraint() is False:
            log_file_size = self.config_items["innodb_log_file_size"].current_value
            log_files_in_group = self.config_items["innodb_log_files_in_group"].current_value
            thread_concurrency = self.config_items["innodb_thread_concurrency"].current_value

            raise ValueError(
                f"Invalid configuration detected:\n"
                f" - Current 'innodb_log_file_size': {log_file_size} (Bytes)\n"
                f" - Current 'innodb_log_files_in_group': {log_files_in_group}\n"
                f" - Current 'innodb_thread_concurrency': {thread_concurrency}\n\n"
                "Constraints violated:\n"
                "1. 'innodb_log_file_size' * 'innodb_log_files_in_group' should be <= 512GB.\n"
                "2. 'innodb_thread_concurrency' * 200 * 1024 should be <= 'innodb_log_file_size' * 'innodb_log_files_in_group'.\n\n"
                "Please adjust your configuration to meet these constraints."
            )
        
    def set_random_config(self):
        valid_config = False
        while not valid_config:
            # Set random values for each configuration item
            for item in self.config_items.values():
                item.set_random_value()

            # Check if the random configuration is valid
            valid_config = self._validate_constraint()

    def _validate_constraint(self):
        # Constraint 1: innodb_log_file_size * innodb_log_files_in_group <= 512GB
        # Constraint 2: innodb_thread_concurrency * 200 * 1024 <= innodb_log_file_size * innodb_log_files_in_group
        log_file_size = self.config_items["innodb_log_file_size"].current_value
        log_files_in_group = self.config_items["innodb_log_files_in_group"].current_value
        thread_concurrency = self.config_items["innodb_thread_concurrency"].current_value

        MAX_LOG_SIZE_BYTES = 512 * 1024**3  # 512GB in bytes

        return (
            log_file_size * log_files_in_group <= MAX_LOG_SIZE_BYTES
            and thread_concurrency * 200 * 1024 <= log_file_size * log_files_in_group
        )

    def generate_config_file(self, output_file_path):
        config_lines = ["[mysqld]"]
        for key, value in self.get_current_config().items():
            config_line = f"{key} = {value}"
            config_lines.append(config_line)

        config_content = "\n".join(config_lines)

        with open(output_file_path, "w") as config_file:
            config_file.write(config_content)
