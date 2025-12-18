import os
import requests
from dataclasses import dataclass

from dotenv import load_dotenv
from bs4 import BeautifulSoup

from data_utils import get_data_path

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
        """Clean text by removing newlines, carriage returns, tabs, and spaces."""
        return text.strip().replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "")

    def get_domain_list(self) -> list[dict]:
        """Get all domains for the user."""

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

    def get_record_list(self, domain: dict) -> list["FreeDNSRecord"]:
        """
        Get all user-inputted records for a domain

        Cleans columns in the following way:
        - "action" - get only the record id from the href
        - "name" - remove the domain name from the name (eg. "www.example.com" -> "www")
        - other - clean newlines etc.
        """
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
                del record_dict["address"]
                record_list.append(FreeDNSRecord(**record_dict))

        return record_list

    def update_domain_records(self, target_ip: str, record_list: list["FreeDNSRecord"]):
        """Updates each record from the record list based on the target IP."""

        for record in record_list:
            domain_id = record.domainid
            record_id = record.recordid

            self.session.post(
                f"https://www.freedns.si/record/edit/domain-id/{domain_id}/record-id/{record_id}",
                data={
                    **record.to_dict(),
                    "content": target_ip,
                    "save": "Shrani",
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "curl",
                },
            )


@dataclass
class FreeDNSRecord:
    domainid: str
    recordid: str
    type: str
    name: str
    prio: int
    ttl: int

    def to_dict(self) -> dict:
        return {
            "domainid": self.domainid,
            "recordid": self.recordid,
            "type": self.type or "A",
            "name": self.name or "",
            "prio": self.prio or 0,
            "ttl": self.ttl or 3600,
        }

    def to_csv(self) -> str:
        return f"{self.domainid or ''},{self.recordid or ''},{self.type or ''},{self.name or ''},{self.prio or ''},{self.ttl or ''}"


class FreeDNSRecordListService:
    @staticmethod
    def save_record_list(record_list: list[FreeDNSRecord]) -> None:
        with open(get_data_path("record-list.csv"), "w") as f:
            f.write("domainid,recordid,type,name,prio,ttl\n")
            for record in record_list:
                f.write(record.to_csv() + "\n")

    @staticmethod
    def load_record_list() -> list[FreeDNSRecord]:
        record_list = []
        with open(get_data_path("record-list.csv"), "r") as f:
            header_row = f.readline().strip().split(",")
            for line in f.readlines():
                record_dict = FreeDNSRecord(**{header: None for header in header_row})
                for header, value in zip(header_row, line.strip().split(",")):
                    setattr(record_dict, header, value)
                record_list.append(record_dict)

        return record_list
