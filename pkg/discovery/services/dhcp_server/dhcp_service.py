# Define a class for DHCP service. 
# One method to start and stop the DHCP server "systemctl start isc-dhcp-server" and "systemctl stop isc-dhcp-server"
# Another method to check the status of the DHCP server "systemctl status isc-dhcp-server"
# Another method to restart the DHCP server "systemctl restart isc-dhcp-server"
import os
import pandas as pd
import paramiko
import json
from utils.scn_log import logger
import sys
from constants import DHCP_HOST_CONFIG_FILE, DHCPD_CONFIG_FILE, TEMP_REMOTE_PATH, DHCPD_CONFIG_SERVER_PATH
from utils.dhcp_ops import dhcp_ops_get_service_name

class DHCPService:
    # Define the constructor to initialize the DHCP server IP, username, and password and port number
    def __init__(self):
        self.client = None
        # Read the configuration json file to get ip, username, password and port
        self.__dhcp_details = json.load(open(DHCP_HOST_CONFIG_FILE))

    # Define a method to connect to the DHCP server and keep client object
    def connect(self):
        logger.info("Connecting to the DHCP server...")
        """Connect to the DHCP server."""
        try:
            dhcp_details = self.__dhcp_details
            print("### Read data from file: ", dhcp_details)
            print(f"Connecting to the DHCP server at {dhcp_details['ip']}...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.sevice_name = dhcp_ops_get_service_name(self.client)
            logger.info(f"Service name: {self.service_name}")

            self.client.connect(dhcp_details["ip"], 
                                port=dhcp_details["port"], 
                                username=dhcp_details["username"], 
                                password=dhcp_details["password"], 
                                timeout=10)
        
        except Exception as e:
            logger.info(f"Error connecting to the DHCP server: {e}")
        else:
            logger.info("Connected to the DHCP server successfully.")
    
    # Define a method to execute the command on the DHCP server
    def __execute_command(self, command):
        """Execute a command on the DHCP server."""
        try:
            # Execute the command on the DHCP server
            stdin, stdout, stderr = self.client.exec_command(command)
            # Print the output of the command
            print(stdout.read().decode())
        except Exception as e:
            print(f"Error executing the command: {e}")
        else:
            print(f"Command executed successfully: {command}")

    # Define a method to start the DHCP server
    def start(self):
        print("Start DHCP is called from User!!!")
        self.connect()
        """Start the DHCP server."""

        # Collect dhcp config file from /tmp/dhcpd.conf
        # Send this file to dhcp server
        # use scp to copy the file to dhcp server
        try:
            # # Open SFTP connection
            sftp_obj = self.client.open_sftp()
            print("SFTP connection established.")

            # Transfer file
            state = sftp_obj.put(DHCPD_CONFIG_FILE, TEMP_REMOTE_PATH)
            logger.debug(f"File transfer successful. Remote file attributes: {state}")


            # Close SFTP connection
            sftp_obj.close()


            # Move file to the final destination using sudo
            logger.info(f"Moving the file to the final destination")
            command = f"sudo mv {TEMP_REMOTE_PATH} {DHCPD_CONFIG_SERVER_PATH}"
            stdin, stdout, stderr = self.client.exec_command(command)
            logger.info(f"Executing command: {command}")     

            command = f"sudo chown root:root {DHCPD_CONFIG_SERVER_PATH}"
            stdin, stdout, stderr = self.client.exec_command(command)
            logger.info(f"Executing command: {command}")            

        except Exception as e:
            logger.error(f"Error copying the DHCP configuration file: {e}")         
            return
            
        # Execute the command to start the DHCP server
        self.__execute_command(f"sudo systemctl start {self.service_name}")
        print(f"{self.service_name} service started successfully.")
    

    # Define a method to stop the DHCP server
    def stop(self):
        """Stop the DHCP server."""
        print(f"Stopping DHCP service...")
        # Execute the command to stop the DHCP server
        self.__execute_command(f"sudo systemctl stop {self.service_name}")
        print(f"{self.service_name} service stopped successfully.")
        sys.stdout.flush()

    # Define a method to check the status of the DHCP server
    def status(self):
        """Check the status of the DHCP server."""
        print(f"Checking the status of the {self.service_name} service...")
        # Execute the command to check the status of the DHCP server
        self.__execute_command(f"systemctl status {self.service_name}")
        print(f"{self.service_name} service is running.")
        sys.stdout.flush()        