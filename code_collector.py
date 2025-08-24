#!/usr/bin/env python3
"""
CodeCollector - Aggregate code files into one text file, then copy result to clipboard.

Usage:
    python3 codecollector.py [--all] [--no-color] [--no-clipboard] [--output FILENAME]

Notes:
- Without --all, only ALLOWED_EXTENSIONS are included and folders in IGNORE_FOLDERS are skipped.
- With --all, every file in every folder is processed (except this script and the output file).
- By default, the collected output is copied to the clipboard at the end (cross-platform).
"""

import os
import sys
import argparse
import platform
import shutil
import subprocess

# --- Configuration ---
ALLOWED_EXTENSIONS = [
    # Core languages
    ".py", ".pyi", ".ipynb",
    ".js", ".mjs", ".cjs", ".jsx",
    ".ts", ".tsx",
    ".java", ".kt", ".kts",
    ".c", ".h", ".cpp", ".cc", ".hpp",
    ".cs", ".fs", ".fsx",
    ".go", ".rs", ".swift",
    ".php", ".rb", ".pl", ".pm",
    ".ex", ".exs", ".erl", ".hrl",
    ".hs", ".lhs", ".scala", ".clj", ".cljs", ".edn",
    ".lua", ".r", ".jl",

    # Web / templating
    ".html", ".htm", ".xml", ".xhtml",
    ".vue", ".svelte", ".astro",
    ".ejs", ".pug", ".jade", ".hbs", ".mustache", ".njk",

    # Styles
    ".css", ".scss", ".sass", ".less", ".styl",

    # Data & queries
    ".json", ".jsonc", ".csv", ".tsv", ".ndjson",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".sql", ".psql", ".prisma", ".graphql", ".gql",

    # Scripts & shells
    ".sh", ".bash", ".zsh", ".fish",
    ".bat", ".cmd", ".ps1",

    # Docs
    ".md", ".mdx", ".rst", ".adoc", ".txt", ".log",
]

SPECIAL_FILENAMES = {
    "Dockerfile", "dockerfile",
    "docker-compose.yml", "docker-compose.yaml",
    "Makefile", "CMakeLists.txt",
    ".gitignore", ".gitkeep", ".gitattributes",
    ".npmrc", ".nvmrc", ".editorconfig",
    ".prettierrc", ".prettierignore",
    ".eslintrc", ".eslintrc.json", ".eslintignore",
    ".stylelintrc", ".stylelintignore",
    "Procfile", "Justfile",
}

IGNORE_FOLDERS = [
    # VCS & IDE
    ".git", ".svn", ".hg", ".idea", ".vscode",

    # Node / web
    "node_modules", "bower_components", "jspm_packages",

    # Python
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".venv", "venv", "env", ".pdm-build", ".pdm-cache",

    # Java / Kotlin / Android
    ".gradle", ".idea", "build", ".build", "out", "bin", "obj",

    # iOS / CocoaPods
    "Pods", "DerivedData",

    # Rust / Go / PHP
    "target", ".cargo", "vendor", "composer", "composer_vendor",

    # JS/TS frameworks & tool caches
    ".next", ".nuxt", ".svelte-kit", ".parcel-cache", ".cache", ".turbo",
    ".expo", ".expo-shared",

    # Packaging & dist
    "dist", "dist-electron", "release", "releases",

    # Coverage / logs / temporary
    "coverage", "coverage-html", "logs", "log", "tmp", "temp",

    # Misc platform clutter
    ".DS_Store", "Thumbs.db",
]

