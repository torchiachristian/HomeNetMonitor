#!/usr/bin/env python3
import nmap
import time
from datetime import datetime

def scan_network(network_range="192.168.1.0/24"):
    """Scansiona la rete locale e restituisce lista dispositivi"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning network {network_range}...")
    
    nm = nmap.PortScanner()
    nm.scan(hosts=network_range, arguments='-sn')  # -sn = ping scan, no port scan
    
    devices = []
    for host in nm.all_hosts():
        device = {
            'ip': host,
            'mac': nm[host]['addresses'].get('mac', 'N/A'),
            'hostname': nm[host].get('hostnames', [{}])[0].get('name', 'Unknown'),
            'status': nm[host]['status']['state'],
            'timestamp': datetime.now().isoformat()
        }
        devices.append(device)
    
    print(f"Trovati {len(devices)} dispositivi")
    return devices

if __name__ == "__main__":
    print("=== Network Scanner Test ===")
    devices = scan_network()
    
    for device in devices:
        print(f"\nIP: {device['ip']}")
        print(f"  MAC: {device['mac']}")
        print(f"  Hostname: {device['hostname']}")
        print(f"  Status: {device['status']}")
