"""Cross-platform build script for BilligerPriceChecker."""

import platform
import subprocess
import sys


def _check_tkinter():
    """Verify tkinter is importable. Exit with clear instructions if not."""
    try:
        import tkinter  # noqa: F401
    except ImportError:
        v = f"{sys.version_info.major}.{sys.version_info.minor}"
        print("ERROR: tkinter is not installed.\n")
        if platform.system() == "Darwin":
            print("On macOS with Homebrew, run:\n")
            print(f"    brew install python-tk@{v}")
            print()
            print("If that formula is unavailable, install tcl-tk and reinstall Python:\n")
            print(f"    brew install tcl-tk && brew reinstall python@{v}")
        else:
            print("Install the tkinter package for your system's Python.")
        print()
        sys.exit(1)


def _check_pyinstaller():
    """Verify PyInstaller is importable. Install it if missing."""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found — installing ...\n")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print()


def main():
    system = platform.system()

    if system == "Darwin":
        spec = "BilligerPriceChecker_mac.spec"
        label = "macOS .app bundle"
        output = "dist/BilligerPriceChecker.app"
    elif system == "Windows":
        spec = "BilligerPriceChecker.spec"
        label = "Windows .exe"
        output = "dist/BilligerPriceChecker.exe"
    else:
        print(f"Unsupported platform: {system}")
        sys.exit(1)

    print(f"Building {label} ...\n")

    _check_tkinter()
    _check_pyinstaller()

    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", spec]
    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"\nDone — {output}")
    else:
        print("\nBuild failed.", file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
