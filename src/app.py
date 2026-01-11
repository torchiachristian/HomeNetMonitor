#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime, timedelta
from database import DB_PATH

app = Flask(__name__, template_folder='../templates', static_folder='../static')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/devices')
def get_devices():
    """Restituisce tutti i dispositivi attivi nelle ultime 24h"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Dispositivi visti nelle ultime 24 ore
    time_24h_ago = datetime.now() - timedelta(hours=24)
    
    cursor.execute('''
        SELECT ip, mac, hostname, first_seen, last_seen, is_known
        FROM devices
        WHERE last_seen > ?
        ORDER BY last_seen DESC
    ''', (time_24h_ago,))
    
    devices = []
    for row in cursor.fetchall():
        devices.append({
            'ip': row['ip'],
            'mac': row['mac'],
            'hostname': row['hostname'],
            'first_seen': row['first_seen'],
            'last_seen': row['last_seen'],
            'is_known': bool(row['is_known'])
        })
    
    conn.close()
    return jsonify(devices)

@app.route('/api/stats')
def get_stats():
    """Statistiche generali"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Totale dispositivi
    cursor.execute('SELECT COUNT(*) as total FROM devices')
    total = cursor.fetchone()['total']
    
    # Dispositivi attivi ora (ultimi 5 minuti)
    time_5min_ago = datetime.now() - timedelta(minutes=5)
    cursor.execute('SELECT COUNT(*) as active FROM devices WHERE last_seen > ?', (time_5min_ago,))
    active = cursor.fetchone()['active']
    
    # Nuovi dispositivi (is_known = 0)
    cursor.execute('SELECT COUNT(*) as new FROM devices WHERE is_known = 0')
    new_devices = cursor.fetchone()['new']
    
    conn.close()
    
    return jsonify({
        'total': total,
        'active': active,
        'new': new_devices
    })

@app.route('/api/mark_known/<mac>', methods=['POST'])
def mark_known(mac):
    """Marca un dispositivo come conosciuto"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE devices SET is_known = 1 WHERE mac = ?', (mac,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/traffic')
def get_traffic():
    """Restituisce statistiche traffico per dispositivo"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Traffico aggregato per IP nelle ultime 24h
    cursor.execute('''
        SELECT 
            d.ip,
            d.mac,
            d.hostname,
            SUM(t.bytes_sent) as total_sent,
            SUM(t.bytes_received) as total_received,
            SUM(t.packets) as total_packets,
            MAX(t.timestamp) as last_update
        FROM devices d
        LEFT JOIN traffic_stats t ON d.id = t.device_id
        WHERE t.timestamp > datetime('now', '-24 hours')
        GROUP BY d.ip
        ORDER BY (total_sent + total_received) DESC
    ''')
    
    traffic = []
    for row in cursor.fetchall():
        if row['total_sent'] is not None:
            traffic.append({
                'ip': row['ip'],
                'mac': row['mac'],
                'hostname': row['hostname'],
                'bytes_sent': row['total_sent'],
                'bytes_received': row['total_received'],
                'total_bytes': row['total_sent'] + row['total_received'],
                'packets': row['total_packets'],
                'last_update': row['last_update']
            })
    
    conn.close()
    return jsonify(traffic)

@app.route('/api/timeline')
def get_timeline():
    """Restituisce timeline connessioni ultimi 7 giorni"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Connessioni per giorno negli ultimi 7 giorni
    cursor.execute('''
        SELECT 
            DATE(timestamp) as date,
            COUNT(DISTINCT device_id) as device_count
        FROM connection_logs
        WHERE timestamp > datetime('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    ''')
    
    timeline = []
    for row in cursor.fetchall():
        timeline.append({
            'date': row['date'],
            'count': row['device_count']
        })
    
    conn.close()
    return jsonify(timeline)

@app.route('/api/anomalies')
def get_anomalies():
    """Restituisce anomalie recenti (ultime 24h)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT type, ip, mac, hostname, details, timestamp, acknowledged
        FROM anomalies
        WHERE timestamp > datetime('now', '-24 hours')
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    
    anomalies = []
    for row in cursor.fetchall():
        anomalies.append({
            'type': row['type'],
            'ip': row['ip'],
            'mac': row['mac'],
            'hostname': row['hostname'],
            'details': row['details'],
            'timestamp': row['timestamp'],
            'acknowledged': bool(row['acknowledged'])
        })
    
    conn.close()
    return jsonify(anomalies)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
