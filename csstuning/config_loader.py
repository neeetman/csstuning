import configparser
from importlib import resources

class ConfigLoader:
    def __init__(self, environment='default'):
        self.config = configparser.ConfigParser()
        with resources.path('csstuning.config', f'{environment}.conf') as config_path:
            self.config.read(config_path)

    def get_config(self):
        return self.config

# Global instance of the ConfigLoader to be imported in other modules
config_loader = ConfigLoader()

def get_config():
    """Convenience function to get the global config."""
    return config_loader.get_config()