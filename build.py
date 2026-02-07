"""Cross-platform build script for BilligerPriceChecker."""

import platform
import subprocess
import sys


def main():
    system = platform.system()

    if system == "Darwin":
        spec = "BilligerPriceChecker_mac.spec"
        print("Building macOS .app bundle ...")
    elif system == "Windows":
        spec = "BilligerPriceChecker.spec"
        print("Building Windows .exe ...")
    else:
        print(f"Unsupported platform: {system}")
        sys.exit(1)

    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", spec]
    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        if system == "Darwin":
            print("\nDone — dist/BilligerPriceChecker.app")
        else:
            print("\nDone — dist/BilligerPriceChecker.exe")
    else:
        print("\nBuild failed.", file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
