import os
import re
from pathlib import Path

def get_next_filename(directory=".opencode/plans/arch", prefix="plan", extension=".md"):
    # Target the directory relative to where the agent is running the command (the project root)
    dir_path = Path(directory)
    
    # Safely create the directory if it doesn't exist yet
    dir_path.mkdir(parents=True, exist_ok=True)

    max_num = 0
    # Regex to match exactly "plan_<number>.md"
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
    # Print the result so the LLM can read it from standard output
    print(get_next_filename())