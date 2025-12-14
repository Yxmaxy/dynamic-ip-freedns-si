import os
import subprocess


class CheckIP:
    @staticmethod
    def _get_data_path(filename: str) -> str:
        """Get path to data file relative to script location."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        return os.path.join(project_root, "data", filename)

    @staticmethod
    def get_current_ip() -> str:
        response = subprocess.run(
            ["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"],
            capture_output=True,
            text=True,
        )
        return response.stdout.strip()

    @staticmethod
    def get_previous_ip() -> str:
        with open(CheckIP._get_data_path("current-ip.txt"), "r") as f:
            return f.read().strip()

    @staticmethod
    def save_current_ip(ip: str) -> None:
        with open(CheckIP._get_data_path("current-ip.txt"), "w") as f:
            f.write(ip)
