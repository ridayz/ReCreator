#!/usr/bin/env python3
"""recompiler.py - Compile rebuilt source into a runnable artifact
Usage: py recompiler.py --src rebuilt/ --out dist/ [--toolchain auto]
"""
import argparse, os, subprocess, sys

def detect_toolchain(src):
    if os.path.exists(os.path.join(src, "CMakeLists.txt")): return "cmake"
    if any(os.path.exists(os.path.join(src, f)) for f in ("main.py", "app.py", "bot.py")):
        return "pyinstaller"
    if os.path.exists(os.path.join(src, "package.json")): return "npm"
    if any(f.endswith((".sln", ".vcxproj")) for f in os.listdir(src)): return "msvc"
    return None

def run(cmd):
    print(f"[RUN] {cmd}")
    try:
        r = subprocess.run(cmd, shell=True)
        return r.returncode == 0
    except Exception as e:
        print(f"  error: {e}")
        return False

def build(src, out, toolchain):
    os.makedirs(out, exist_ok=True)
    if toolchain == "cmake":
        b = os.path.join(out, "build"); os.makedirs(b, exist_ok=True)
        return run(f'cmake -S "{src}" -B "{b}"') and run(f'cmake --build "{b}" --config Release')
    if toolchain == "pyinstaller":
        entry = next((f for f in ("main.py", "app.py", "run.py", "bot.py")
                      if os.path.exists(os.path.join(src, f))), None)
        if not entry:
            print("No Python entrypoint found (main.py/app.py/run.py/bot.py)")
            return False
        return run(f'pyinstaller --onefile --distpath "{out}" --workpath "{out}/_build" '
                   f'--specpath "{out}" "{os.path.join(src, entry)}"')
    if toolchain == "npm":
        # Windows: signing step of electron-builder needs symlink privilege;
        # disable signing so the build succeeds without admin.
        env = 'set CSC_IDENTITY_AUTO_DISCOVERY=false&& '
        return (run(f'npm --prefix "{src}" install')
                and run(env + f'npm --prefix "{src}" run build'))
    if toolchain == "msvc":
        proj = next((f for f in os.listdir(src) if f.endswith((".sln", ".vcxproj"))), None)
        if not proj:
            print("No .sln/.vcxproj found"); return False
        return run(f'msbuild "{os.path.join(src, proj)}" /p:Configuration=Release /p:OutDir="{out}"')
    print("No toolchain detected. Pass --toolchain explicitly.")
    return False

def main():
    p = argparse.ArgumentParser(description="Compile rebuilt source into a runnable artifact")
    p.add_argument("--src", required=True, help="Rebuilt source directory")
    p.add_argument("--out", required=True, help="Output directory for binary/installer")
    p.add_argument("--toolchain", default="auto",
                   choices=["auto", "cmake", "msvc", "pyinstaller", "npm"])
    a = p.parse_args()

    tc = a.toolchain
    if tc == "auto":
        tc = detect_toolchain(a.src)
        print(f"Detected toolchain: {tc}")
    sys.exit(0 if build(a.src, a.out, tc) else 1)

if __name__ == "__main__":
    main()
