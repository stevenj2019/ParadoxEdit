import re
from pathlib import Path

INPUT = Path("input.md")
OUTPUT = Path("output")

def parse_commands(text):
    sections = re.split(
        r"(?=^## )",
        text,
        flags=re.MULTILINE
    )

    for section in sections:
        if not section.strip():
            continue

        yield parse_command(section)


def parse_command(section):
    name = re.search(
        r"^##\s+(\S+)",
        section,
        re.MULTILINE
    ).group(1)

    scopes = re.search(
        r"\*\s+Supported Scopes:\s*(.+)",
        section
    )

    targets = re.search(
        r"\*\s+Supported Targets:\s*(.+)",
        section
    )

    description = re.search(
        r"```(.*?)```",
        section,
        re.DOTALL
    )

    return {
        "name": name,
        "scopes": extract_list(scopes),
        "targets": extract_list(targets),
        "description": clean_description(
            description.group(1)
            if description else ""
        )
    }


def extract_list(match):
    if not match:
        return []

    value = match.group(1).strip()

    if value.lower() == "none":
        return []

    return [
        x.strip()
        for x in value.split(",")
    ]


def clean_description(text):
    if "Example:" in text:
        return text.split(
            "Example:",
            1
        )[0].strip().replace("\n", "\\n")
    elif "ex:" in text:
        return text.split(
            "ex:",
            1
        )[0].strip().replace("\n", "\\n")


def generate_py(scope, data):
    path = OUTPUT / f"{scope.lower().capitalize()}.py"
    for command in data:
        class_name = "".join(
            x.capitalize()
            for x in command["name"].split("_")
        )
        desc = command['description'] if command['description'] is not None else ""
        with open(path, "a") as PY_FILE:
            PY_FILE.write(f"""
class {class_name}Effect(Effect):
    def __init__(self):
        super().__init__(\"{command['name']}\", \"{desc}\", False)
    
    def to_node():
        return NotImplementedError
    """
            )

if __name__ == "__main__":
    OUTPUT.mkdir(exist_ok=True)

    data = INPUT.read_text(
        encoding="utf-8"
    )

    out_data = dict()
    for command in parse_commands(data):
        for scope in command["scopes"]:
            if scope not in out_data.keys():
                out_data[scope] = []
            out_data[scope].append(command)
    
    for scope in out_data.keys():
        generate_py(scope, out_data[scope])
        # print(scope)
        print(out_data[scope])
    # generate(command)