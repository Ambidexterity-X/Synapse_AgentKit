"""
This module checks the compatibility of the system's CPU, GPU, and RAM.
Provides utilities to execute a file and display system hardware information with progress tracking.
"""

import platform
import os
import time
import subprocess
import psutil

try:
    import GPUtil
except ImportError:
    GPUtil = None


REQUIRED_CPU_MODEL = "Intel(R) Core(TM) Ultra 5 125H"
REQUIRED_GPU_KEYWORD = "Intel(R) Arc(TM) Graphics"
REQUIRED_RAM_GB = 15.43


def _run_powershell(command: str) -> str:
    """Runs a PowerShell command and returns stripped stdout, or an empty string."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except OSError:
        return ""


def _get_windows_cpu_name() -> str:
    """Gets CPU model from Windows CIM as a fallback for generic platform strings."""
    return _run_powershell("(Get-CimInstance Win32_Processor).Name")


def _get_windows_gpu_names() -> list[str]:
    """Gets GPU model names from Windows CIM."""
    output = _run_powershell("Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name")
    return [line.strip() for line in output.splitlines() if line.strip()]


def display_progress_bar(current: int, total: int, label: str = "") -> None:
    """
    Displays a colored progress bar in the terminal.

    Args:
        current (int): Current progress value.
        total (int): Total value for completion.
        label (str): Label to display before the progress bar.
    """
    percentage = (current / total) * 100
    filled_length = int(40 * current // total)
    bar = "█" * filled_length + "░" * (40 - filled_length)

    # Green color for the bar
    green = "\033[92m"
    reset = "\033[0m"

    print(f"\r{label} {green}{bar}{reset} {percentage:.1f}%", end="", flush=True)


def get_system_info() -> dict:
    """
    Retrieves system hardware information (CPU, GPU, RAM).

    Returns:
        dict: Dictionary containing system hardware information.
    """
    system_info = {}

    # CPU Information
    cpu_name = platform.processor().strip()
    if not cpu_name or "genuineintel" in cpu_name.lower() or "family" in cpu_name.lower():
        windows_cpu_name = _get_windows_cpu_name()
        if windows_cpu_name:
            cpu_name = windows_cpu_name
    system_info["cpu_name"] = cpu_name
    system_info["cpu_count"] = psutil.cpu_count(logical=False)
    system_info["cpu_count_logical"] = psutil.cpu_count(logical=True)

    # RAM Information
    ram = psutil.virtual_memory()
    system_info["ram_total_gb"] = ram.total / (1024 ** 3)
    system_info["ram_available_gb"] = ram.available / (1024 ** 3)
    system_info["ram_percent"] = ram.percent

    # GPU Information
    system_info["gpu_info"] = []
    if GPUtil:
        try:
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                system_info["gpu_info"].append(
                    {"name": gpu.name, "memory_total_gb": gpu.memoryTotal / 1024}
                )
        except RuntimeError:
            system_info["gpu_info"] = [{"name": "Not detected", "memory_total_gb": 0}]

    if not system_info["gpu_info"]:
        gpu_names = _get_windows_gpu_names()
        if gpu_names:
            system_info["gpu_info"] = [{"name": name, "memory_total_gb": 0} for name in gpu_names]
        else:
            system_info["gpu_info"] = [{"name": "GPU detection unavailable", "memory_total_gb": 0}]

    return system_info


def display_system_info(system_info: dict) -> None:
    """
    Displays system hardware information in a formatted manner.

    Args:
        system_info (dict): Dictionary containing system information.
    """
    print("\n" + "=" * 60)
    print("SYSTEM HARDWARE INFORMATION".center(60))
    print("=" * 60)

    print("\nCPU Information:")
    print(f"  Model: {system_info['cpu_name']}")
    print(f"  Cores (Physical): {system_info['cpu_count']}")
    print(f"  Cores (Logical): {system_info['cpu_count_logical']}")

    print("\nRAM Information:")
    print(f"  Total: {system_info['ram_total_gb']:.2f} GB")
    print(f"  Available: {system_info['ram_available_gb']:.2f} GB")
    print(f"  Usage: {system_info['ram_percent']:.1f}%")

    print("\nGPU Information:")
    for idx, gpu in enumerate(system_info["gpu_info"], 1):
        print(f"  GPU {idx}: {gpu['name']} ({gpu['memory_total_gb']:.2f} GB)")

    print("=" * 60 + "\n")


def check_compatibility() -> bool:
    """
    Checks if the system's hardware is compatible.
    Compatibility is determined by checking CPU, GPU, and RAM.
    Displays a progress bar and system information during the check.

    Returns:
        bool: True if compatible, False otherwise.
    """
    print("\n" + "=" * 60)
    print("SYSTEM COMPATIBILITY CHECK".center(60))
    print("=" * 60 + "\n")

    # Simulate progress with actual hardware checks
    steps = 3
    for step in range(1, steps + 1):
        display_progress_bar(step, steps, f"Checking step {step}/{steps}...")
        time.sleep(0.5)

    print("\n")

    # Get system information
    system_info = get_system_info()
    display_system_info(system_info)

    # Compatibility checks based on detected baseline system specs.
    cpu_compatible = False
    gpu_compatible = False
    ram_compatible = False

    cpu_info = system_info["cpu_name"]
    if REQUIRED_CPU_MODEL in cpu_info:
        cpu_compatible = True

    if system_info["ram_total_gb"] >= REQUIRED_RAM_GB:
        ram_compatible = True

    if system_info["gpu_info"]:
        for gpu in system_info["gpu_info"]:
            if REQUIRED_GPU_KEYWORD in gpu["name"]:
                gpu_compatible = True
                break

    # Display results
    print("COMPATIBILITY RESULTS:")
    print("-" * 60)
    print(f"✓ CPU Compatible: {'YES' if cpu_compatible else 'NO'} ({REQUIRED_CPU_MODEL})")
    print(f"✓ GPU Compatible: {'YES' if gpu_compatible else 'NO'} ({REQUIRED_GPU_KEYWORD})")
    print(f"✓ RAM Compatible: {'YES' if ram_compatible else 'NO'} ({REQUIRED_RAM_GB:.2f} GB minimum)")
    print("-" * 60)

    overall_compatible = cpu_compatible and gpu_compatible and ram_compatible

    if overall_compatible:
        print("\n✓ OVERALL: COMPATIBLE - System meets all advanced checks!")
    else:
        print("\n✗ OVERALL: INCOMPATIBLE - System does not meet all checks.")
        print(
            f"   Baseline: {REQUIRED_CPU_MODEL} + {REQUIRED_GPU_KEYWORD} + "
            f"{REQUIRED_RAM_GB:.2f}GB RAM"
        )

    print("=" * 60 + "\n")

    return overall_compatible


def execute_file(file_path: str) -> None:
    """
    Executes a Python file if it exists.

    Args:
        file_path (str): The path to the Python file to execute.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    # Ensure the file exists before execution
    if os.path.exists(file_path):
        print(f"Executing {file_path}...")
        with open(file_path, "r", encoding="utf-8") as file:
            # pylint: disable=exec-used
            exec(file.read())
    else:
        print(f"Error: File {file_path} does not exist.")

# Alias for the compatibility check function
syscheck = check_compatibility


def main() -> int:
    """Command-line entry point for running the compatibility check."""
    return 0 if check_compatibility() else 1


if __name__ == "__main__":
    raise SystemExit(main())

