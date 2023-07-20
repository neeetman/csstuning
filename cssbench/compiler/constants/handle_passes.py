import json
import os

# Initialize lists
# analysis_passes = []
# transform_passes = []
# other_passes = []

# # Prepare data structure for the categorized passes
# categorized_passes = {
#     "analysis_passes": [],
#     "transform_passes": [],
#     "other_passes": [],
# }

# # Read and process llvm_analysis_passes.txt
# with open("llvm_analysis_passes.txt", 'r') as file:
#     for line in file:
#         line = line.split(':')[0].strip()  # Remove everything after and including ':'
#         analysis_passes.append(line)

# # Read and process llvm_transfom_flags.txt
# with open("llvm_transfom_passes.txt", 'r') as file:
#     for line in file:
#         line = line.split(':')[0].strip()  # Remove everything after and including ':'
#         transform_passes.append(line)

# # Read and process O3.txt
# with open("O3.txt", 'r') as file:
#     for line in file:
#         line = line.split(':')[0].strip()  # Remove everything after and including ':'
#         if line in analysis_passes:
#             categorized_passes["analysis_passes"].append(line)
#         elif line in transform_passes:
#             categorized_passes["transform_passes"].append(line)
#         else:
#             categorized_passes["other_passes"].append(line)

# # Write the data to a JSON file
# with open('categorized_passes.json', 'w') as json_file:
#     json.dump(categorized_passes, json_file, indent=4)

# with open('llvm_passes.json', 'r') as json_file:
#     categorized_passes = json.load(json_file)
#     categorized_passes["analysis_passes"].sort()
#     categorized_passes["transform_passes"].sort()
#     # Delete prefix '-' of the passes
#     categorized_passes["analysis_passes"] = [pass_name.strip('-') for pass_name in categorized_passes["analysis_passes"]]
#     categorized_passes["transform_passes"] = [pass_name.strip('-') for pass_name in categorized_passes["transform_passes"]]

# with open('llvm_passes.json', 'w') as json_file:
#     json.dump(categorized_passes, json_file, indent=4)

# with open("programs.txt", "r") as f:
#     flags = [line.strip() for line in f]

# with open("programs.json", "w") as f:
#    json.dump(flags, f, indent=4)


def merge_flag():
    file_path = "gcc_flags.txt"  # Replace with your file path
    parts = {"O1": [], "O2": [], "O3": [], "perticular": []}
    part_keys = list(parts.keys())

    with open(file_path, "r") as file:
        part_index = 0
        for line in file.readlines():
            stripped_line = line.strip()
            if stripped_line:  # not an empty line
                parts[part_keys[part_index]].append(stripped_line)
            else:  # empty line
                part_index += 1  # move to next part

    with open("gcc_flags.json", "w") as f:
        json.dump(parts, f, indent=4)


def get_benchmarks():
    file_path = "programs.json"  # Replace with your file path
    benchmarks = {"cbench": [], "polybench": []}

    # get subdirectories name in ../benchmark/programs/
    benchs = os.listdir("../benchmark/programs/")
    for bench in benchs:
        if "cbench" in bench:
            benchmarks["cbench"].append(bench)
        elif "polybench" in bench:
            benchmarks["polybench"].append(bench)

    with open(file_path, "w") as f:
        json.dump(benchmarks, f, indent=4)


if __name__ == "__main__":
    get_benchmarks()
