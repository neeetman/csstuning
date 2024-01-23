import os
import glob

def count_lines_in_folder(folder_path, extensions):
    total_lines = 0
    for extension in extensions:
        for filepath in glob.glob(os.path.join(folder_path, '*' + extension)):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                total_lines += sum(1 for line in file)
    return total_lines

# List of folders to count lines
folders = [
    "cbench-consumer-tiff2bw",
    "cbench-security-rijndael",
    "cbench-telecom-crc32",
    "cbench-bzip2",
    "cbench-office-stringsearch2",
    "cbench-network-patricia",
    "cbench-consumer-tiff2rgba",
    "cbench-automotive-susan-e",
    "cbench-telecom-adpcm-d",
    "cbench-automotive-qsort1",
    "cbench-security-sha",
    "cbench-telecom-adpcm-c",
    "cbench-telecom-gsm",
    "cbench-consumer-jpeg-d",
]

# Define file extensions to count lines in
extensions = ['.h', '.c']

# Initialize a dictionary to hold the line counts for each folder
line_counts = {}

file_path = os.path.dirname(os.path.realpath(__file__))

# Count lines for each folder
for folder in folders:
    folder_path = f'{file_path}/programs/{folder}'  # Assuming the folders are in the /mnt/data directory
    line_counts[folder] = count_lines_in_folder(folder_path, extensions)

print(line_counts)