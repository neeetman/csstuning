import sys
import unittest
from csstuning.dbms.dbms_config_space import MySQLConfigSpace

sys.path.append("/home/anshao/csstuning")


class TestMysqlConfigSpace(unittest.TestCase):
    def test_generate_config_file(self):
        config_space = MySQLConfigSpace()
        config_space.generate_config_file("test.cnf")


if __name__ == "__main__":
    unittest.main()
