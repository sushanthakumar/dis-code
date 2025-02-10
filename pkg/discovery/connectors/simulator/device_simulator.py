'''
File: device_sim_main.py
Authors: Kamal, Sandhya
Description: Simulates discovring devices and providing meta data directly
'''

import pandas as pd
import os

DEVICE_META_DATA = os.path.dirname(os.path.abspath(__file__))+"/DeviceMetadata1.csv"

def scan_devices():
    # Check DEVICE_META_DATA_BY_USER exists
    if os.path.exists(DEVICE_META_DATA):
        # Read CSV file
        df = pd.read_csv(DEVICE_META_DATA)
    else:
        return []

    # from df chose rows randomly
    df2 = df.sample(frac=0.3)
    json_data = df2.to_dict(orient='records')
    return json_data
