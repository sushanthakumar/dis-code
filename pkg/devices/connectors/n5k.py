'''
File: scn_disc_db.py
Author: Sandhya, Kamal
Description: This file contains the class ScnDevicesDb which is used to create and write data to the database from MDS.
'''
import os
from abc import ABC, abstractmethod
from scan_device_info_plugin import DeviceInfoPlugin

class DeviceInfo(DeviceInfoPlugin):
    def __init__(self):
        pass

    def get_metadata_info(self, deviceInfo):
        print("Device info from n5k")
        updated = {
            'Inventory Type': 'n5k',
            'Serial ID': 2001,
            'Vendor Name': 'n5k',
            'IP Address': 'ValueError',
            'DHCP Lease': 'ValueError'
        }
        deviceInfo.update(updated)
        deviceInfo["Vendor Name"] = "Cisco"