import os
import subprocess
import json
import sys

CONFIG_FILE = "multi_tool_config.json"
SUPPORTED_EXTENSIONS = [".py", ".bat", ".sh", ".exe"]
SCRIPT_PATHS_HEADER_START = "# === SCRIPT_PATHS_START ==="
# ["D:\\shogle\\progaming-lang\\Projects"]
SCRIPT_PATHS_HEADER_END = "# === SCRIPT_PATHS_END ==="

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print()
    print("                     \033[38;2;0;255;255m███╗   ███╗██╗   ██╗██╗  ████████╗██╗    ████████╗ ██████╗  ██████╗ ██╗\033[0m")
    print("                     \033[38;2;0;204;255m████╗ ████║██║   ██║██║  ╚══██╔══╝██║    ╚══██╔══╝██╔═══██╗██╔═══██╗██║\033[0m")
    print("                     \033[38;2;0;153;255m██╔████╔██║██║   ██║██║     ██║   ██║       ██║   ██║   ██║██║   ██║██║\033[0m")
    print("                     \033[38;2;0;102;255m██║╚██╔╝██║██║   ██║██║     ██║   ██║       ██║   ██║   ██║██║   ██║██║\033[0m")
    print("                     \033[38;2;0;51;255m██║ ╚═╝ ██║╚██████╔╝███████╗██║   ██║       ██║   ╚██████╔╝╚██████╔╝███████╗\033[0m")
    print("                     \033[38;2;0;0;255m╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝\033[0m")
    print()

def load_embedded_paths():
    with open(__file__, "r", encoding="utf-8") as f:
        lines = f.readlines()
    start_idx = end_idx = None
    for i, line in enumerate(lines):
        if SCRIPT_PATHS_HEADER_START in line:
            start_idx = i
        elif SCRIPT_PATHS_HEADER_END in line:
            end_idx = i
            break
    if start_idx is not None and end_idx is not None:
        try:
            return json.loads(lines[start_idx + 1].lstrip("# ").strip())
        except:
            return []
    return None

def embed_paths_in_script(paths):
    with open(__file__, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx = end_idx = None
    for i, line in enumerate(lines):
        if SCRIPT_PATHS_HEADER_START in line:
            start_idx = i
        elif SCRIPT_PATHS_HEADER_END in line:
            end_idx = i
            break

    if start_idx is not None and end_idx is not None:
        lines[start_idx + 1] = f"# {json.dumps(paths)}\n"
    else:
        lines.insert(0, SCRIPT_PATHS_HEADER_END + "\n")
        lines.insert(0, f"# {json.dumps(paths)}\n")
        lines.insert(0, SCRIPT_PATHS_HEADER_START + "\n")

    with open(__file__, "w", encoding="utf-8") as f:
        f.writelines(lines)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def first_time_setup():
    print("\033[38;2;0;255;255mFirst time setup: please add at least one script directory.\033[0m")
    paths = []
    while True:
        path = input("Enter a script directory path (or leave blank to finish): ").strip()
        if not path:
            break
        if os.path.isdir(path):
            paths.append(path)
        else:
            print("\033[38;2;255;0;0mInvalid directory.\033[0m")

    if not paths:
        print("No paths provided. Exiting.")
        sys.exit(0)

    print("\nWhere do you want to save these paths?")
    print("1. Save to external JSON file (recommended)")
    print("2. Embed inside this Python file (⚠️ advanced)")
    choice = input("Your choice (1/2): ").strip()

    if choice == "2":
        print("\n\033[38;2;255;100;0m⚠️  WARNING: You chose to embed paths inside this script.\033[0m")
        print("- This script file must remain writable.")
        print("- Do NOT rename or move the script after saving.")
        print("- Editing this file manually may break the tool.\n")
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm == "y":
            embed_paths_in_script(paths)
            return {"script_dirs": paths, "embedded": True}
        else:
            print("Cancelled. Saving to external JSON instead.")
            save_config({"script_dirs": paths})
            return {"script_dirs": paths, "embedded": False}
    else:
        save_config({"script_dirs": paths})
        return {"script_dirs": paths, "embedded": False}

def collect_all_scripts(directories):
    all_scripts = []
    for dir_path in directories:
        try:
            for f in os.listdir(dir_path):
                if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS:
                    full_path = os.path.join(dir_path, f)
                    all_scripts.append((f, full_path, dir_path))
        except Exception as e:
            print(f"\033[38;2;255;0;0mError reading {dir_path}: {e}\033[0m")
    return all_scripts

def group_scripts_by_dir(scripts):
    grouped = {}
    for name, full_path, dir_path in scripts:
        grouped.setdefault(dir_path, []).append((name, full_path))
    return grouped

def display_menu(grouped_scripts):
    print()
    index = 1
    script_map = {}

    for dir_index, (dir_path, scripts) in enumerate(grouped_scripts.items()):
        print(f"\n\033[38;2;0;255;255mDirectory:\033[0m {dir_path}")
        for i, (name, full_path) in enumerate(scripts):
            base_name = os.path.splitext(name)[0]
            if i == 0:
                print(f"        ╔═({index}) {base_name}")
            elif i == len(scripts) - 1:
                print(f"        ╚╦═══({index}) {base_name}")
                print("         ║")
            else:
                print(f"        ╠═══({index}) {base_name}")
                print("        ║")
            script_map[str(index)] = full_path
            index += 1
    return script_map

def run_script(script_path):
    ext = os.path.splitext(script_path)[1].lower()
    args = input("\033[38;2;180;180;180mEnter arguments (or leave blank):\033[0m ").strip()
    try:
        if ext == ".py":
            subprocess.run(["python", script_path] + args.split())
        else:
            subprocess.run(f'"{script_path}" {args}', shell=True)
    except Exception as e:
        print(f"\033[38;2;255;0;0mError running script: {e}\033[0m")
    input("\n\033[38;2;180;180;180mPress Enter to return to menu...\033[0m")

def main():
    embedded_paths = load_embedded_paths()
    config = load_config()

    if not embedded_paths and not config:
        config = first_time_setup()

    script_dirs = embedded_paths if embedded_paths else config["script_dirs"]
    use_embedded = bool(embedded_paths)

    while True:
        banner()
        all_scripts = collect_all_scripts(script_dirs)
        grouped = group_scripts_by_dir(all_scripts)

        if not all_scripts:
            print("\033[38;2;255;0;0mNo scripts found. Please check your directories.\033[0m")
            input("Press Enter to exit...")
            break

        script_map = display_menu(grouped)
        choice = input("        ╚══════> ").strip()
        if choice in script_map:
            run_script(script_map[choice])
        else:
            print("\033[38;2;255;0;0mInvalid selection.\033[0m")
            input("Press Enter to continue...")

# === SCRIPT_PATHS_START ===
# []
# === SCRIPT_PATHS_END ===

if __name__ == "__main__":
    main()
