import logging
import requests

from data_utils import get_data_path

logger = logging.getLogger(__name__)


class PublicIP:
    @staticmethod
    def get_current_ip() -> str:
        external_services = [
            "https://api.ipify.org",
            "https://ifconfig.me/ip",
        ]
        for service in external_services:
            response = requests.get(service)
            if response.status_code == 200:
                return response.text.strip()

        raise Exception("No external service returned a valid IP")

    @staticmethod
    def get_previous_ip() -> str:
        with open(get_data_path("current-ip.txt"), "r") as f:
            return f.read().strip()

    @staticmethod
    def save_current_ip(ip: str) -> None:
        with open(get_data_path("current-ip.txt"), "w") as f:
            f.write(ip)
