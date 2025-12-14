from check_ip import CheckIP
from freedns import FreeDNS, RecordListInterface


def main():
    previous_ip = CheckIP.get_previous_ip()
    current_ip = CheckIP.get_current_ip()

    if previous_ip != current_ip:
        freedns = FreeDNS()
        record_list = RecordListInterface.load_record_list()

        freedns.login()
        freedns.update_domain_records(current_ip, record_list)
        CheckIP.save_current_ip(current_ip)


if __name__ == "__main__":
    main()
