#!/usr/bin/env python3

'''
File: scn_usecase_main.py
Author: Sandhya, Kamal
Description: This file contains the APIs to handle usecase and recommendations
'''

import os
import re
import sys
import pandas as pd
import yaml
from flask import request
from flask_restx import Resource
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask import jsonify
import requests

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CWD+'/../services/recommend') 


######### Configuration ##########
USECASE_YAML_FILE = os.path.join(os.path.dirname(__file__)+"/../config/usecase.yaml")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Check if API link is provided in the command line
if len(sys.argv) < 2:
    print("Usage: python api.py <API_INTERFACE_URL>")
    sys.exit(1)

API_INTERFACE = sys.argv[1]  # Get API link from command-line argument
os.environ["API_INTERFACE"] = API_INTERFACE 
#################################

from scn_recommendations import Recommendation


# Create the Flask app
app = Flask(__name__)
# Create the API
CORS(app)
# Create the API
api = Api(app, title="Usecase API", version="1.0")

#############  Usecase  #####################
#api to add new usecases and retrive all the usecases
@api.route('/v1/usecases/')
class usecase(Resource):
    #Retrives all the records fron the usecase table
    @api.doc(description="Retrieve records.",
             )
    @api.response(200, "Successfully retrieved .")
    @api.response(404, "Not found.")
    @api.response(500, "Internal Server Error.")
    def get(self):
        #print("yaml file", CWD+"/../config/usecase.yaml")
        try:
            with open(USECASE_YAML_FILE, "r") as file:
                data = yaml.safe_load(file)
            usecase = pd.DataFrame(data['usecases'])
            if usecase.empty:
                return {"message": "No records found in the YAML file."}, 404
            
            return usecase.to_dict(orient="records"), 200
        
        except FileNotFoundError:
            print("YAML file is : ", USECASE_YAML_FILE)
            return {"message": "YAML file not found."}, 404
        
        except yaml.YAMLError as e:
            return {"message": f"Error parsing YAML file: {str(e)}"}, 500
        
        except Exception as e:
            return {"message": str(e)}, 500


@api.route('/v1/usecases/<int:id>')
class usecase_id(Resource):
    def get(self,id):
        try:
            with open(USECASE_YAML_FILE, "r") as file:
                data = yaml.safe_load(file)
            usecase = pd.DataFrame(data['usecases'])

            if usecase.empty:
                return {"message": "No records found in the YAML file."}, 404
            
            detailed_info = usecase[usecase['ID'] == id].to_dict(orient='records')
            if detailed_info:
                return {"details": detailed_info}, 200
            else:
                return {"message": f"No use case found with ID {id}."}, 404

        
        except FileNotFoundError:
            print("YAML file is : ", USECASE_YAML_FILE)
            return {"message": "YAML file not found."}, 404
        
        except yaml.YAMLError as e:
            return {"message": f"Error parsing YAML file: {str(e)}"}, 500
        
        except Exception as e:
            return {"message": str(e)}, 500


''' This function loads the the data from "load_data" and performs recommendation in "validate_recommendation" 
    and displays the response'''
#Api to perform recommendation
@api.route('/v1/usecases/recommendations')  
@api.doc(description="Recommendations.")
class recommendations(Resource):
    def get(self):
        try:
            #Loads data from the Recommendations file
            Recommendation.load_data(self)
            recommendations = Recommendation.validate_recommendation(self)

            if recommendations:
                return {"recommendations": recommendations}
            else:
                return {"message": "No use case matches the selected devices."}, 404

        except Exception as e:
            print("Error in recommendations", e)
            return {"message": str(e)}, 500
        

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001 ,debug=True)

