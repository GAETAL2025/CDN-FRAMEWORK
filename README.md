# 🔧 NetHunterCDN

**NetHunterCDN** è uno strumento modulare per network reconnaissance con interfaccia **CLI** e **TUI (Text User Interface)** professionale nel terminale, tipo Metasploit. Esegue tool come Nmap e organizza i risultati in modo strutturato.

## 🎯 Caratteristiche Principali

- ✅ **CLI moderna** - Comandi semplici e intuitivi
- ✅ **TUI nel Terminale** - Interfaccia interattiva rosso/nero
- ✅ **Modulo Nmap integrato** - Scan real-time con molte opzioni
- ✅ **Aircrack-ng suite** - `airmon-ng`, `airodump-ng`, `aireplay-ng`, `aircrack-ng`
- ✅ **Gestione WiFi** - lista interfacce e switch managed/monitor
- ✅ **Auto-update Git** - controlla e applica gli aggiornamenti da `origin/main`
- ✅ **Executor universale** - Per qualsiasi comando shell
- ✅ **Logging completo** - Debug e monitoring
- ✅ **Architettura modulare** - Facile aggiungere nuovi tool

## 📋 Milestone Completata (Fase 1-10)

- ✅ **FASE 1**: Entry point + input da terminale
- ✅ **FASE 2**: Command system (CLI) - scan, wifi, help
- ✅ **FASE 3**: Executor robusto con timeout e gestione errori
- ✅ **FASE 4**: Modulo Nmap con XML parsing e output strutturato
- ✅ **FASE 5**: WiFi scan con airodump-ng e CSV parsing
- ✅ **FASE 6**: WiFi capture handshake con airodump-ng + aireplay-ng
- ✅ **FASE 7**: WiFi cracking WPA/WPA2 con aircrack-ng
- ✅ **FASE 8**: Architettura modulare, output standardizzato, validazione input
- ✅ **FASE 9**: TUI MSF-like completa (rosso/nero, comandi testuali, banner ASCII)
- ✅ **FASE 10**: Test esteso e documentazione aggiornata

## 🚀 Utilizzo Rapido

### Scan Nmap
```bash
python3 main.py scan 192.168.1.1
python3 main.py scan example.com -type fast
```

### WiFi Operations
```bash
# Lista interfacce
python3 main.py wifi list

# Scan reti WiFi
python3 main.py wifi scan -interface wlan0 -duration 10

# Cattura handshake
python3 main.py wifi-capture 00:11:22:33:44:55 -channel 6 -interface wlan0mon

# Cracca password
python3 main.py wifi-crack capture.cap 00:11:22:33:44:55 -wordlist rockyou.txt
```
- 📋 **FASE 9**: Test esteso
- 📋 **FASE 10**: Modulo WiFi (Aircrack-ng)

## 🚀 Installazione

### Requisiti
- Python 3.8+
- Nmap (per il modulo scan)
- rich (per TUI)

### Setup
```bash
cd /home/ghost/Scrivania/CDN-FRAMEWORK

# Installa Nmap
sudo apt install nmap

# Installa dipendenze Python
pip install -r requirements.txt

# Test di verifica
python3 test.py

# Avvia TUI (richiede sudo)
sudo python3 tui_simple.py
```

## 📖 Utilizzo

### 🖥️ TUI (Terminal UI - CONSIGLIATO)

Interfaccia interattiva professionale direttamente nel terminale, **tipo Metasploit** con comandi testuali.

```bash
sudo python3 tui_simple.py
```

**Features**:
- 🎯 **Prompt MSF-like**: `nhcdn >` con contesto moduli
- 🔴 **Grafica rosso/nero** - Tema professionale
- 📋 **Comandi testuali** - `use`, `show`, `set`, `run`
- 🎨 **Banner ASCII art** - Versione, autore, piattaforma
- ⚡ **Auto-update** - Controllo aggiornamenti Git
- 🔒 **Root check** - Verifica privilegi sudo

**Comandi principali**:
- `help` - Mostra aiuto comandi
- `version` - Versione del tool
- `banner` - Ristampa il banner
- `clear` - Pulisce il terminale
- `clean` - Cancella log, cap, csv salvati
- `use <module>` - Carica modulo (nmap/scan, wifi/scan, wifi/capture, wifi/crack)
- `show modules` - Lista moduli disponibili
- `show options` - Opzioni modulo corrente
- `set <option> <value>` - Imposta parametro
- `run` - Esegue modulo caricato
- `back` - Torna al contesto principale
- `scan <target>` - Scan Nmap veloce
- `wifi scan` - Scan reti WiFi
- `exit` - Esci dalla console

