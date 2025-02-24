



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

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "./login_details/credentials.json")

# Define the parameters to be fetched from the devices using SSH, and the corresponding commands and regex patterns
param_against_file ={
    "Firmware Version": {"file": "Firmware_Version", "regex":r"(.*)"},
    "Software Version": {"file": "uname -a", "regex":r"(.*)#"}
}


class DeviceInfo(DeviceInfoPlugin):
    def __init__(self):
        with open(CREDENTIALS_PATH, 'r') as fd:
            credentials = json.load(fd)
        
        self.user = credentials.get("default").get("username")
        self.password = credentials.get("default").get("password")
        self.port = credentials.get("default").get("port")
        

    def get_metadata_info(self, deviceInfo):

        print("Getting metadata info...from default_plugin.py")

        # Do SSH using IP
        # Get the IP Address from the deviceInfo
        ip = deviceInfo.get("IP Address")
        try:
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, self.port, self.user, self.password, timeout=1)

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
            deviceInfo["Vendor Name"] = "Unclassified"
        except Exception as e:
            print(f"Error in getting device information: {e}")
            return None

        print("Getting metadata info...from mds.py")
        
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