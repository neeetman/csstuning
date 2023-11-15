import json
from pathlib import Path
from csstuning.config_space import ConfigSpace
from csstuning.config import config_loader


class GCCConfigSpace(ConfigSpace):
    def __init__(self):
        super().__init__(self._load_config())

        self.align_flags = [
            "align-functions",
            "align-jumps",
            "align-labels",
            "align-loops",
        ]
        self.quaternions = self._create_quaternions_mapping()
        self._setup_align_flags()

    @staticmethod
    def _load_config():
        env_conf = config_loader.get_config()
        conf_dir = Path(env_conf.get("compiler", "compiler_config_dir"))
        conf_space_file = conf_dir / "gcc_flags_104.json"

        try:
            with open(conf_space_file, "r") as file:
                return json.load(file)
        except Exception as e:
            raise FileNotFoundError(f"Unable to load the configuration file: {e}")

    def generate_flags_str(self):
        flags_str = ""
        for name, entry in self.config_items.items():
            if entry.type == "enum":
                if entry.current_value == "ON":
                    flags_str += f" -f{name}"
                else:
                    flags_str += f" -fno-{name}"
            elif entry.type == "integer" and entry.name in self.align_flags:
                value = self.integer_to_quaternion(entry.current_value)
                if value.strip() != "":
                    flags_str += f" -f{name}={value}"
                else:
                    flags_str += f" -fno-{name}"

    def integer_to_quaternion(self, value):
        return self.quaternions[value]

    def _setup_align_flags(self):
        """For align flags, we have 4 parameters: n, m, n1, m1"""
        for flag in self.align_flags:
            self.config_items[flag].max_value = len(self.quaternions) - 1

    @staticmethod
    def _create_quaternions_mapping():
        n_values = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        m_values = [0, 1, 3, 7, 15, 31, 63]

        # handle the case where n, n1, m, m1 = 0
        def format_quaternion(n, m, n1, m1):
            parts = []
            if n > 0:
                parts.append(str(n))
                if m > 0:
                    parts.append(str(m))
            if n1 > 0:
                parts.append(str(n1))
                if m1 > 0:
                    parts.append(str(m1))
            return ":".join(parts)
    
        return [
            format_quaternion(n, m, n1, m1)
            for n in n_values for m in m_values if m < n
            for n1 in n_values if n1 < n
            for m1 in m_values if m1 < n1
        ]


class LLVMConfigSpace(ConfigSpace):
    def __init__(self):
        super().__init__(self._load_config())

    @staticmethod
    def _load_config():
        env_conf = config_loader.get_config()
        conf_dir = Path(env_conf.get("compiler", "compiler_config_dir"))
        conf_space_file = conf_dir / "llvm_passes_82.json"

        try:
            with open(conf_space_file, "r") as file:
                return json.load(file)
        except Exception as e:
            raise FileNotFoundError(f"Unable to load the configuration file: {e}")
        
    def generate_flags_str(self):
        pass