**Tipi Nmap disponibili**:
- **Scan Types:** connect, syn, fin, null, xmas, udp, idle, ack, maimon, fast, aggressive, traceroute
- **Timing:** paranoid, sneaky, polite, normal, aggressive, insane
- **Opzioni:** ports (porte specifiche), traceroute (yes/no)

**Esempio sessione**:
```
nhcdn > use nmap/scan
nhcdn (nmap/scan) > show options
nhcdn (nmap/scan) > set target 192.168.1.1
nhcdn (nmap/scan) > set type aggressive
nhcdn (nmap/scan) > set timing insane
nhcdn (nmap/scan) > set traceroute yes
nhcdn (nmap/scan) > run
nhcdn (nmap/scan) > back
nhcdn > clear
nhcdn > clean
nhcdn > exit
```
- `6` - Help
- `7` - Exit

### 💻 Interfaccia CLI (Linea di Comando)

Per chi preferisce il terminale:

```bash
# Aiuto
sudo python3 main.py help

# Versione
sudo python3 main.py version

# Scan base
sudo python3 main.py scan 192.168.1.1

# Scan con porte specifiche
sudo python3 main.py scan 192.168.1.1 -ports 22,80,443

# Scan SYN (veloce, richiede sudo)
sudo python3 main.py scan 192.168.1.1 -type syn

# Scan con verbose
sudo python3 main.py scan 192.168.1.1 -verbose

# Scan completo
sudo python3 main.py scan 192.168.1.1 -type syn -ports 1-65535 -verbose

# WiFi list
sudo python3 main.py wifi list

# Switch WiFi monitor
sudo python3 main.py wifi mode wlan0 -mode monitor

# Avvia monitor mode con airmon-ng
sudo python3 main.py airmon start wlan0

# Esegui airodump-ng
sudo python3 main.py airodump wlan0 -output capture

# Esegui aireplay-ng deauth
sudo python3 main.py aireplay deauth wlan0 -target AA:BB:CC:DD:EE:FF -count 10

# Esegui aircrack-ng
sudo python3 main.py aircrack capture.cap -wordlist wordlist.txt
```

## 🏗️ Struttura del Progetto

```
CDN-FRAMEWORK/
├── main.py                      # CLI Entry point
├── tui_simple.py                # TUI Menu-based (CONSIGLIATO!) ⭐
├── tui.py                       # TUI Full interactive (legacy)
├── test.py                      # Suite di test (6 test)
├── PUSH.sh                      # Script push GitHub
├── QUICKSTART.sh                # Quick start guide
├── README.md                    # Documentazione
├── MILESTONE.md                 # Report milestone
├── CONTRIBUTING.md              # Linee guida dev
├── requirements.txt             # Dipendenze
├── .gitignore                   # Git ignore
├── .gitattributes               # Git attributes
└── src/
    ├── __init__.py
    ├── cli/
    │   ├── __init__.py
    │   └── commands.py          # Parser CLI e gestione comandi
    ├── executor/
    │   ├── __init__.py
    │   └── executor.py          # Executor comandi shell
    ├── modules/
    │   ├── __init__.py
    │   ├── update/
    │   │   ├── __init__.py
    │   │   └── update_module.py # Auto-update Git
    │   ├── nmap/
    │   │   ├── __init__.py
    │   │   └── nmap_module.py   # Integrazione Nmap
    │   ├── wifi/
    │   │   ├── __init__.py
    │   │   └── wifi_module.py   # Gestione interfacce WiFi
    │   └── aircrack/
    │       ├── __init__.py
    │       └── aircrack_module.py # Suite Aircrack-ng
    └── config/
        ├── __init__.py
        └── logger.py            # Logger centralizzato
```

## 🔍 Componenti Principali

### 1. **Executor** (`src/executor/executor.py`)
Ponte tra il framework e i tool di sistema.
- Esegue comandi shell
- Cattura stdout/stderr
- Gestisce timeouts e errori
- Verifica disponibilità di comandi

### 2. **CLI Parser** (`src/cli/commands.py`)
Interpreta argomenti da terminale.
- Registra comandi disponibili
- Valida input
- Estrae parametri
- Gestisce help

