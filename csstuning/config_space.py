import random


class ConfigItem:
    def __init__(self, name, data):
        self.name = name
        self.type = data.get("type")
        self.enum_values = data.get("enum_values")
        self.min_value = data.get("min")  # Minimum value for integers
        self.max_value = data.get("max")  # Maximum value for integers
        self.scope = data.get("scope")

        if self.type == "integer":
            self.default = int(data.get("default", self.min_value))
        else:
            self.default = data.get("default")

        self.current_value = self.default

    def get_current_value(self):
        return self.current_value

    def set_current_value(self, value):
        # For integer type, check if the value is within the min and max range
        if self.type == "integer":
            if not (self.min_value <= int(value) <= self.max_value):
                raise ValueError(
                    f"{self.name} must be between {self.min_value} and {self.max_value}."
                )
        # If the type is enum, check if the value is within the allowed values
        elif self.type == "enum" and value not in self.enum_values:
            raise ValueError(f"{self.name} must be one of {self.enum_values}.")

        self.current_value = value

    def set_random_value(self):
        if self.type == "integer":
            self.current_value = random.randint(self.min_value, self.max_value)
        elif self.type == "enum":
            self.current_value = random.choice(self.enum_values)
        else:
            raise TypeError(f"Random value is not defined for type '{self.type}'.")

    def get_default_value(self):
        return self.default

    def get_range(self):
        if self.type == "enum":
            return self.enum_values
        elif self.type == "integer":
            return (self.min_value, self.max_value)
        else:
            raise TypeError(f"Range is not defined for type '{self.type}'.")

    def get_type(self):
        return self.type

    def reset_to_default(self):
        self.current_value = self.default

    def get_details(self):
        details = {
            "name": self.name,
            "default": self.default,
            "current_value": self.current_value,
            "type": self.type,
            "range": self.get_range(),
        }
        return details


class ConfigSpace:
    def __init__(self, config_data):
        self.config_items = {
            name: ConfigItem(name, data) for name, data in config_data.items()
        }

    def get_current_config(self) -> dict:
        return {
            name: item.get_current_value() for name, item in self.config_items.items()
        }

    def set_current_config(self, config: dict):
        if config is None:
            return

        for name, value in config.items():
            self.set_option_value(name, value)

    def set_random_config(self):
        for item in self.config_items.values():
            item.set_random_value()

    def reset_all_to_defaults(self):
        for item in self.config_items.values():
            item.reset_to_default()

    def get_all_details(self) -> dict:
        return {name: item.get_details() for name, item in self.config_items.items()}

    def get_option_details(self, name) -> dict:
        item = self._validate_option_name(name)
        return item.get_details()

    def set_option_value(self, name, value):
        item = self._validate_option_name(name)
        item.set_current_value(value)

    def reset_option_to_default(self, name):
        item = self._validate_option_name(name)
        item.reset_to_default()

    def _validate_option_name(self, name):
        if name not in self.config_items:
            raise KeyError(
                f"The option '{name}' is not found in the configuration space."
            )
        return self.config_items[name]
