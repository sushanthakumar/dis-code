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
from ping3 import ping
import json
import constants

# PATH for credentials
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "../login_details/credentials.json")

# Define the parameters to be fetched from the devices using SSH, and the corresponding commands and regex patterns
param_against_file ={
    "Firmware Version": { "regex":r".*:(.*)"},
    "Software Version": {"regex":r'NXOS:\s+version\s+([\d\.\(\)A-Za-z\-]+)'},
    "Hardware Model": {"regex":r"Hardware\s*\n\s*(cisco\s+UCS-FI-\d+)"}
}

class DeviceInfo(DeviceInfoPlugin):
    def __init__(self):
        with open(CREDENTIALS_PATH, 'r') as fd:
            credentials = json.load(fd)
        
        self.user = credentials.get("fabricinterconnect").get("username")
        self.password = credentials.get("fabricinterconnect").get("password")
        self.port = credentials.get("fabricinterconnect").get("port")

    def execute_nxos_commands(self,ssh):
        try:
            shell = ssh.invoke_shell()
            import time

            # Connect to NXOS mode
            shell.send("connect nxos\n")
            time.sleep(2)

            # Run 'show version'
            shell.send("show version\n")
            time.sleep(2)

            # Read output
            output = shell.recv(65535).decode("utf-8")
            return output
        except Exception as e:
            print(f"Error executing NXOS commands: {e}")
            return None
    

    def get_metadata_info(self, deviceInfo):
        # Do SSH using IP
        # Get the IP Address from the deviceInfo
        ip = deviceInfo.get("IP Address")
        deviceInfo["Vendor Name"] = "Cisco"
        deviceInfo["AutoGrp"] = "Fabric Interconnect"
        try:
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=self.port, username=self.user, password=self.password, timeout=5)
            # Execute NXOS commands and get output
            output = self.execute_nxos_commands(ssh)

            # Get the device information from the MDS
            for key, value in param_against_file.items():
                # Update the deviceInfo with the fetched information or add None if not found
                if re.search(value["regex"], output,  re.IGNORECASE | re.DOTALL):
                    # Update key value in deviceInfo with the fetched value if key is not there, add it
                    extracted_value = re.search(value["regex"], output, re.IGNORECASE | re.DOTALL).group(1)
                        # Explicitly prefix "NXOS " only for Software Version
                    deviceInfo[key] = f"NXOS {extracted_value}" if key == "Software Version" else extracted_value
                else:
                    deviceInfo[key] = None
            ssh.close() 
        except Exception as e:
            print(f"Error in getting device information: {e}")
            return None
        
    def healthcheck(self, deviceInfo):
        """Perform a ping test to check device health."""
        ip = deviceInfo.get("IP Address")
        
        if not ip:
            logger.error("IP Address missing in deviceInfo.")
            return constants.health_check_Offline

        try:
            logger.debug(f"Pinging device {ip}...")
            response = ping(ip, timeout=2)
            device_status = constants.health_check_Online if response else constants.health_check_Offline
            logger.debug(f"Ping result for {ip}: {device_status}")
            return device_status
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return constants.health_check_Offline
