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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
