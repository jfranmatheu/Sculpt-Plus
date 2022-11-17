from pathlib import Path

def read_file(file_path: str or Path) -> str:
    if isinstance(file_path, Path):
        file_path = str(file_path)
    with open(file_path, 'r') as f:
        content = f.read()
        return content
