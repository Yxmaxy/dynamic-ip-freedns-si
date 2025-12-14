from check_ip import CheckIP
from freedns import FreeDNS, RecordListInterface


def main():
    target_ip = CheckIP.get_current_ip()

    response = input(f"Create record list for {target_ip} This will delete the current record list? (y/n)? ")
    if response != "y":
        return

    freedns = FreeDNS()

    freedns.login()
    domain_list = freedns.get_domain_list()

    for domain in domain_list:
        record_list = freedns.get_record_list(domain)
        RecordListInterface.save_record_list(record_list)


if __name__ == "__main__":
    main()
