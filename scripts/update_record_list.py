from public_ip import PublicIP
from freedns import FreeDNS, FreeDNSRecordListService


def main():
    previous_ip = PublicIP.get_previous_ip()
    current_ip = PublicIP.get_current_ip()

    if previous_ip != current_ip:
        freedns = FreeDNS()
        record_list = FreeDNSRecordListService.load_record_list()

        freedns.login()
        freedns.update_domain_records(current_ip, record_list)
        PublicIP.save_current_ip(current_ip)

        # NOTE: here you can add calls to other services like SMS, email notifications etc.


if __name__ == "__main__":
    main()
