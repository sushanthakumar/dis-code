#!/usr/bin/env python3

'''
python scn-p1-discovery/core/scn_discovery/src/scn_disc_main.py
Project name : SmartConfigNxt
title : scn_disc_main.py
Discription : Discovery and Usecase recommendation 
author : Kamal, Sandhya
version :1.0
'''

from flask import Flask,jsonify, request
from flask_restx import Api, Resource ,fields
import yaml
import pandas as pd 
from flask_cors import CORS
import os
import json
from devices import ScnDevicesDb
from utils.scn_log import logger
from werkzeug.utils import secure_filename
from discovery.connectors.simulator import device_simulator
from discovery.services.dhcp_server.dhcp_service import DHCPService


# Create the Flask app
app = Flask(__name__)
# Create the API
CORS(app)
api = Api(app, title="Device Management API", version="1.0")
# Create the device database object
devices_db = ScnDevicesDb()
dhcp_service = DHCPService()
model_list = api.model('device_db',{
                "Tag":fields.Raw(required = True, description = "Select a tag" ) })

model_tag = api.model('tags',{
                "Tags":fields.Raw(required = True, description = "Add a tag"  )
                           })

################  scan device #################
# Api to handle scan request
@api.route('/v1/synclist')
class scan(Resource):
    @api.doc(description="Retrieve records.")
    @api.response(200, "Successfully retrieved .")
    @api.response(404, "Not found.")
    @api.response(500, "Internal Server Error.")
    def get(self):
        logger.debug("Scanning for devices...") 
        try:
            devices_list = devices_db.scan_and_update()
            devices_list = devices_db.get_devices_list()
            return devices_list, 200
        except Exception as e:
            return {"message": str(e)}, 500
        
############# Discovered devices ##############

# Api to handle list request
@api.route('/v1/devices')
class list(Resource):
    @api.doc(description="Retrieve records.")
    @api.response(200, "Successfully retrieved .")
    @api.response(404, "Not found.")
    @api.response(500, "Internal Server Error.")
    def get(self):
        logger.debug("Retrieving devices list...")
        try:
            devices_list = devices_db.get_devices_list()
            return devices_list, 200
        except Exception as e:
            return {"message": str(e)},

######### Upload devices #########
# API for CSV Upload
def convert_to_wsl_path(path):
    if ":" in path:  
        drive, tail = path.split(":", 1)
        tail =tail.replace('\\', '/')
        return f"/mnt/{drive.lower()}{tail}"
    return path  

@api.route('/v1/devices/upload/<path:file_path>')
class UploadCSV(Resource):
    @api.doc(description="Upload a CSV file from the local file system (supports Docker volumes).")
    @api.response(201, "File uploaded successfully.")
    @api.response(400, "Invalid file path or format.")
    def post(self, file_path):
        try:
            
            file_path = convert_to_wsl_path(file_path)#This line shd be removed later
            file_path = os.path.abspath(os.path.normpath(file_path))
            logger.debug(f"Received file path: {file_path}")

            # Check if file exists
            if not os.path.exists(file_path):
                return {"error": "File not found."}, 400

            # Read CSV file
            try:
                csv_data = pd.read_csv(file_path)
            except Exception as e:
                logger.error(f"Error reading CSV file: {e}")
                return {"error": "Failed to read CSV file."}, 400

            # Database operations
            conn = devices_db.establish_db_conn()
            cursor = conn.cursor()
            for _, device in csv_data.iterrows():
                logger.debug(f"Processing device: {device.to_dict()}")

                cursor.execute("SELECT * FROM device_db WHERE Serial_ID = ?", (device["Serial ID"],))
                rows = cursor.fetchall()

                if rows:
                    cursor.execute("""
                        UPDATE device_db SET 
                        Inventory_Type = ?, Vendor_Name = ?, IP_Address = ?, 
                        DHCP_Lease = ?, DHCP_Options = ?, Firmware_Version = ?, 
                        Software_Version = ?, Hardware_Model = ? 
                        WHERE Serial_ID = ?
                    """, (
                        device["Inventory Type"], device["Vendor Name"], device["IP Address"],
                        device["DHCP Lease"], device["DHCP Options"], device["Firmware Version"],
                        device["Software Version"], device["Hardware Model"], device["Serial ID"]
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO device_db 
                        (Serial_ID, Inventory_Type, Vendor_Name, IP_Address, 
                        DHCP_Lease, DHCP_Options, Firmware_Version, 
                        Software_Version, Hardware_Model) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        device["Serial ID"], device["Inventory Type"], device["Vendor Name"],
                        device["IP Address"], device["DHCP Lease"], device["DHCP Options"],
                        device["Firmware Version"], device["Software Version"], device["Hardware Model"]
                    ))

            conn.commit()
            cursor.close()

            return {"message": "File uploaded successfully"}, 201

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": "An unexpected error occurred."}, 500



