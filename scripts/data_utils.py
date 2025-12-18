import os


def get_data_path(filename: str) -> str:
    """Get path to data file relative to script location."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    return os.path.join(project_root, "data", filename)


def create_data_folder() -> bool:
    if not os.path.exists(get_data_path("")):
        os.makedirs(get_data_path(""), exist_ok=True)
        return True
    return False
