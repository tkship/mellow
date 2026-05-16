"""Setup Flutter SDK."""
import subprocess, sys, os

target = r"D:\flutter"
g = r"C:\Program Files\Git\cmd\git.exe"

if not os.path.exists(g):
    g = "git"

if os.path.exists(target):
    print("Flutter exists, pulling...")
    subprocess.run([g, "-C", target, "pull", "origin", "stable"], check=True)
else:
    print("Cloning Flutter SDK (300MB+)...")
    subprocess.run([
        g, "clone", "-b", "stable",
        "https://github.com/flutter/flutter.git",
        target, "--depth", "1"
    ], check=True)
print("Flutter SDK ready!")
