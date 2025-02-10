'''
File: scn_disc_db.py
Author: Sandhya, Kamal
Description: This file contains the class ScnDevicesDb which is used to create and write data to the database.
'''
import os

CWD = os.path.dirname(os.path.abspath(__file__))
import sys
import os
import sqlite3
import uuid
import json
import sys
import re
import importlib
from pathlib import Path
from datetime import datetime
from paramiko import SSHClient, AutoAddPolicy
import discovery.connectors.dhcp as dhcp
from discovery.connectors.dhcp import dhcp_connector
from discovery.connectors.simulator import device_simulator
#from devices.utils.scn_log import logger
from utils.scn_log import logger


# Constants

CWD = os.path.dirname(os.path.abspath(__file__))
VENDOR_CONNECTORS_PATH = CWD+"/connectors/"
VENDOR_PLUGINS_PATH = CWD+"/connectors/vendor_plugin_config.json"
REPETITIONS = 3

# Define the parameters to be fetched from the devices using SSH, and the corresponding commands and regex patterns
param_against_file ={
    "Inventory Type": {"file": "cat /proc/cpuinfo", "regex":r"vendor_id\s+:(.*)"},
    "Vendor Name": {"file": "/proc/cpuinfo", "regex":r"vendor_id\s+:(.*)"},    
    "IP Address": {"file": "IP_Address", "regex":r"(.*)"},
    "DHCP Lease": {"file": "DHCP_Lease", "regex":r"(.*)"},
    "DHCP Options": {"file": "DHCP_Options", "regex":r"(.*)"},
    "Firmware Version": {"file": "Firmware_Version", "regex":r"(.*)"},
    "Software Version": {"file": "uname -a", "regex":r"(.*)#"},
    "Hardware Model": {"file": "cat /proc/cpuinfo", "regex":r"model name\s+:(.*)"},
    "Serial ID": {"file": "Serial_ID", "regex":r"(.*)"}
}

DevicePluginsPool = json.load(open(VENDOR_PLUGINS_PATH))

# Define the SSH details for each device to connect and fetch the parameters using SSH
device_ssh_details = {
    "client1": {"ip":"127.0.0.1", "username": "vagrant", "password": "vagrant", "port": 22222},
    "MikroTik": {"ip":"127.0.0.1", "username": "admin", "password": "vagrant", "port": 222222},
}



