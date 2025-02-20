'''
File Name: scn_log.py
Author: Sandhya and Kamal
Description: This file contains the logging configuration for the device management API server.
'''

import logging

# Create logging object for the API server logs 
logging.basicConfig(filename='device_management.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
# Configure the logging level
logging.getLogger().setLevel(logging.DEBUG)
# Create a logger object
logger = logging.getLogger(__name__)
# create for console logging
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)

logger.debug("Logger initialized successfully")
