#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta
from database import DB_PATH

def detect_anomalies():
    """Rileva comportamenti anomali nei dispositivi"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    anomalies = []
    
    # 1. Traffico eccessivo improvviso (>100MB in 30 secondi)
    cursor.execute('''
        SELECT 
            d.ip, d.hostname, d.mac,
            SUM(t.bytes_sent + t.bytes_received) as total_bytes,
            MAX(t.timestamp) as last_seen
        FROM devices d
        JOIN traffic_stats t ON d.id = t.device_id
        WHERE t.timestamp > datetime('now', '-1 minute')
        GROUP BY d.id
        HAVING total_bytes > 104857600
    ''')
    
    for row in cursor.fetchall():
        anomalies.append({
            'type': 'HIGH_TRAFFIC',
            'ip': row[0],
            'hostname': row[1] or 'Unknown',
            'mac': row[2],
            'details': f"Traffico eccessivo: {row[3] / 1024 / 1024:.2f} MB in 1 minuto",
            'timestamp': row[4]
        })
    
    # 2. Connessioni a ore strane (02:00 - 06:00)
    current_hour = datetime.now().hour
    if 2 <= current_hour < 6:
        cursor.execute('''
            SELECT ip, hostname, mac, last_seen
            FROM devices
            WHERE last_seen > datetime('now', '-5 minutes')
        ''')
        
        for row in cursor.fetchall():
            anomalies.append({
                'type': 'ODD_HOURS',
                'ip': row[0],
                'hostname': row[1] or 'Unknown',
                'mac': row[2],
                'details': f"Attività rilevata alle {datetime.now().strftime('%H:%M')}",
                'timestamp': row[3]
            })
    
    # 3. Dispositivi nuovi connessi
    cursor.execute('''
        SELECT ip, hostname, mac, first_seen
        FROM devices
        WHERE is_known = 0 AND first_seen > datetime('now', '-10 minutes')
    ''')
    
    for row in cursor.fetchall():
        anomalies.append({
            'type': 'NEW_DEVICE',
            'ip': row[0],
            'hostname': row[1] or 'Unknown',
            'mac': row[2],
            'details': f"Nuovo dispositivo rilevato",
            'timestamp': row[3]
        })
    
    conn.close()
    return anomalies

def save_anomaly(anomaly):
    """Salva anomalia nel database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO anomalies (type, ip, mac, hostname, details, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (anomaly['type'], anomaly['ip'], anomaly['mac'], 
          anomaly['hostname'], anomaly['details'], datetime.now()))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("=== Anomaly Detector Test ===")
    anomalies = detect_anomalies()
    
    if anomalies:
        print(f"\n⚠️  Rilevate {len(anomalies)} anomalie:\n")
        for a in anomalies:
            print(f"[{a['type']}] {a['ip']} ({a['hostname']})")
            print(f"  {a['details']}\n")
    else:
        print("✓ Nessuna anomalia rilevata")
