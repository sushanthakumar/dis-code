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
        print("Device info from Flashblade")
        updated = {
            'Inventory Type': 'MikroTik',
            'Serial ID': 6001,
            'Vendor Name': 'MikroTik',
            'IP Address': deviceInfo['IP Address'],
            'DHCP Lease': '3600'
        }
        deviceInfo.update(updated)