# ANSI escape sequences
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_CYAN = "\033[36m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_MAGENTA = "\033[35m"


def colorize(s: str, enable: bool) -> str:
    return s if enable else ""


def print_header(use_color=True):
    c_bold = colorize(COLOR_BOLD, use_color)
    c_cyan = colorize(COLOR_CYAN, use_color)
    c_reset = colorize(COLOR_RESET, use_color)
    header = f"""
{c_cyan}{c_bold}
  ____          _       ____      _ _           _             
 / ___|___   __| | ___ / ___|___ | | | ___  ___| |_ ___  _ __ 
| |   / _ \\ / _` |/ _ \\ |   / _ \\| | |/ _ \\/ __| __/ _ \\| '__|
| |__| (_) | (_| |  __/ |__| (_) | | |  __/ (__| || (_) | |   
 \\____\\___/ \\__,_|\\___|\\____\\___/|_|_|\\___|\\___|\\__\\___/|_|    
{c_reset}
    """
    print(header)


def aggregate_code(output_filename, all_files=False, use_color=True):
    script_path = os.path.abspath(__file__)
    output_path = os.path.abspath(output_filename)
    file_count = 0

    c_green = colorize(COLOR_GREEN, use_color)
    c_yellow = colorize(COLOR_YELLOW, use_color)
    c_magenta = colorize(COLOR_MAGENTA, use_color)
    c_reset = colorize(COLOR_RESET, use_color)

    try:
        with open(output_filename, "w", encoding="utf-8") as outfile:
            for root, dirs, files in os.walk("."):
                if not all_files:
                    dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
                for file in files:
                    file_path = os.path.join(root, file)
                    abs_file_path = os.path.abspath(file_path)
                    if abs_file_path in (script_path, output_path):
                        continue
                    if not all_files:
                        name = os.path.basename(file)
                        _, ext = os.path.splitext(file)
                        if (ext.lower() not in ALLOWED_EXTENSIONS) and (name not in SPECIAL_FILENAMES):
                            continue
                    rel_path = os.path.relpath(file_path, ".")
                    outfile.write(
                        f"▶️ {rel_path}\n{'-' * (len(rel_path) + 2)}\n")
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read() + "\n\n")
                        file_count += 1
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]\n\n")
                        print(
                            f"{c_yellow}Warning: Could not read {rel_path}: {e}{c_reset}")
        print(
            f"{c_green}Done! Aggregated {file_count} files into {output_filename}{c_reset}")
        return True
    except Exception as e:
        print(f"{c_magenta}Error writing to {output_filename}: {e}{c_reset}")
        return False


def _try_native_clipboard(text: str) -> bool:
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return True
        elif system == "Windows":
            subprocess.run(["clip"], input=text.encode("utf-16le"), check=True)
            return True
        else:
            if shutil.which("xclip"):
                subprocess.run(["xclip", "-selection", "clipboard"],
                               input=text.encode("utf-8"), check=True)
                return True
            if shutil.which("xsel"):
                subprocess.run(["xsel", "--clipboard", "--input"],
                               input=text.encode("utf-8"), check=True)
                return True
    except Exception:
        pass
    return False


def _try_tk_clipboard(text: str) -> bool:
    try:
        import tkinter as tk
        r = tk.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
        r.update()
        r.destroy()
        return True
    except Exception:
        return False


def copy_file_to_clipboard(path: str, use_color=True) -> bool:
    c_green = colorize(COLOR_GREEN, use_color)
    c_yellow = colorize(COLOR_YELLOW, use_color)
    c_magenta = colorize(COLOR_MAGENTA, use_color)
    c_reset = colorize(COLOR_RESET, use_color)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
    except Exception as e:
        print(f"{c_magenta}Could not read {path} to copy: {e}{c_reset}")
        return False

    if _try_native_clipboard(data):
        print(f"{c_green}Copied {path} to clipboard.{c_reset}")
        return True

    if _try_tk_clipboard(data):
        print(f"{c_green}Copied {path} to clipboard via Tkinter.{c_reset}")
        return True

    print(f"{c_yellow}Clipboard not available. Install pbcopy/clip/xclip/xsel or use Tkinter GUI.{c_reset}")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate code files into one text file, then copy result to clipboard.")
    parser.add_argument("--all", action="store_true",
                        help="Aggregate all files.")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI colors.")
    parser.add_argument("--no-clipboard", action="store_true",
                        help="Skip copying the result to clipboard.")
    parser.add_argument("--output", "-o", type=str, default="collected_code.txt",
                        help="Set output filename (default: collected_code.txt)")
    args = parser.parse_args()

    use_color = (not args.no_color) and sys.stdout.isatty()

    print_header(use_color=use_color)
    if args.all:
        print(
            f"{colorize(COLOR_CYAN, use_color)}Running in ALL mode...{colorize(COLOR_RESET, use_color)}")
    else:
        print(f"{colorize(COLOR_CYAN, use_color)}Aggregating selected files...{colorize(COLOR_RESET, use_color)}")

    ok = aggregate_code(output_filename=args.output,
                        all_files=args.all, use_color=use_color)
    if ok and not args.no_clipboard:
        copy_file_to_clipboard(args.output, use_color=use_color)


if __name__ == "__main__":
    main()
