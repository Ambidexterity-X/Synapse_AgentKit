import platform
import re
import os

def check_compatibility():
    cpu_info = platform.processor()

    # Check if the CPU is Intel Core Ultra series
    if "Intel" in cpu_info and "Core Ultra" in cpu_info:
        # Extract generation number from CPU info
        match = re.search(r'(\d+)th Gen', cpu_info)
        if match:
            generation = int(match.group(1))
            if generation >= 14:
                print("Compatible: Intel Core Ultra series, 14th Gen or above.")
                return

    # If not compatible
    print("Incompatible: Requires Intel Core Ultra series, 14th Gen or above.")

def execute_file(file_path):
    # Ensure the file exists before execution
    if os.path.exists(file_path):
        print(f"Executing {file_path}...")
        exec(open(file_path).read())
    else:
        print(f"Error: File {file_path} does not exist.")

if __name__ == "__main__":
    check_compatibility()

# Alias for the compatibility check function
syscheck = check_compatibility