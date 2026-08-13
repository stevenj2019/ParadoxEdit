import sys

def get_version(file:list[str]) -> str:
    for line in file:
        if line.startswith("# Version:"):
            return line.split(":")[1].strip()

def get_changes(file:list[str]) -> str:
    array = []
    for line in file:
        if "*" in line:
            array.append(line.strip())
    return "\n".join(array)

def parser_arg(arg:str) -> tuple[str, str]:
    _arg = arg if "=" not in arg else arg.split("=")[0].strip()
    _value = "" if "=" not in arg else arg.split("=")[1].strip()
    return (_arg, _value)

md_path = "changes.md"
py_path = "src/App/AppData.py"
with open(md_path) as FILE:
    file_lines = FILE.readlines()
if sys.argv[1] == "--get_version":
    print(get_version(file_lines))
if sys.argv[1] == "--get_changes":
    print(get_changes(file_lines))
if sys.argv[1] == "--write":
    arg, value = parser_arg(sys.argv[2])
    if arg == "-commit":
        with open(py_path, "w+") as FILE:
            FILE.writelines(["APPNAME = \"ParadoxEdit\"\n",
                            f"VERSION = \"{get_version(file_lines)}\"\n",
                            f"COMMIT = \"{value}\"\n"
            ])