### 3. **Nmap Module** (`src/modules/nmap/nmap_module.py`)
Integrazione specializzata con Nmap.
- Costruisce comandi Nmap
- Supporta tipi di scan: SYN, Connect, Ping, UDP, FIN, NULL, XMAS, Version, OS, Aggressive, Quick, Intense
- Gestisce output formato testo e XML
- Verifica disponibilità tool

### 4. **WiFi Module** (`src/modules/wifi/wifi_module.py`)
Gestione interfacce wireless.
- Elenca interfacce WiFi
- Mostra stato interfaccia
- Cambia modalità managed/monitor

### 5. **Aircrack Module** (`src/modules/aircrack/aircrack_module.py`)
Suite Aircrack-ng integrata.
- Avvia/arresta `airmon-ng`
- Esegue `airodump-ng`
- Esegue `aireplay-ng`
- Esegue `aircrack-ng`

### 6. **Update Module** (`src/modules/update/update_module.py`)
Auto-update dal repository Git.
- Controlla `origin/main` all'avvio
- Esegue `git pull --ff-only`
- Riavvia automaticamente dopo l'aggiornamento

### 7. **Logger** (`src/config/logger.py`)
Sistema di logging centralizzato.
- Log a console
- Log a file
- Livelli configurabili (DEBUG, INFO, WARNING, ERROR)

## 🧪 Test

Esegui la suite di test:

```bash
python3 test.py
```

Test inclusi:
1. Executor - esecuzione comandi
2. CLI Parser - parsing argomenti
3. Nmap Command Building - costruzione comando
4. Nmap Availability - verifica installazione
5. Help Command - sistema di aiuto
6. Invalid Input - gestione errori

## 📝 Esempi Avanzati

### Scan completo con output strutturato
```bash
python3 main.py scan 192.168.1.1 -type syn -ports 1-1000 -verbose
```

### Scan di una rete
```bash
python3 main.py scan 192.168.1.0/24 -type ping
```

## 🐙 GitHub - Push Repository

Repository è stato inizializzato localmente e pronto per il push.

**Remote configurato**:
```
https://github.com/GAETAL2025/CDN-FRAMEWORK.git
```

**Per fare il push**:

Esegui uno di questi comandi (dipende dal tuo metodo di autenticazione):

### Opzione 1: SSH (Consigliato)
```bash
# Genera chiave SSH (se non l'hai già)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Aggiungi public key su GitHub
# https://github.com/settings/keys

# Cambia remote a SSH
git remote set-url origin git@github.com:GAETAL2025/CDN-FRAMEWORK.git

# Push
git push -u origin master
```

### Opzione 2: HTTPS + Token
```bash
# Genera Personal Access Token
# https://github.com/settings/tokens

# Push (chiederà username e token)
git push -u origin master

# Username: GAETAL2025
# Password: <tuo-token>
```

### Opzione 3: Credenziali memorizzate
```bash
# Configura git per memorizzare credenziali
git config --global credential.helper store

# Prima push chiederà credenziali (saranno salvate)
git push -u origin master
```

**Script automatico**:
```bash
bash PUSH.sh
```

Per aggiungere un nuovo modulo:

1. Crea cartella `src/modules/newtool/`
2. Implementa classe con metodo `check_available()` e `execute()`
3. Registra nel `main.py`
4. Aggiungi test

Esempio:
```python
# src/modules/newtool/module.py
from ..executor.executor import CommandExecutor

class NewToolModule:
    def __init__(self, executor: CommandExecutor):
        self.executor = executor
    
    def check_available(self) -> bool:
        return self.executor.check_command_exists("newtool")
    
    def execute(self, target: str, params: dict) -> dict:
        cmd = self._build_command(target, params)
        stdout, stderr, code = self.executor.execute(cmd)
        return {"success": code == 0, "output": stdout}
```

## 🎯 Prossimi Step

1. **FASE 5**: Parsing XML per output strutturato
2. **FASE 6**: Architettura modulare multi-tool
3. **FASE 7**: Logging esteso a file
4. **FASE 8**: Validazione dipendenze
5. **FASE 9**: Test suite completa
6. **FASE 10**: Modulo WiFi (Aircrack-ng)

## 💡 Note di Sviluppo

- Mantieni ogni modulo indipendente
- Non toccare l'executor se aggiungi nuovi tool
- Usa il logger per debug
- Testa prima con help/version

## 📄 Licenza

MIT

## 📧 Support

Per problemi o suggerimenti relativamente alle fasi successive, contatta lo sviluppatore.

---

**CDN-FRAMEWORK v1.0.0** - Network reconnaissance framework modulare
