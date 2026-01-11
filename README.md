# 🌐 HomeNetMonitor

Dashboard web per monitoraggio continuo della rete locale con rilevamento dispositivi e alert anomalie.

## 📋 Funzionalità

- ✅ Scansione automatica rete locale ogni 30 secondi
- ✅ Rilevamento dispositivi (IP, MAC, hostname)
- ✅ Dashboard web real-time con auto-refresh
- ✅ Alert visivi per dispositivi nuovi/sconosciuti
- ✅ Storico connessioni in database SQLite
- ✅ Stato online/offline dispositivi

## 🛠️ Tecnologie

- **Backend**: Python 3.10+
- **Scanning**: nmap, python-nmap
- **Web Framework**: Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript

## 📦 Installazione

### Prerequisiti
```bash
sudo apt update
sudo apt install python3.10-venv nmap
```

### Setup
```bash
# Clone repository
git clone https://github.com/torchiachristian/HomeNetMonitor.git
cd HomeNetMonitor

# Crea virtual environment
python3 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Inizializza database
python3 src/database.py
```

## 🚀 Utilizzo

### 1. Avvia il monitor di rete
```bash
sudo venv/bin/python3 src/monitor.py
```

**Nota**: Richiede `sudo` per accesso raw socket network scanning.

### 2. Avvia la dashboard (in un altro terminale)
```bash
cd ~/HomeNetMonitor
source venv/bin/activate
python3 src/app.py
```

### 3. Accedi alla dashboard

Apri il browser su: `http://localhost:5000`

## 📊 Dashboard

La dashboard mostra:

- **Statistiche**: Totale dispositivi, attivi ora, nuovi/sconosciuti
- **Tabella dispositivi**: IP, MAC, hostname, timestamp, stato
- **Alert visivi**: Dispositivi nuovi evidenziati in rosso
- **Auto-refresh**: Aggiornamento automatico ogni 10 secondi

## 🔧 Configurazione

### Modificare range IP

Modifica in `src/network_scanner.py`:
```python
def scan_network(network_range="192.168.1.0/24"):  # Cambia qui
```

### Modificare intervallo scansione

Modifica in `src/monitor.py`:
```python
monitor_loop(interval=30)  # Secondi tra scansioni
```

## 📁 Struttura Progetto
```
HomeNetMonitor/
├── src/
│   ├── app.py              # Flask application
│   ├── database.py         # Database management
│   ├── monitor.py          # Main monitoring loop
│   └── network_scanner.py  # Network scanning logic
├── templates/
│   └── dashboard.html      # Web dashboard
├── requirements.txt        # Python dependencies
└── README.md
```

## 🎓 Scopo Didattico

Progetto ITS che integra:
- Networking e scansione reti locali
- Database relazionali (SQLite)
- Web development (Flask + frontend)
- Cybersecurity base
- Monitoraggio real-time

## ⚠️ Note

- Testare solo sulla propria rete domestica
- Lo scanning richiede permessi amministrativi
- I dispositivi nuovi rimangono evidenziati fino a marcatura manuale come "noti"

## 📝 License

MIT License - Progetto didattico ITS

## 👨‍💻 Autore

Christian Torchia - [GitHub](https://github.com/torchiachristian)
