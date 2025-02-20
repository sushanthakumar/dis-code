'''
File: discovery_main.py
Author: Kamal and Sandhya
Description: This file contains the main functions to get IP and 
'''

import re
import csv
import os
import json
from paramiko import SSHClient, AutoAddPolicy, SFTPClient
from datetime import datetime
import time
from utils.scn_log import logger


# Constants
CWD = os.path.dirname(os.path.abspath(__file__))

CWD = os.path.dirname(os.path.abspath(__file__))
DHCP_HOST_DETAILS = "/tmp/dhcp_host.conf"


DHCP_LEASE_FILE = CWD+"/data/dhcpd.leases"
REPETITIONS = 10


# Function to fetch the DHCP lease file from the DHCP server
def fetch_dhcp_leases_via_ssh(dhcp_server_ip, username, password, remote_path, local_path, port):
    """Fetches the DHCP lease file from a remote DHCP server using SSH."""
    logger.debug("Fetching DHCP lease file from the DHCP server.")
    try:
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        logger.debug(f"Connecting to DHCP server at {dhcp_server_ip}:{port}...")
        client.connect(dhcp_server_ip, port=port, username=username, password=password, timeout=30)

        # Remove local_path
        if os.path.exists(local_path):
            os.remove(local_path)
        # Use SFTP to download the lease file
        sftp = client.open_sftp()
        logger.debug(f"Fetching lease file from {remote_path}...")
        sftp.get(remote_path, local_path) 
        sftp.close()
        client.close()

        logger.debug(f"Successfully fetched DHCP lease file to {local_path}")
        return local_path
    except Exception as e:
        logger.error(f"Error fetching DHCP lease file: {e}")
        return None

# Function to parse the DHCP lease file
def parse_dhcp_leases(lease_file="dhcpd.leases"):
    devices = []
    try:
        with open(lease_file, "r") as file:
            content = file.read()
            # Ignore commented lines
            content = '\n'.join([line for line in content.splitlines() if not line.strip().startswith("#")])
            leases = re.findall(r'lease\s(?P<ip>\d+\.\d+\.\d+\.\d+)\s\{[\s\S]*?starts\s\d\s(?P<start_time>[\d\/\:\s]+);[\s\S]*?ends\s\d\s(?P<end_time>[\d\/\:\s]+);[\s\S]*?hardware\s\w+\s(?P<mac>[a-fA-F0-9:]+);(?:[\s\S]*?set vendor-class-identifier\s*=\s\"(?P<inventory_type>.*?)\";)?', content, re.DOTALL)

            #list(map(print, leases))
            for lease in leases:
                print(lease)
                if len(lease) == 5:
                    ip, start_time, stop_time, mac, inventory_type = lease
                else:
                    continue
                devices.append({"ip": ip.strip(), "mac": mac.strip(), "Inventory Type": inventory_type.strip(),
                "start_time": start_time.strip(), "stop_time": stop_time.strip()})
    except Exception as e:
        print(f"Error parsing DHCP lease file: {e}")
    return devices


# Function to remove duplicate devices
def remove_duplicates(devices):
    seen = set()
    unique_devices = []
    for device in devices:
        identifier = (device['mac'])
        if identifier not in seen:
            seen.add(identifier)
            unique_devices.append(device)
        else:
            # remove the old entry
            unique_devices = [d for d in unique_devices if d['mac'] != device['mac']]
            unique_devices.append(device)

    return unique_devices

# Function to enrich the device information with vendor details
def enrich_vendor_info(devices):
    for device in devices:
        device["vendor"] = "Unknown"  # Placeholder for vendor information
    return devices

# Function to check if a device is a Cisco device based on its MAC address
def is_cisco_device(mac):
    cisco_ouis = ["00:50:56", "00:40:96", "00:14:5E", "00:24:14"]  # Add other Cisco OUIs as needed
    oui = mac.upper()[:8]
    return oui in cisco_ouis

# Function to save device information to a CSV file
def save_to_csv(filename, devices):
    """Save device information to a CSV file."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["ip", "mac", "hostname", "vendor"])
        writer.writeheader()
        writer.writerows(devices)
    print(f"Device details saved to {filename}")


# Function to get the device information
def scan_devices():
    # If file DEVICE_SCAN_CONFIG_PATH does not exist, create it
    if os.path.exists(DHCP_HOST_DETAILS):
        DHCPServerDetails = json.load(open(DHCP_HOST_DETAILS))
    else:
        logger.error(f"File not found {DHCP_HOST_DETAILS}")
        return []

    # List of all device information
    device_information_all = []

    # Step 1: Fetch the DHCP lease file from the DHCP server
    lease_file = fetch_dhcp_leases_via_ssh(DHCPServerDetails["ip"], 
                                           DHCPServerDetails["username"], 
                                           DHCPServerDetails["password"],
                                           remote_path=DHCPServerDetails["lease_file"],
                                           local_path=DHCP_LEASE_FILE,
                                           port = DHCPServerDetails["port"])
    if not lease_file:
        logger.error(f"lease_file file is None")
        return []
    
    # Step 2: Parse the DHCP lease file to get devices
    devices = parse_dhcp_leases(lease_file)

    # Step 3: Remove duplicate devices
    devices = remove_duplicates(devices)

    # Step 4: Enrich with vendor information (placeholder for now)
    devices = enrich_vendor_info(devices)
    return devices


if __name__ == "__main__":
    devices = scan_devices()
    print("Device discovery completed.")
