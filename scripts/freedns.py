import os
import requests

from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()


class FreeDNS:
    def __init__(self):
        self.username = os.getenv("FREEDNS_USER")
        self.password = os.getenv("FREEDNS_PASS")
        self.session = requests.Session()

    def login(self):
        self.session.post(
            "https://www.freedns.si/user/checklogin",
            data={
                "username": self.username,
                "password": self.password
            },
        )

    def _clean_text(self, text: str) -> str:
        return text.strip().replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "")

    def get_domain_list(self) -> list[dict]:
        response = self.session.get("https://www.freedns.si/domain")
        bs4 = BeautifulSoup(response.text, "html.parser")

        domain_list = []
        for row in bs4.find_all("tr")[1:]:
            columns = row.find_all("td")
            domain_id = self._clean_text(columns[1].a["href"].split("/")[-1])
            domain_name = self._clean_text(columns[0].text)

            domain_list.append({
                "id": domain_id,
                "name": domain_name,
            })

        return domain_list

    def get_record_list(self, domain: dict) -> list[dict]:
        domain_id = domain["id"]
        domain_name = domain["name"]

        response = self.session.get(f"https://www.freedns.si/record/index/domain-id/{domain_id}")
        bs4 = BeautifulSoup(response.text, "html.parser")

        record_list = []
        column_names = ["type", "name", "prio", "address", "ttl", "action"]

        for row in bs4.find_all("tr", attrs=None)[1:]:
            record_dict = {
                "domainid": domain_id,
                "recordid": None,
                "type": None,
                "name": None,
                "prio": None,
                "address": None,
                "ttl": None,
            }
            for column, column_name in zip(row.find_all("td"), column_names):
                if column_name == "action":
                    if column.a:
                        record_dict["recordid"] = self._clean_text(column.a["href"].split("/")[-1])
                    else:
                        record_dict["recordid"] = None
                else:
                    record_dict[column_name] = self._clean_text(column.text)
                if column_name == "name":
                    record_dict[column_name] = self._clean_text(column.text).replace(f".{domain_name}", "").replace(domain_name, "")

            if record_dict["type"] not in ["SOA", "NS"]:
                record_list.append(record_dict)

        return record_list

    def update_domain_records(self, target_ip: str, record_list: list[dict]):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "curl",
        }

        for record in record_list:
            domain_id = record["domainid"]
            record_id = record["recordid"]

            data = {
                "domainid": domain_id,
                "recordid": record_id,
                "type": record["type"] or "A",
                "name": record["name"] or "",
                "content": target_ip,
                "prio": record["prio"] or 0,
                "ttl": record["ttl"] or 3600,
                "save": "Shrani",
            }

            self.session.post(
                f"https://www.freedns.si/record/edit/domain-id/{domain_id}/record-id/{record_id}",
                data=data,
                headers=dict(headers),
            )


class RecordListInterface:
    @staticmethod
    def _get_data_path(filename: str) -> str:
        """Get path to data file relative to script location."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        return os.path.join(project_root, "data", filename)

    @staticmethod
    def save_record_list(record_list: list[dict]) -> None:
        with open(RecordListInterface._get_data_path("record-list.csv"), "w") as f:
            f.write("domainid,recordid,type,name,prio,ttl\n")
            for record in record_list:
                f.write(f"{record['domainid']},{record['recordid']},{record['type']},{record['name']},{record['prio']},{record['ttl']}\n")

    @staticmethod
    def load_record_list() -> list[dict]:
        record_list = []
        with open(RecordListInterface._get_data_path("record-list.csv"), "r") as f:
            header_row = f.readline().strip().split(",")
            for line in f.readlines():
                record_dict = {}
                for header, value in zip(header_row, line.strip().split(",")):
                    record_dict[header] = value
                record_list.append(record_dict)

        return record_list
