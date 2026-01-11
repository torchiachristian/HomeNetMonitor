#!/usr/bin/env python3
from scapy.all import sniff, IP
from collections import defaultdict
from datetime import datetime
import threading
import time

class TrafficMonitor:
    def __init__(self):
        self.traffic_data = defaultdict(lambda: {'bytes_sent': 0, 'bytes_received': 0, 'packets': 0, 'last_updated': datetime.now()})
        self.monitoring = False
        self.monitor_thread = None
        
    def packet_handler(self, packet):
        """Gestisce ogni pacchetto catturato"""
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            packet_size = len(packet)
            
            # Traffico in uscita (source è nella nostra rete)
            if src_ip.startswith('192.168.'):
                self.traffic_data[src_ip]['bytes_sent'] += packet_size
                self.traffic_data[src_ip]['packets'] += 1
                self.traffic_data[src_ip]['last_updated'] = datetime.now()
            
            # Traffico in entrata (destination è nella nostra rete)
            if dst_ip.startswith('192.168.'):
                self.traffic_data[dst_ip]['bytes_received'] += packet_size
                self.traffic_data[dst_ip]['packets'] += 1
                self.traffic_data[dst_ip]['last_updated'] = datetime.now()
    
    def start_monitoring(self, interface=None):
        """Avvia il monitoraggio del traffico"""
        def monitor():
            print(f"[Traffic Monitor] Avviato su interface: {interface or 'default'}")
            try:
                sniff(prn=self.packet_handler, store=False, iface=interface)
            except Exception as e:
                print(f"[Traffic Monitor] Errore: {e}")
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
    
    def get_traffic_stats(self):
        """Restituisce statistiche traffico per tutti i dispositivi"""
        stats = {}
        for ip, data in self.traffic_data.items():
            stats[ip] = {
                'bytes_sent': data['bytes_sent'],
                'bytes_received': data['bytes_received'],
                'total_bytes': data['bytes_sent'] + data['bytes_received'],
                'packets': data['packets'],
                'last_updated': data['last_updated'].isoformat()
            }
        return stats
    
    def reset_stats(self):
        """Reset delle statistiche (per nuova finestra temporale)"""
        self.traffic_data.clear()

# Istanza globale
traffic_monitor = TrafficMonitor()

if __name__ == "__main__":
    print("=== Traffic Monitor Test ===")
    print("Avvio monitoraggio traffico per 30 secondi...")
    
    traffic_monitor.start_monitoring()
    time.sleep(30)
    
    print("\n=== Statistiche Traffico ===")
    stats = traffic_monitor.get_traffic_stats()
    for ip, data in stats.items():
        print(f"\nIP: {ip}")
        print(f"  Inviati: {data['bytes_sent']:,} bytes")
        print(f"  Ricevuti: {data['bytes_received']:,} bytes")
        print(f"  Totale: {data['total_bytes']:,} bytes")
        print(f"  Pacchetti: {data['packets']}")
