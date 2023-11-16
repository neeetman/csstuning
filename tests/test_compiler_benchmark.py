import sys
sys.path.append("/home/anshao/csstuning")

import unittest

from csstuning.compiler.compiler_benchmark import GCCBenchmark, LLVMBenchmark


class TestCompilerBenchmark(unittest.TestCase):
    def setUp(self):
        workload = "cbench-automotive-bitcount"
        self.gcc_benchmark = GCCBenchmark(workload=workload)
        self.llvm_benchmark = LLVMBenchmark(workload=workload)
        print("\n" + "=" * 50)
        print(f"Starting Test：{self._testMethodName}")
        print("=" * 50)

    def test_01_run_with_default(self):
        # Test for successful execution
        try:
            gcc_result = self.gcc_benchmark.run({})
            print(gcc_result)
            llvm_result = self.llvm_benchmark.run({})
            print(llvm_result)
        except Exception as e:
            self.fail(f"run() raised an exception unexpectedly: {e}")

    def test_02_run_with_random(self):
        try:
            gcc_result = self.gcc_benchmark.run_with_random()
            print(gcc_result)
            llvm_result = self.llvm_benchmark.run_with_random()
            print(llvm_result)
        except Exception as e:
            self.fail(f"run() raised an exception unexpectedly: {e}")

    def test_03_run_with_all_on(self):
        try:
            self.gcc_benchmark.config_space.set_all_to_on()
            gcc_result = self.gcc_benchmark.run({})
            print(gcc_result)

            self.llvm_benchmark.config_space.set_all_to_on()
            llvm_result = self.llvm_benchmark.run({})
            print(llvm_result)
        except Exception as e:
            self.fail(f"run() raised an exception unexpectedly: {e}")

    def tearDown(self):
        print("=" * 50)
        print(f"Finished Test：{self._testMethodName}")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    unittest.main()
