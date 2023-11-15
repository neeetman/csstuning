import configparser
import os
from pathlib import Path
from importlib import resources


class ConfigLoader:
    def __init__(self, environment="default"):
        csstuning_dir = self._read_cstuning_dir()

        config_path = Path(csstuning_dir, f"{environment}.conf")

        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        for section in self.config.sections():
            for key, value in self.config.items(section):
                if "{csstuning_dir}" in value:
                    self.config.set(
                        section, key, value.format(csstuning_dir=csstuning_dir)
                    )

    def _read_cstuning_dir(self):
        default_prefix = os.path.expanduser("~")
        install_info_path = Path(default_prefix, ".csstuing.ini")

        if install_info_path.exists():
            config = configparser.ConfigParser()
            config.read(install_info_path)
            return config.get("DEFAULT", "CSSTUNING_DIR", fallback=default_prefix)
        return default_prefix

    def get_config(self):
        return self.config


# Global instance of the ConfigLoader to be imported in other modules
config_loader = ConfigLoader()


def get_config():
    """Convenience function to get the global config."""
    return config_loader.get_config()
