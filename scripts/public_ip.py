import os
import logging
import ipaddress
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
            try:
                response = requests.get(service, timeout=30)
            except requests.RequestException:
                logger.warning("Could not reach %s", service, exc_info=True)
                continue
            if response.status_code != 200:
                continue

            current_ip = response.text.strip()
            try:
                ipaddress.ip_address(current_ip)
            except ValueError:
                logger.warning("%s returned a non-IP response", service)
                continue

            return current_ip

        raise Exception("No external service returned a valid IP")

    @staticmethod
    def get_previous_ip() -> str:
        if not os.path.exists(get_data_path("current-ip.txt")):
            return ""
        with open(get_data_path("current-ip.txt"), "r") as f:
            return f.read().strip()

    @staticmethod
    def save_current_ip(ip: str) -> None:
        with open(get_data_path("current-ip.txt"), "w") as f:
            f.write(ip)
