#!/usr/bin/env python3
import sqlite3
import time
from datetime import datetime
from network_scanner import scan_network
from database import DB_PATH

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

def monitor_loop(interval=30):
    """Loop principale di monitoraggio"""
    print("=== Network Monitor Avviato ===")
    print(f"Scansione ogni {interval} secondi")
    print("Premi Ctrl+C per fermare\n")
    
    try:
        while True:
            devices = scan_network()
            save_devices(devices)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Scansione completata. In attesa...\n")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nMonitor fermato dall'utente")

if __name__ == "__main__":
    monitor_loop()
