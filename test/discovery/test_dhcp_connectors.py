

import sys
import os

CWD=os.path.dirname(os.path.abspath(__file__))
PWD = CWD
sys.path.append(CWD+"/../../pkg/discovery/connectors/dhcp")
from dhcp_connector import *
import pytest  

def test_removing_stale_info_from_lease_file_01():
    pass