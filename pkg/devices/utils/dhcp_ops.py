'''
File: dhcp_ops.py
Author: Sandhya and Kamal
Description: This file contains the functions to perform operations on the DHCP server.
'''

import re
import csv
import os
import json
from paramiko import SSHClient, AutoAddPolicy, SFTPClient
from datetime import datetime
import time
from utils.scn_log import logger


def dhcp_ops_get_service_name(client):
    try:
        # Check if /etc/os-release file exists (Works for CentOS, Ubuntu, Debian, etc.)
        stdin, stdout, stderr = client.exec_command("cat /etc/os-release 2>/dev/null")
        os_info = stdout.read().decode().strip()

        os_name = "Unknown"
        if os_info:
            for line in os_info.split("\n"):
                if line.startswith("PRETTY_NAME="):  # Get the full OS name
                    os_name = line.split("=")[1].strip().strip('"')
                    break
        else:
            # If /etc/os-release is missing, try another method
            stdin, stdout, stderr = client.exec_command("lsb_release -d 2>/dev/null | cut -f2")
            os_name = stdout.read().decode().strip()

            if not os_name:  # Last fallback for older systems
                stdin, stdout, stderr = client.exec_command("cat /etc/redhat-release 2>/dev/null")
                os_name = stdout.read().decode().strip()

        logger.debug(f"Remote OS: {os_name}")
        if os_name == "Ubuntu":
            service_name = "isc-dhcp-server"
        elif os_name == "CentOS Stream 9":
            service_name = "dhcpd"

    except Exception as e:
        logger.error(f"Error getting OS name: {e}")
        service_name = "isc-dhcp-server"

    return service_name


# Function to get the DHCP lease file name based on the OS
def dhcp_ops_get_lease_file_name(client):
    try:
        # Check if /etc/os-release file exists (Works for CentOS, Ubuntu, Debian, etc.)
        stdin, stdout, stderr = client.exec_command("cat /etc/os-release 2>/dev/null")
        os_info = stdout.read().decode().strip()

        os_name = "Unknown"
        if os_info:
            for line in os_info.split("\n"):
                if line.startswith("PRETTY_NAME="):  # Get the full OS name
                    os_name = line.split("=")[1].strip().strip('"')
                    break
        else:
            # If /etc/os-release is missing, try another method
            stdin, stdout, stderr = client.exec_command("lsb_release -d 2>/dev/null | cut -f2")
            os_name = stdout.read().decode().strip()

            if not os_name:  # Last fallback for older systems
                stdin, stdout, stderr = client.exec_command("cat /etc/redhat-release 2>/dev/null")
                os_name = stdout.read().decode().strip()

        logger.debug(f"Remote OS: {os_name}")
        if os_name == "Ubuntu":
            lease_file_name = "/var/lib/dhcp/dhcpd.leases"
        elif os_name == "CentOS Stream 9":
            lease_file_name = "/var/lib/dhcpd/dhcpd.leases"

    except Exception as e:
        logger.error(f"Error getting OS name: {e}")
        lease_file_name = "/var/lib/dhcp/dhcpd.leases"

    return lease_file_name