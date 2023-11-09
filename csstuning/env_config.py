import os

class EnvironmentConfig:
    def __init__(self):
        self._config = {
            # "DATABASE_URL": self._get_env_variable("DATABASE_URL"),
            # "API_KEY": self._get_env_variable("API_KEY", mandatory=False, default="default_api_key"),
        }

    def _get_env_variable(self, name, mandatory=True, default=None):
        value = os.getenv(name, default)
        if mandatory and value is None:
            raise EnvironmentError(f"Required environment variable '{name}' is not set.")
        return value

    def get(self, name):
        return self._config.get(name)

env_config = EnvironmentConfig()