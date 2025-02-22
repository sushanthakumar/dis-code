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

# Enum for Oprating Systems
class OS:
    UBUNTU = "ubuntu"
    CENTOS = "centos"
    DEBIAN = "debian"
    FEDORA = "fedora"
    RHEL = "redhat"
    UNKNOWN = "unknown"

def get_os_name(client):
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
        if re.search(r'ubuntu', os_name, re.IGNORECASE):
            return OS.UBUNTU
        elif re.search(r'centos', os_name, re.IGNORECASE):
            return OS.CENTOS
        elif re.search(r'debian', os_name, re.IGNORECASE):
            return OS.DEBIAN
        elif re.search(r'fedora', os_name, re.IGNORECASE):
            return OS.FEDORA
        elif re.search(r'redhat', os_name, re.IGNORECASE):
            return OS.RHEL
        else:
            return OS.UBUNTU # Default to Ubuntu

    except Exception as e:
        logger.error(f"Error getting OS name: {e}")

def dhcp_ops_get_service_name(client):
    os_name = get_os_name(client)
    if os_name == OS.UBUNTU:
        service_name = "isc-dhcp-server"
    elif os_name == OS.CENTOS:
        service_name = "dhcpd"
    else:
        service_name = "isc-dhcp-server"    # Default to Ubuntu
    return service_name


# Function to get the DHCP lease file name based on the OS
def dhcp_ops_get_lease_file_name(client):
    os_name = get_os_name(client)
    if os_name == OS.UBUNTU:
        lease_file = "/var/lib/dhcp/dhcpd.leases"
    elif os_name == OS.CENTOS:
        lease_file = "/var/lib/dhcpd/dhcpd.leases"
    else:
        lease_file = "/var/lib/dhcp/dhcpd.leases"    # Default to Ubuntu
    return lease_file