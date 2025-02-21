'''
File: scn_disc_db.py
Author: Sandhya, Kamal
Description: This file contains the class ScnDevicesDb which is used to create and write data to the database.
'''
import os
import sqlite3
import json
import importlib
from pathlib import Path
#import discovery.connectors.dhcp as dhcp
from discovery.connectors.dhcp import dhcp_connector
from discovery.connectors.simulator import device_simulator
#from devices.utils.scn_log import logger
from utils.scn_log import logger
import sys
import constants
# Constants
CWD = os.path.dirname(os.path.abspath(__file__))
VENDOR_CONNECTORS_PATH = CWD+"/connectors/"
VENDOR_PLUGINS_PATH = CWD+"/connectors/vendor_plugin_config.json"
DevicePluginsPool = json.load(open(VENDOR_PLUGINS_PATH))

# Create class for db file create and write the data to the database
class ScnDevicesDb:
    def __init__(self):
        self.devices_meta_data = []
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
            Inventory_Type VARCHAR(255),
            Vendor_Name VARCHAR(255),
            Hardware_Address VARCHAR(255) primary key,
            IP_Address VARCHAR(255),
            DHCP_Lease VARCHAR(255),
            Firmware_Version VARCHAR(255),
            Software_Version VARCHAR(255),
            Hardware_Model VARCHAR(255),
            Tags JSON,
            status VARCHAR(225) default "Online",
            Discovery_Type VARCHAR(255)) """)
        
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

        # Simluated Devices with meta data
        self.devices_meta_data = device_simulator.scan_devices()
        # Add new column for Discovery Type with value "Simulated"
        for device in self.devices_meta_data:
            device["Discovery Type"] = "Simulated"

        # Get Devices IPs from DHCP server (lease file)
        self.devices = dhcp_connector.scan_devices()
        logger.debug(f"Devices from DHCP server: {self.devices}")
        # Connect to each device using IP and Host Name as metioned in connectors/
        self.__get_device_meta_data() 

        cursor = self.db_connection.cursor()
        for device in self.devices_meta_data:

            cursor.execute("SELECT * FROM device_db WHERE Hardware_Address = ?", (device["Hardware Address"],))
            #cursor.execute("SELECT COUNT(*) FROM device_db;")
            rows = cursor.fetchall()
            
            logger.debug(f"Device info: {device}")

            if rows:
                cursor.execute("UPDATE device_db SET Inventory_Type = ?, Vendor_Name = ?, Hardware_Address = ?, IP_Address = ?, DHCP_Lease = ?, Firmware_Version = ?, Software_Version = ?, Hardware_Model = ?, Discovery_Type = ? WHERE Hardware_Address = ?",
                                (device["Inventory Type"], device["Vendor Name"], device["Hardware Address"], device["IP Address"], device["DHCP Lease"],  device["Firmware Version"], device["Software Version"], device["Hardware Model"], device["Discovery Type"], device["Hardware Address"]))
            else:
                cursor.execute("INSERT INTO device_db ( Inventory_Type, Vendor_Name, Hardware_Address, IP_Address, DHCP_Lease, Firmware_Version, Software_Version, Hardware_Model,Discovery_Type) VALUES (?, ?, ?, ?, ?, ?, ?, ?,'DHCP')",
                                (device["Inventory Type"], device["Vendor Name"], device["Hardware Address"], device["IP Address"], device["DHCP Lease"],  device["Firmware Version"], device["Software Version"], device["Hardware Model"]))
        self.db_connection.commit()
        

    #Function to write the data to the database
    def get_devices_list(self):
        cursor = self.db_connection.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM device_db")
        rows = cursor.fetchall()

        # 'Flash Blade', 'Pure Storage', 'fc:14:1b:dd:f1:a6', '10.1.1.196', '3600', 'v1.0', 'Purity//FA 6.6.10', 'XFM-8400-12', None, 'Online', 'Simulated'
        # make dictionary of the data and return
        devices_list = []
        for row in rows:
            devices_list.append({"Inventory_Type": row["Inventory_Type"],
                                "Vendor_Name": row["Vendor_Name"],
                                "Hardware_Address": row["Hardware_Address"],
                                "IP_Address": row["IP_Address"],
                                "DHCP_Lease": row["DHCP_Lease"],
                                "Firmware_Version": row["Firmware_Version"],
                                "Software_Version": row["Software_Version"],
                                "Hardware_Model": row["Hardware_Model"],
                                "Tags": row["Tags"],
                                "Status": row["status"],
                                "Discovery_Type": row["Discovery_Type"]})        
        return devices_list

    #Function to delete the devices from the database whos device type is DHCP
    def delete_devices(self):
        logger.debug("Deleting the entryies with discovery type: DHCP")
        cursor = self.db_connection.cursor()
        cursor.execute("DELETE FROM device_db WHERE Discovery_Type = 'DHCP'")
        print("Deleted the devices from the database whos device type is DHCP")
        self.db_connection.commit()    

    def __get_collect_device_info_from_connector(self, devicePluginFilePath, device_metadata_information):
        try:
            # DevicePluginsPool[device["Inventory Type"]] is library path to the device plugin
            # Example: DevicePluginsPool[device["Inventory Type"]] = "/data/scn_discovery/vendor_plugins/mds.py"
            # Import the module and create an object of the class
            # Import module dynamically using importlib

            module_path = VENDOR_CONNECTORS_PATH+devicePluginFilePath
            module_name = Path(VENDOR_CONNECTORS_PATH+devicePluginFilePath).stem  # This will give 'mds'

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            devicesInfo = module.DeviceInfo()
            devicesInfo.get_metadata_info(device_metadata_information)
            logger.debug("Device metadata information: %s", device_metadata_information)
            self.devices_meta_data.append(device_metadata_information.copy())

        except Exception as e:
            logger.debug(f"Error loading plugin for {devicePluginFilePath}")
            logger.debug("Error: ", e)

    def __get_device_meta_data(self):

        # Step 5: Create a SSH connection to each device and fetch the required parameters
        for device in self.devices:
            print(f"Scanning device {device['Inventory Type']} with IP {device['ip']}")

            # Default device information
            device_metadata_information = {
                        'Inventory Type': device["Inventory Type"],
                        'Vendor Name': 'Unknown',
                        'Hardware Address': device["mac"],
                        'IP Address': device["ip"],
                        'DHCP Lease': "--",
                        'Firmware Version': "--",
                        'Software Version': "--",
                        "Discovery Type": "DHCP",
                        'Hardware Model': "Unknown",
            }

            # if Inventory Type is available in the DevicePluginsPool, then use the plugin to get the metadata information
            if device["Inventory Type"] in DevicePluginsPool["DevicePluginsPool"].keys(): # Plugins are available for the device
                devicePluginFilePath = DevicePluginsPool["DevicePluginsPool"][device["Inventory Type"]]
                self.__get_collect_device_info_from_connector(devicePluginFilePath, device_metadata_information)

            else: # For generic devices : connector is not available
                logger.debug("No plugin found for %s", device)
                self.__get_collect_device_info_from_connector(DevicePluginsPool["DefaultPlugin"], device_metadata_information)

    #Function to get the device health "offline" or "online"
    def healthcheck(self, id):
        logger.debug("Starting healthcheck for device ID %s...", id)

        # Fetch device information from the database
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM device_db WHERE Hardware_Model = ?", (id,))
        device = cursor.fetchone()

        if not device:
            logger.error("Device with Hardware_Model %s not found in database.", id)

            return "Device Not Found"
        
        column_names = [desc[0] for desc in cursor.description]
        # Ensure the fetched data matches the expected format
        if isinstance(device, tuple) and len(device) == len(column_names):
            device_dict = dict(zip(column_names, device))
        else:
            logger.error(f"Database fetch error: device data malformed for ID %s.",id)
            return "Database Fetch Error"

        # Retrieve essential device details
        ip_address = device_dict.get("IP_Address")
        inventory_type = device_dict.get("Inventory_Type")

        if not ip_address or not inventory_type:
            logger.error("IP Address or Inventory Type column not found or is empty in database.")
            return "Invalid Device Data"

        logger.debug("Performing health check on %s with IP %s", inventory_type, ip_address)

        device_metadata_information = {
            'Inventory Type': inventory_type,
            'Vendor Name': "Unknown",
            'Hardware Address': "--",
            'IP Address': ip_address,
            'DHCP Lease': "--",
            'Firmware Version': "--",
            'Software Version': "--",
            'Hardware Model': "--",
            "Discovery Type": "Unknown"
        }
        # Check if a plugin exists for the given inventory type
        if inventory_type in DevicePluginsPool["DevicePluginsPool"]:
            devicePluginFilePath = DevicePluginsPool["DevicePluginsPool"][inventory_type]

            try:
                module_path = VENDOR_CONNECTORS_PATH + devicePluginFilePath
                module_name = Path(module_path).stem 
                
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Perform the health check using the plugin
                devicesInfo = module.DeviceInfo()
                device_status = devicesInfo.healthcheck(device_metadata_information)

                return device_status
            except Exception as e:
                logger.error("Error loading plugin for %s: %s", inventory_type, e)
                return "Plugin Error"

        logger.error("No plugin found for %s",inventory_type)
        return "No Plugin Found"