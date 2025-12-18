import os


def get_data_path(filename: str) -> str:
    """Get path to data file relative to script location."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    return os.path.join(project_root, "data", filename)
