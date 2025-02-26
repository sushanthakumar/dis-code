import sys
import os

CWD=os.path.dirname(os.path.abspath(__file__))
PWD = CWD
sys.path.append(CWD+"/../../pkg/discovery/connectors/dhcp")
from dhcp_connector import *
import pytest  

def test_removing_stale_info_from_lease_file_01():
    DHCP_LEASE_PATH = PWD+"/data/dhcp.lease"
    print("Lease file path = ", DHCP_LEASE_PATH)
    devices = parse_dhcp_leases(DHCP_LEASE_PATH)
    devices = remove_duplicates(devices)
    
    list(map(print, devices))
    # Get the length of entries having the same IP address: 192.168.10.152
    assert len([d for d in devices if d['ip'] == "192.168.10.152"]) == 1


def test_removing_stale_info_from_lease_file_02():
    DHCP_LEASE_PATH = PWD+"/data/dhcp_nohardware_address.lease"
    print("Lease file path = ", DHCP_LEASE_PATH)
    devices = parse_dhcp_leases(DHCP_LEASE_PATH)
    devices = remove_duplicates(devices)    
    list(map(print, devices))
    # Get the length of entries having the same IP address: 192.168.10.182
    assert len([d for d in devices if d['ip'] == "192.168.10.182"]) == 0

def test_removing_stale_info_from_lease_file_03():
    DHCP_LEASE_PATH = PWD+"/data/dhcp_one_hw_two_ips.lease"
    print("Lease file path = ", DHCP_LEASE_PATH)
    devices = parse_dhcp_leases(DHCP_LEASE_PATH)
    print(devices)
    devices = remove_duplicates(devices)
    
    list(map(print, devices))
    # Get the length of entries having the same HW address": 88:fc:5d:27:01:a0
    assert len([d for d in devices if d['mac'] == "88:fc:5d:27:01:a0"]) == 1


def test_parse_name_after_uid_04():
    DHCP_LEASE_PATH = PWD+"/data/dhcp_lease_after_uid.lease"
    print("Lease file path = ", DHCP_LEASE_PATH)
    devices = parse_dhcp_leases(DHCP_LEASE_PATH)
    for d in devices:
        print(d)
