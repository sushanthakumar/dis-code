'''
File: scn_disc_db.py
Author: Sandhya, Kamal
Description: This file contains the class ScnDevicesDb which is used to create and write data to the database from MDS.
'''
import os
from abc import ABC, abstractmethod
from scan_device_info_plugin import DeviceInfoPlugin
import paramiko # For SSH
import re
from paramiko import SSHClient
from utils.scn_log import logger

# Define the parameters to be fetched from the devices using SSH, and the corresponding commands and regex patterns
param_against_file ={
    "Inventory Type": {"cmd": "cat /proc/cpuinfo", "regex":r"vendor_id\s+:(.*)"},
    "Vendor Name": {"cmd": "/proc/cpuinfo", "regex":r"vendor_id\s+:(.*)"},    
    "IP Address": {"cmd": "IP_Address", "regex":r"(.*)"},
    "DHCP Lease": {"cmd": "DHCP_Lease", "regex":r"(.*)"},
    "DHCP Options": {"cmd": "DHCP_Options", "regex":r"(.*)"},
    "Firmware Version": {"cmd": "Firmware_Version", "regex":r"(.*)"},
    "Software Version": {"cmd": "show version", "regex":r'version\s+(\d+\.\d+\(\d+\))'},
    "Hardware Model": {"cmd": "cat /proc/cpuinfo", "regex":r"model name\s+:(.*)"},
    "Serial ID": {"cmd": "Serial_ID", "regex":r"(.*)"}
}

ssh_details = {
    "username": "admin",
    "password": "admin",
    "port": 22
}

class DeviceInfo(DeviceInfoPlugin):
    def __init__(self):
        pass

    def get_metadata_info(self, deviceInfo):
        print("Getting metadata info...from CISOC plugin"*10)
        
    def healthcheck(self, deviceInfo):
        """Perform a ping test to check device health."""
        ip = deviceInfo.get("IP Address")
        
        if not ip:
            logger.error("IP Address missing in deviceInfo.")
            return "Offline"

        try:
            logger.debug(f"Pinging device {ip}...")
            response = ping(ip, timeout=2)  # ✅ Pings and gets response time
            device_status = "Online" if response else "Offline"
            logger.debug(f"Ping result for {ip}: {device_status}")
            return device_status
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return "Offline"