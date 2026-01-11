#!/usr/bin/env python3
print("DEBUG: Script avviato")
import sqlite3
import time
from traffic_monitor import traffic_monitor
from datetime import datetime
from network_scanner import scan_network
from database import DB_PATH
from traffic_monitor import traffic_monitor
from anomaly_detector import detect_anomalies, save_anomaly
print("DEBUG: Import traffic_monitor OK")
from datetime import datetime
print("DEBUG: Import datetime OK")
from network_scanner import scan_network
print("DEBUG: Import network_scanner OK")
from database import DB_PATH
print("DEBUG: Import database OK")

def save_devices(devices):
    """Salva i dispositivi trovati nel database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for device in devices:
        # Controlla se il dispositivo esiste già (by MAC)
        if device['mac'] != 'N/A':
            cursor.execute('SELECT id, is_known FROM devices WHERE mac = ?', (device['mac'],))
            result = cursor.fetchone()
            
            if result:
                # Dispositivo esistente - aggiorna last_seen
                device_id = result[0]
                cursor.execute('''
                    UPDATE devices 
                    SET last_seen = ?, ip = ?, hostname = ?
                    WHERE id = ?
                ''', (datetime.now(), device['ip'], device['hostname'], device_id))
            else:
                # Nuovo dispositivo
                cursor.execute('''
                    INSERT INTO devices (ip, mac, hostname, is_known)
                    VALUES (?, ?, ?, 0)
                ''', (device['ip'], device['mac'], device['hostname']))
                device_id = cursor.lastrowid
                print(f"⚠️  NUOVO DISPOSITIVO RILEVATO: {device['ip']} - {device['mac']}")
            
            # Log connessione
            cursor.execute('''
                INSERT INTO connection_logs (device_id, ip, status)
                VALUES (?, ?, ?)
            ''', (device_id, device['ip'], device['status']))
    
    conn.commit()
    conn.close()
def save_traffic_stats():
    """Salva statistiche traffico nel database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stats = traffic_monitor.get_traffic_stats()
    
    for ip, data in stats.items():
        # Trova device_id dal MAC o IP
        cursor.execute('SELECT id FROM devices WHERE ip = ?', (ip,))
        result = cursor.fetchone()
        
        if result:
            device_id = result[0]
            cursor.execute('''
                INSERT INTO traffic_stats (device_id, ip, bytes_sent, bytes_received, packets, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (device_id, ip, data['bytes_sent'], data['bytes_received'], data['packets'], datetime.now()))
    
    conn.commit()
    conn.close()

def monitor_loop(interval=30):
    """Loop principale di monitoraggio"""
    print("=== Network Monitor Avviato ===")
    print(f"Scansione ogni {interval} secondi")
    print("Avvio traffic monitoring...")
    
    # Avvia traffic monitor in background
    traffic_monitor.start_monitoring()
    
    print("Premi Ctrl+C per fermare\n")
    
    try:
        while True:
            devices = scan_network()
            save_devices(devices)
            save_traffic_stats()
            
            # Rileva anomalie
            anomalies = detect_anomalies()
            if anomalies:
                print(f"\n⚠️  ALERT: Rilevate {len(anomalies)} anomalie!")
                for anomaly in anomalies:
                    print(f"  [{anomaly['type']}] {anomaly['ip']} - {anomaly['details']}")
                    save_anomaly(anomaly)
                print()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Scansione completata. In attesa...\n")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nMonitor fermato dall'utente")

if __name__ == "__main__":
    monitor_loop()
