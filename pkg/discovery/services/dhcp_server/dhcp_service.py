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
 
# Get CWD using os with 
CWD = os.path.dirname(os.path.abspath(__file__))
DHCP_HOST_CONFIG_FILE = "/tmp/dhcp_host.conf"
DHCPD_CONFIG_FILE = "/tmp/dhcpd.conf"
DHCPD_CONFIG_SERVER_PATH = "/etc/dhcp/dhcpd.conf"
TEMP_REMOTE_PATH = "/tmp/dhcpd_tmp.conf"


# DHCP_HOST_CONFIG_FILE = "/tmp/config/dhcp_host.conf"
# DHCPD_CONFIG_FILE = "/tmp/config/dhcpd.conf"
# DHCPD_CONFIG_SERVER_PATH = "/etc/dhcp/dhcpd.conf"
# TEMP_REMOTE_PATH = "/tmp/dhcpd_tmp.conf"

class DHCPService:
    # Define the constructor to initialize the DHCP server IP, username, and password and port number
    def __init__(self):
        self.client = None

    
    # Define a method to connect to the DHCP server and keep client object
    def connect(self, config_file=DHCP_HOST_CONFIG_FILE):
        logger.info("Connecting to the DHCP server...")
        """Connect to the DHCP server."""
        try:
            # Read the configuration json file to get ip, username, password and port
            dhcp_details = json.load(open(config_file))
            print("### Read data from file: ", dhcp_details)
            print(f"Connecting to the DHCP server at {dhcp_details['ip']}...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.service_name = dhcp_details["service_name"]

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
        self.connect(DHCP_HOST_CONFIG_FILE)
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
            
            print(f"File transfer successful. Remote file attributes: {state}")
            sys.stdout.flush()

            # Close SFTP connection
            sftp_obj.close()


            # Move file to the final destination using sudo
            logger.info(f"Moving the file to the final destination")
            command = f"sudo mv {TEMP_REMOTE_PATH} {DHCPD_CONFIG_SERVER_PATH}"

            command = "sudo chown root:root /etc/dhcp/dhcpd.conf"
            stdin, stdout, stderr = self.client.exec_command(command)
            logger.info(f"Executing command: {command}")            

            status = self.client.exec_command(command)
            print(f"File moved to the final destination. Status: {status}")

        except Exception as e:
            print(f"Error copying the DHCP configuration file: {e}")
            sys.stdout.flush()           
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