@api.route('/v1/devices/<int:id>/tags')        
@api.expect(model_list)
class device_tag(Resource):
    def patch(self, id):
        data = request.json
        tags = data.get("Tag", {})
        conn = devices_db.establish_db_conn()
        cursor = conn.cursor()

        # Convert the dictionary into a list of JSON strings
        tag_list = [json.dumps({key: value}) for key, value in tags.items()]

        # Fetch existing tags for the device
        cursor.execute("SELECT Tags FROM device_db WHERE ID = ?", (id,))
        existing_tag = cursor.fetchone()

        if existing_tag and existing_tag[0] is not None:
            # If existing tag(s) exist, decrement their count
            old_tags = json.loads(existing_tag[0])  # Convert JSON string back to a dictionary
            
            if isinstance(old_tags, dict):  # Handle cases where only one tag was stored
                old_tags = [json.dumps(old_tags)]
            
            for old_tag in old_tags:
                cursor.execute("SELECT device_count FROM tags WHERE tags = ?", (old_tag,))
                old_tag_data = cursor.fetchone()
                
                if old_tag_data:
                    old_device_count = old_tag_data[0]
                    new_device_count = max(0, old_device_count - 1)  # Ensure count does not go negative
                    cursor.execute("UPDATE tags SET device_count = ? WHERE tags = ?", (new_device_count, old_tag))

        # Assign new tags
        for tag_value in tag_list:
            cursor.execute("SELECT device_count FROM tags WHERE tags = ?", (tag_value,))
            tag_data = cursor.fetchone()

            if tag_data:
                # If tag exists, increment count
                device_count = tag_data[0] + 1
                cursor.execute("UPDATE tags SET device_count = ? WHERE tags = ?", (device_count, tag_value))
            else:
                # If tag does not exist, create a new row with count = 1
                cursor.execute("INSERT INTO tags (tags, device_count) VALUES (?, ?)", (tag_value, 1))

        # Store the new tags in device_db
        cursor.execute("UPDATE device_db SET Tags = ? WHERE ID = ?", (json.dumps(tag_list), id))

        # Commit changes
        conn.commit()
        return {"message": "Tags updated and counts adjusted."}, 200


############ Health Check ###########

@api.route("/v1/devices/healthcheck/<id>")
class Healthcare(Resource): 
    @api.doc(description="Update healthcare device status.")
    @api.response(200, "Device status updated successfully.")
    @api.response(404, "Device not found.")
    def patch(self,id):
        logger.debug("Updating device status...")
        try:
            conn = devices_db.establish_db_conn()
            cursor = conn.cursor()
            device_status = "offline"

            cursor.execute("SELECT * FROM device_db WHERE ID = ?", (id,))
            device = cursor.fetchone()

            if not device:
                return {"message": "Device not found."}, 404

            cursor.execute("UPDATE device_db SET status = ? WHERE ID = ?", (device_status, id))
            conn.commit()
            # Fetch updated record
            cursor.execute("SELECT * FROM device_db WHERE ID = ?", (id,))
            updated_device = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            updated_device_dict = dict(zip(column_names, updated_device))

            return {"message": "Device status updated successfully.", "updated_record": updated_device_dict}, 200

        except Exception as e:
            return {"message": str(e)}, 500
        
############### Tags ###############
@api.route('/v1/customtags')
class tag(Resource):
    #Retrives the tags data from the tags table
    def get(self):
        logger.debug("Retrieving tags data...")
        conn = devices_db.establish_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tags")
        #fetches all the record from the table
        rows = cursor.fetchall()
        #List to store all retrived records
        tags = []
        for row in rows:
            #Appenda all the row in the list initialized above
            tags.append([{"Id" : row[0]},json.loads(row[1]), {"Device_count" : row[2]}])   
        return tags  
    
    #Adds the data in the data 
    @api.expect(model_tag)
    @api.doc(description="Retrieve records.")
    @api.response(200, "Successfull .")
    @api.response(404, "Not found.")
    @api.response(500, "Internal Server Error.")
    def post(self):
        logger.debug("Creating a new tag...")
        try:
            data = request.json
            conn = devices_db.establish_db_conn()
            cursor = conn.cursor()
            query = """
                    INSERT INTO tags (
                        Tags
                    ) VALUES (?)
                """
            #Sends the json values to the query
            values = (json.dumps(data["Tags"]),)
            cursor.execute(query, values)
            conn.commit()

            return {"message": "Record successfully created."}, 201
        except Exception as e:
            return {"message": str(e)}, 500
    
    #Delets the record based on their ID
    @api.doc(params={'id': 'Delete Tag'})
    @api.response(200, "Tag successfully deleted.")
    @api.response(400, "Tag name is required.")
    @api.response(404, "Tag not found.")
    def delete(self):
        ID = request.args.get('id')

        # Debugging: Print the received name
        print(f"Received ID: {ID}")

        if not ID:
            return {"result": "Tag id is required."}, 400

        conn = devices_db.establish_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, device_count FROM tags WHERE id=?", (ID,))
        tag_data = cursor.fetchone()

        if not tag_data:
            return {"result": "Tag not found."}, 404

        tag_id, device_count = tag_data

        # Check if the tag is linked to any devices
        if device_count > 0:
            return {"result": "Tag is linked to devices and cannot be deleted Please uncheck it."}, 409

        # Proceed with deleting the tag if device_count is 0
        cursor.execute("DELETE FROM tags WHERE id=?", (ID,))
        conn.commit()
        conn.close()

        return {"result": f"Tag '{ID}' deleted successfully."}, 200


