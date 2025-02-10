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
        # Do SSH using IP
        # Get the IP Address from the deviceInfo
        ip = deviceInfo.get("IP Address")
        try:
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=ssh_details["username"], password=ssh_details["password"], port=ssh_details["port"])

            # Get the device information from the MDS
            for key, value in param_against_file.items():
                stdin, stdout, stderr = ssh.exec_command(value["cmd"])
                output = stdout.read().decode('utf-8')
                # Update the deviceInfo with the fetched information or add None if not found
                if re.search(value["regex"], output,  re.IGNORECASE | re.DOTALL):
                    # Update key value in deviceInfo with the fetched value if key is not there, add it
                    if key not in deviceInfo:
                        deviceInfo[key] = re.search(value["regex"], output,  re.IGNORECASE | re.DOTALL).group(1)
                else:
                    deviceInfo[key] = None
            ssh.close()
        except Exception as e:
            print(f"Error in getting device information: {e}")
            return None