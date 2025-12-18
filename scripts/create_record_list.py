from public_ip import PublicIP
from freedns import FreeDNS, FreeDNSRecordListService
from data_utils import create_data_folder


def main():
    target_ip = PublicIP.get_current_ip()

    if not create_data_folder():
        response = input(f"Create record list for {target_ip} This will delete the current record list? (y/n)? ")
        if response != "y":
            return

    freedns = FreeDNS()

    freedns.login()
    domain_list = freedns.get_domain_list()

    for domain in domain_list:
        record_list = freedns.get_record_list(domain)
        FreeDNSRecordListService.save_record_list(record_list)


if __name__ == "__main__":
    main()