# Add api to support "/v1/dhcpservice/start" endpoint
@api.route('/v1/dhcpservice/start')
class dhcp_service_start(Resource):
    @api.doc(description="Start the DHCP service.")
    @api.response(200, "DHCP service started successfully.")
    @api.response(500, "Internal Server Error.")
    def patch(self):
        print("Patch Starting the DHCP service...")
        try:
            dhcp_service.start()
            logger.debug("DHCP service started successfully.")
            return {"message": "DHCP service started successfully."}, 200
        except Exception as e:
            logger.error(f"Error starting DHCP service: {e}")
            return {"message": str(e)}, 500

# Add api to support "/v1/dhcpservice/stop" endpoint
@api.route('/v1/dhcpservice/stop')
class dhcp_service_stop(Resource):
    @api.doc(description="Stop the DHCP service.")
    @api.response(200, "DHCP service stopped successfully.")
    @api.response(500, "Internal Server Error.")
    def patch(self):
        print("Patch Stopping the DHCP service...")
        try:
            dhcp_service.stop()
            logger.debug("DHCP service stopped successfully.")
            return {"message": "DHCP service stopped successfully."}, 200
        except Exception as e:
            logger.error(f"Error stopping DHCP service: {e}")
            return {"message": str(e)}, 500


#Api to perform recommendation
@api.route('/v1/upload')
@api.doc(description="devices.")
class upload(Resource):
    def post(self):
        try:
            #Loads data from the Recommendations file
            print("Headers ----> : ", request.headers)

            
            return
            

        except Exception as e:
            return {"message": str(e)}, 500
######## Upload devices ##############
@api.route('/v1/devices/upload')
class UploadCSV(Resource):
    @api.doc(description="Upload a CSV file from the local file system (supports Docker volumes).")
    @api.response(201, "File uploaded successfully.")
    @api.response(400, "Invalid file path or format.")
    @api.response(500, "Internal server error.")
    def post(self):
        try:
            file_path = "/tmp/devices/0064159746"
            logger.debug(f"Received file path: {file_path}")

            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return {"error": "File not found."}, 400

            # Read CSV file
            try:
                csv_data = pd.read_csv(file_path)
                csv_data.columns = csv_data.columns.str.strip()  # Remove spaces from column names
                logger.debug(f"CSV Columns: {csv_data.columns.tolist()}")
            except Exception as e:
                logger.error(f"Error reading CSV file: {e}")
                return {"error": "Failed to read CSV file."}, 400

            # Check if necessary columns exist
            required_columns = [
                "Serial ID", "Inventory Type", "Vendor Name", "IP Address",
                "DHCP Lease", "DHCP Options", "Firmware Version",
                "Software Version", "Hardware Model"
            ]
            missing_columns = [col for col in required_columns if col not in csv_data.columns]
            if missing_columns:
                logger.error(f"Missing columns in CSV: {missing_columns}")
                return {"error": f"Missing columns in CSV: {missing_columns}"}, 400

            # Database operations
            conn = devices_db.establish_db_conn()
            cursor = conn.cursor()

            for _, device in csv_data.iterrows():
                try:
                    serial_id = device["Serial ID"]
                    cursor.execute("SELECT * FROM device_db WHERE Serial_ID = ?", (serial_id,))
                    rows = cursor.fetchall()

                    if rows:
                        cursor.execute("""
                            UPDATE device_db SET 
                            Inventory_Type = ?, Vendor_Name = ?, IP_Address = ?, 
                            DHCP_Lease = ?, DHCP_Options = ?, Firmware_Version = ?, 
                            Software_Version = ?, Hardware_Model = ? 
                            WHERE Serial_ID = ?
                        """, (
                            device["Inventory Type"], device["Vendor Name"], device["IP Address"],
                            device["DHCP Lease"], device["DHCP Options"], device["Firmware Version"],
                            device["Software Version"], device["Hardware Model"], serial_id
                        ))
                    else:
                        cursor.execute("""
                            INSERT INTO device_db 
                            (Serial_ID, Inventory_Type, Vendor_Name, IP_Address, 
                            DHCP_Lease, DHCP_Options, Firmware_Version, 
                            Software_Version, Hardware_Model) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            serial_id, device["Inventory Type"], device["Vendor Name"],
                            device["IP Address"], device["DHCP Lease"], device["DHCP Options"],
                            device["Firmware Version"], device["Software Version"], device["Hardware Model"]
                        ))
                except KeyError as ke:
                    logger.error(f"Missing column in row: {ke}")
                    continue  # Skip invalid rows

            conn.commit()
            return {"message": "Success"}, 201



        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {"error": "An unexpected error occurred."}, 500

# Run the app
if __name__ == '__main__':
    logger.debug("Starting Device Management API server...")
    devices_db.scan_and_update()
    app.run(host="0.0.0.0", port=5000, debug=True)