# Create class for db file create and write the data to the database
class ScnDevicesDb:
    def __init__(self):
        self.DHCP_SERVICE_ENABLE = False
        DEVICE_SCAN_CONFIG_PATH = CWD+"/config/device_config.json"
        DHCPConfigDetails = json.load(open(DEVICE_SCAN_CONFIG_PATH))
        self.establish_db_conn()

    #Function to make the database connection
    def establish_db_conn(self):
        self.db_connection = sqlite3.connect("scn_device_info.db", check_same_thread=False)   
        
        cursor = self.db_connection.cursor()

        #Create the database and table if not exists
        cursor.execute(""" 
        Create table if not exists device_db(
            ID INTEGER primary key Autoincrement,
            Serial_ID INTEGER UNIQUE,
            Inventory_Type VARCHAR(255),
            Vendor_Name VARCHAR(255),
            IP_Address VARCHAR(255),
            DHCP_Lease VARCHAR(255),
            DHCP_Options VARCHAR(255),
            Firmware_Version VARCHAR(255),
            Software_Version VARCHAR(255),
            Hardware_Model VARCHAR(255),
            Tags JSON,
            status VARCHAR(225) default "Online") """)
        
        
        cursor.execute(""" 
        Create table if not exists tags(
                       id integer Primary key Autoincrement,
                       tags json,
                       device_count integer default 0) """)

        self.db_connection.commit()
        return self.db_connection
    

    #Function to write the data to the database
    def scan_and_update(self):
        logger.debug("Scanning devices and updating the database")
        self.devices_meta_data = []
        # Simluated Devices with meta data
        self.devices_meta_data = device_simulator.scan_devices() # [....]

        # Get Devices IPs from DHCP server (lease file)
        self.devices = dhcp_connector.scan_devices()

        print("Devices from DHCP: ", self.devices)


        # Connect to each device using IP and Host Name as metioned in connectors/
        self.__get_device_meta_data()


        # Todo: Need to call API to full data from the devices by connecting to the devices using SSH/telnet
        # Depending on device type, the connection method mentioned in .json file (configuration)

        cursor = self.db_connection.cursor()
        for device in self.devices_meta_data:
            logger.debug(f"Updating device {device} in the database")
            cursor.execute("SELECT * FROM device_db WHERE Serial_ID = ?", (device["Serial ID"],))
            rows = cursor.fetchall()
            if rows:
                cursor.execute("UPDATE device_db SET Inventory_Type = ?, Vendor_Name = ?, IP_Address = ?, DHCP_Lease = ?, DHCP_Options = ?, Firmware_Version = ?, Software_Version = ?, Hardware_Model = ? WHERE Serial_ID = ?",
                                (device["Inventory Type"], device["Vendor Name"], device["IP Address"], device["DHCP Lease"], device["DHCP Options"], device["Firmware Version"], device["Software Version"], device["Hardware Model"], device["Serial ID"]))
            else:
                cursor.execute("INSERT INTO device_db (Serial_ID, Inventory_Type, Vendor_Name, IP_Address, DHCP_Lease, DHCP_Options, Firmware_Version, Software_Version, Hardware_Model) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (device["Serial ID"], device["Inventory Type"], device["Vendor Name"], device["IP Address"], device["DHCP Lease"], device["DHCP Options"], device["Firmware Version"], device["Software Version"], device["Hardware Model"]))
        self.db_connection.commit()

    #Function to write the data to the database
    def get_devices_list(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM device_db")
        rows = cursor.fetchall()

        # make dictionary of the data and return
        devices_list = []
        for row in rows:
            devices_list.append({"ID": row[0] ,"Serial_ID":row[1], "Inventory_Type":row[2], "Vendor_Name":row[3], "IP_Address":row[4], "DHCP_Lease":row[5], "DHCP_Options":row[6], "Firmware_Version":row[7], "Software_Version":row[8], "Hardware_Model":row[9], "Tags": row[10], "Status":row[11]})
        return devices_list


    def __get_device_meta_data(self):
        device_name_to_type = {
            "MDS": "Switch",
            "Nexus": "Switch",
            "Cisco": "Switch",
            "Juniper": "Router",
            "Arista": "Switch",
        }

        print("Scanning devices and fetching metadata information")
        print("Devices: ", self.devices)
   
        # Step 5: Create a SSH connection to each device and fetch the required parameters
        SerialNum = 1
        for device in self.devices:
            SerialNum += 1
            print(f"Scanning device {device['hostname']} with IP {device['ip']}")

            # Default device information
            device_metadata_information = {
                        'Inventory Type': 'Unknown',
                        'Serial ID': SerialNum,
                        'Vendor Name': 'Unknown',
                        'IP Address': device["ip"],
                        'DHCP Lease': "--",
                        'DHCP Options': device["mac"],
                        'Firmware Version': "--",
                        'Software Version': "--",
                        'Hardware Model': "--",
                        "DviceType": "Unknown"
            }

            if device["hostname"] in DevicePluginsPool["DevicePluginsPool"].keys(): # Plugins are available for the device
                devicePluginFilePath = DevicePluginsPool["DevicePluginsPool"][device["hostname"]]
                try:
                    # DevicePluginsPool[device["hostname"]] is library path to the device plugin
                    # Example: DevicePluginsPool[device["hostname"]] = "/data/scn_discovery/vendor_plugins/mds.py"
                    # Import the module and create an object of the class
                    # Import module dynamically using importlib
                    #module = importlib.import_module(devicePluginFilePath)

                    module_path = VENDOR_CONNECTORS_PATH+devicePluginFilePath
                    module_name = Path(VENDOR_CONNECTORS_PATH+devicePluginFilePath).stem  # This will give 'mds'

                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    devicesInfo = module.DeviceInfo()
                    devicesInfo.get_metadata_info(device_metadata_information)
                    self.devices_meta_data.append(device_metadata_information.copy())


                except Exception as e:
                    print(f"Error loading plugin for {device['hostname']}")
                    print("Error: ", e)

            else: # For generic devices
                if device["hostname"] in device_ssh_details.keys():
                    device_metadata_information_list = self.__getGenericDegiveInfo(device,SerialNum)
                    SerialNum += len(device_metadata_information_list)
                    self.devices_meta_data.extend(device_metadata_information_list.copy())
                else:
                    logger.error(f"No SSH details available for {device['ip'], device['hostname']}")
                    self.devices_meta_data.append(device_metadata_information.copy())


    # Function to fetch the parameters from the devices using SSH in genreic way
    def __getGenericDegiveInfo(self, device, SerialNumStart):

        device_information_with_dups = []
        device_information = {}

        # Check if SSH details are available for the device
        ssh_details = device_ssh_details.get(device["hostname"], None) # MDS
        if ssh_details:
            SerialNum = SerialNumStart
            sshClient = SSHClient()
            sshClient.set_missing_host_key_policy(AutoAddPolicy())
            ssh_details['ip'] = device["ip"]
            try:
                sshClient.connect(ssh_details['ip'], port=ssh_details['port'], username=ssh_details['username'], password=ssh_details['password'], timeout=5)
                for param, cmd in param_against_file.items():
                    stdin, stdout, stderr = sshClient.exec_command(cmd["file"])
                    output = stdout.read().decode()
                    match = re.search(cmd["regex"], output)
                    if match:
                        device_information[param] = match.group(1).strip()
                    else:
                        device_information[param] = "N/A"
                sshClient.close()
            except Exception as e:
                print(f"Error connecting to {device['hostname']}: {e}")
                for param in param_against_file.keys():
                    device_information[param] = "N/A"
            
            device_information["IP Address"] = device["ip"]
            device_information["DHCP Options"] = device["mac"]

            # Calculate DHCP Lease time depending on the start and stop time
            try:
                format = '%Y/%m/%d %H:%M:%S'
                datetime1 = datetime.strptime(device["start_time"], format)
                datetime2 = datetime.strptime(device["stop_time"], format)
                device_information["DHCP Lease"]  = (datetime2 - datetime1).total_seconds()
            except Exception as e:
                print(f"Error calculating DHCP Lease time: {e}")
                device_information["DHCP Lease"] = "--"

            # Add information for software version
            device_information["Software Version"] = 1.0

            # Duplicate the device information for multiple repetitions
            for i in range(REPETITIONS):
                device_information["Serial ID"] = SerialNum
                SerialNum += 1
                device_information_with_dups.append(device_information.copy())
                
            return device_information_with_dups
