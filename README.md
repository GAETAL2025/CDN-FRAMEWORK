# 🔧 CDN-FRAMEWORK

**CDN-FRAMEWORK** è uno strumento modulare per network reconnaissance. Esegue tool come Nmap e organizza i risultati in modo strutturato.

## 📋 Roadmap (Milestone Completate)

- ✅ **FASE 1**: Entry point + input da terminale
- ✅ **FASE 2**: Command system (CLI) - scan, wifi, help
- ✅ **FASE 3**: Executor - esecuzione comandi shell
- ✅ **FASE 4**: Modulo Nmap reale + output grezzo

### In sviluppo (Prossime fasi):
- 📋 **FASE 5**: Parsing XML
- 📋 **FASE 6**: Architettura modulare avanzata
- 📋 **FASE 7**: Logging completo
- 📋 **FASE 8**: Controllo dipendenze
- 📋 **FASE 9**: Test esteso
- 📋 **FASE 10**: Modulo WiFi (Aircrack-ng)

## 🚀 Installazione

### Requisiti
- Python 3.8+
- Nmap (facoltativo, per il modulo scan)

### Setup
```bash
cd /home/ghost/Scrivania/CDN-FRAMEWORK

# Installa Nmap (opzionale)
sudo apt install nmap

# Test di verifica
python3 test.py
```

## 📖 Utilizzo

### Comando di aiuto
```bash
python3 main.py help
```

### Scan Nmap
```bash
# Scan base
python3 main.py scan 192.168.1.1

# Scan con porte specifiche
python3 main.py scan 192.168.1.1 -ports 22,80,443

# Scan SYN (più accurato)
python3 main.py scan 192.168.1.1 -type syn

# Scan con verbose
python3 main.py scan 192.168.1.1 -verbose

# Scan completo con output XML
python3 main.py scan 192.168.1.1 -type syn -ports 1-65535 -verbose
```

### Versione
```bash
python3 main.py version
```

## 🏗️ Struttura del Progetto

```
CDN-FRAMEWORK/
├── main.py                      # Entry point principale
├── test.py                      # Suite di test
├── README.md                    # Questo file
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
    │   └── nmap/
    │       ├── __init__.py
    │       └── nmap_module.py   # Integrazione Nmap
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
- Supporta tipi di scan (SYN, Connect, Ping)
- Gestisce output formato testo e XML
- Verifica disponibilità tool

### 4. **Logger** (`src/config/logger.py`)
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

## 🔧 Sviluppo Locale

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
