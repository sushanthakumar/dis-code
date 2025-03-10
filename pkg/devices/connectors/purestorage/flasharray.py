'''
File:   
A
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

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "../login_details/credentials.json")

# Define the parameters to be fetched from the devices using SSH, and the corresponding commands and regex patterns
param_against_file ={
    "Software Version": {"cmd": "purearray list", "regex":r'Purity//FA\s+(\d+\.\d+\.\d+)'},
    #"Hardware Model": {"cmd": "cat /proc/cpuinfo", "regex":r"model name\s+:(.*)"}
    }

class DeviceInfo(DeviceInfoPlugin):
    '''This class is used to get the metadata information from the Fabric Interconnect device.'''
    def __init__(self):
        ''''''
        with open(CREDENTIALS_PATH, 'r') as fd:
            credentials = json.load(fd)
        
        self.user = credentials.get("flasharray").get("username")
        self.password = credentials.get("flasharray").get("password")
        self.port = credentials.get("flasharray").get("port")

    def get_metadata_info(self, deviceInfo):
        ''' Get the metadata information from the Nexus device.'''
        # Do SSH using IP
        # Get the IP Address from the deviceInfo
        ip = deviceInfo.get("IP Address")
        deviceInfo["Vendor Name"] = "Pure Storage"
        deviceInfo["Auto_Grp"] = "Storage"
        try:
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=self.port, username=self.user, password=self.password, timeout=5)

            # Get the device information from the MDS
            for key, value in param_against_file.items():
                stdin, stdout, stderr = ssh.exec_command(value["cmd"])
                output = stdout.read().decode('utf-8')
                # Update the deviceInfo with the fetched information or add None if not found
                if re.search(value["regex"], output,  re.IGNORECASE | re.DOTALL):
                    # Update key value in deviceInfo with the fetched value if key is not there, add it
                    extracted_value = re.search(value["regex"], output,  re.IGNORECASE | re.DOTALL).group(1)
                    deviceInfo[key] = f"Purity//FA {extracted_value}" if key == "Software Version" else extracted_value
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
            response = ping(ip, timeout=2)  # Pings and gets response time
            device_status = constants.health_check_Online if response else constants.health_check_Offline
            logger.debug(f"Ping result for {ip}: {device_status}")
            return device_status
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return constants.health_check_Offline