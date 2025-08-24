# 🗂️ CodeCollector

CodeCollector is a handy cross-platform script to **aggregate your project’s source code files into a single text file** and optionally **copy it to your clipboard**.  

It’s useful for:
- Sharing code snippets with AI tools
- Creating backups of project code
- Reviewing all source files in one place

## ✨ Features
- **Cross-platform:** works on macOS, Linux, and Windows.
- **Smart filtering:**
  - Collects common code, config, and data file types.
  - Skips heavy folders like `node_modules/`, `.git/`, `venv/`, `dist/`, etc.
  - Includes special files like `Dockerfile`, `Makefile`, `.gitignore`.
- **Modes:**
  - Default → Only allowed extensions and relevant files.
  - `--all` → Collects *everything* except the script itself and the output file.
- **Custom output name:** `--output mydump.txt`
- **Clipboard copy:** automatically copies the result to your clipboard at the end.
  - macOS → uses `pbcopy`
  - Linux → uses `xclip`/`xsel` (install if missing)
  - Windows → uses `clip`
- **Toggles:**  
  - `--no-clipboard` → Skip copying to clipboard  
  - `--no-color` → Plain output without ANSI colors

## 📦 Installation

Clone or download this repo somewhere on your system.  
Example (download directly with `curl`):

```bash
curl -o ~/bin/codecollector.py https://raw.githubusercontent.com/yourusername/yourrepo/main/codecollector.py
chmod +x ~/bin/codecollector.py
````

> Make sure `~/bin` (or the folder you choose) is in your `$PATH`.

## 🚀 Usage

Run directly:

```bash
python3 codecollector.py
```

Collect all files (ignore filtering):

```bash
python3 codecollector.py --all
```

Choose a different output filename:

```bash
python3 codecollector.py -o project_dump.txt
```

Skip clipboard:

```bash
python3 codecollector.py --no-clipboard
```

## ⚡ Bash Alias

If you want to call it with a short command like `codecollector`, add this to your `~/.bashrc` (or `~/.zshrc` if you use zsh):

```bash
alias codecollector="python3 ~/bin/codecollector.py"
```

Reload your shell:

```bash
source ~/.bashrc
```

Now you can just run:

```bash
codecollector
```

Or with options:

```bash
codecollector --all -o dump.txt --no-clipboard
```

## 🛠️ Requirements

* **Python 3.7+**
* Clipboard tools:

  * macOS: `pbcopy` (built-in)
  * Linux: `xclip` or `xsel` (`sudo apt install xclip`)
  * Windows: `clip` (built-in)


## 📖 Example

```bash
$ codecollector -o collected.txt
▶️ src/main.py
----------------
[... file content ...]

Done! Aggregated 37 files into collected.txt
Copied collected.txt to clipboard.
```


## 📜 License

MIT
