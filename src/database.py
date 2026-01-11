#!/usr/bin/env python3
import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'network_monitor.db')

def init_database():
    """Inizializza il database con le tabelle necessarie"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabella dispositivi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            mac TEXT,
            hostname TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_known BOOLEAN DEFAULT 0,
            UNIQUE(mac)
        )
    ''')
    
    # Tabella log connessioni
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS connection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            ip TEXT,
            status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database inizializzato: {DB_PATH}")

if __name__ == "__main__":
    init_database()
    print("Database creato con successo!")
