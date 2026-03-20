import platform
import re

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

if __name__ == "__main__":
    check_compatibility()

# Alias for the compatibility check function
syscheck = check_compatibility