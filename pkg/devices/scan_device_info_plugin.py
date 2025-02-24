'''
File: scn_disc_db.py
Author: Sandhya, Kamal
'''
import os
from abc import ABC, abstractmethod

# Class DeviceInfoPlugin is abstract class for all the device plugins
# It has abstract methods to be implemented by the child classes
# It has a method to get the device information
# Methods:
#     get_device_info: Abstract method to get the device information
#     Return type: dict having device information
#     device information includes:
#      - Inventory Type,Serial ID,Vendor Name,IP Address,Firmware Version,Software Version,Hardware Model

class DeviceInfoPlugin(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_metadata_info(self, deviceInfo):
        pass