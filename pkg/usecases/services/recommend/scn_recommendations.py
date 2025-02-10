#!/usr/bin/env python3

'''
File: scn_usecase_main.py
Author: Sandhya, Kamal
Description: This file contains the APIs to handle usecase and recommendations
'''

import os
import re
import pandas as pd
import yaml
from flask import request
from flask_restx import Resource
from flask import Flask
from flask_restx import Api
from flask import jsonify
import requests
import sys
######### Configuration ##########
USECASE_YAML_FILE = os.path.join(os.path.dirname(__file__), "../../config/usecase.yaml")
# Get API link from command line argument
# Get API link from environment variable
API_INTERFACE = os.getenv("API_INTERFACE")

if not API_INTERFACE:
    raise ValueError("API_INTERFACE environment variable is not set.")
#################################

        
############## Recommendations  #####################

class Recommendation(Resource):
    def load_data(self):
        try:
            # self.conn = devices_db.establish_db_conn()
            # self.cursor = self.conn.cursor()
            #loads the usecase yaml file
            print("yaml file" , USECASE_YAML_FILE)
            with open(USECASE_YAML_FILE, "r") as file:
                data = yaml.safe_load(file)

            #converting the yaml data into dataframe  
            self.usecase_data = pd.DataFrame(data['usecases'])
            #print(self.usecase_data)
            
            # Request Device Management API to get the devices list
            self.device_data = pd.DataFrame(requests.get(f"{API_INTERFACE}/v1/devices").json())
            print(self.device_data)
            
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    #Logic of the recommendations 
    def validate_recommendation(self):
        recommendations = []

        for _,usecase in self.usecase_data.iterrows(): 
            usecase_id, description, server_type, server_count, switch_type, switch_count, storage_type, storage_count = usecase
            
            available_server = available_switch = available_storage = 0
        
            # Check if the count is not NaN and greater than 0 to check availability
            if pd.notna(server_count) and server_count > 0:
                available_server = self.device_data[self.device_data['Inventory_Type'] == server_type].shape[0]
            
            if pd.notna(switch_count) and switch_count > 0:
                available_switch = self.device_data[self.device_data['Inventory_Type'] == switch_type].shape[0]
            
            if pd.notna(storage_count) and storage_count > 0:
                available_storage = self.device_data[self.device_data['Inventory_Type'] == storage_type].shape[0]
            
            # Check the availability for the specified devices
            server_check = (pd.isna(server_count) or available_server >= server_count)
            switch_check = (pd.isna(switch_count)  or available_switch >= switch_count)
            storage_check = (pd.isna(storage_count) or available_storage >= storage_count)

            # If the available devices meet the requirements for the specified ones, add recommendation
            if server_check and switch_check and storage_check:
                recommendations.append({
                    'Usecase_ID': usecase_id,
                    'Description': description
                })

        return recommendations
    
    

    



