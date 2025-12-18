# Dynamic IP on FreeDNS.si

A simple Python script used to automatically update the IP address on [FreeDNS.si](https://www.freedns.si/).

The main idea of the script is to automatically update the IP address of your server which doesn't have a static IP address.

## Setup

### Create the Python environment
1. Create a virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2. Install the dependencies
    ```bash
    pip install -r requirements.txt
    ```

### Create the `.env` file
1. Copy the `.env.example` file to `.env`
    ```bash
    cp .env.example .env
    ```
2. Fill in your FreeDNS.si username and password
    ```bash
    nano .env
    ```

## Usage

### Create a Record list for your domain
1. Run the `create_record_list.py` script
    ```bash
    python create_record_list.py
    ```
2. Enter `y` to create the record list
3. The script will create a `record-list.csv` file in the `data/` directory

### Update the Record list
1. Run the `update_record_list.py` script to update the record list with the current public IP address
    ```bash
    python update_record_list.py
    ```

### Add a cronjob to update the record list periodically
1. Add the following cronjob to your system
    ```bash
    13 */2 * * * /path/to/venv/bin/python /path/to/dynamic-ip-freedns-si/scripts/update_record_list.py
    ```
2. This cronjob will run the `update_record_list.py` script every 2 hours.
    - Make sure to replace the path to the virtual environment and the script with the actual path.