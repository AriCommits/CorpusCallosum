import os
import re
from pathlib import Path

def get_next_filename(directory=".opencode/audits/arch", prefix="audit", extension=".md"):
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)

    max_num = 0
    pattern = re.compile(rf"^{prefix}_(\d+)\{extension}$")

    for file_path in dir_path.glob(f"{prefix}_*{extension}"):
        match = pattern.match(file_path.name)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num

    next_num = max_num + 1
    return str(dir_path / f"{prefix}_{next_num}{extension}")

if __name__ == "__main__":
    print(get_next_filename())