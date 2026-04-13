"""
WiFi Scan Module: Utilizzo di airodump-ng per scanning reti WiFi
"""

import logging
from typing import Dict, Any, List
import sys
import time
import os
from pathlib import Path

# Aggiungi src al path per import assoluti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor.executor import CommandExecutor

logger = logging.getLogger(__name__)


class WifiScanModule:
    """Modulo per scanning reti WiFi con airodump-ng"""

    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.tool_name = "airodump-ng"

    def check_available(self) -> bool:
        """Verifica se airodump-ng è installato"""
        if self.executor.check_command_exists(self.tool_name):
            logger.info("airodump-ng è disponibile")
            return True
        else:
            logger.error("airodump-ng non trovato! Installa con: sudo apt install aircrack-ng")
            return False

    def scan(self, interface: str, duration: int = 10) -> Dict[str, Any]:
        """
        Esegue uno scan delle reti WiFi visibili
        """
        if not self.check_available():
            return {
                "success": False,
                "data": None,
                "error": "airodump-ng non disponibile. Installa con: sudo apt install aircrack-ng"
            }

        # Verifica che l'interfaccia sia in modalità monitor
        if not self._is_monitor_mode(interface):
            return {
                "success": False,
                "data": None,
                "error": f"Interfaccia {interface} non è in modalità monitor. Usa 'airmon start {interface}'"
            }

        # File temporaneo per output
        output_file = f"/tmp/wifi_scan_{int(time.time())}.csv"

        try:
            # Comando airodump-ng
            command = f"{self.tool_name} {interface} --output-format csv -w /tmp/wifi_scan --write-interval 1"
            logger.info(f"Esecuzione scan WiFi su {interface}")
            logger.info(f"Comando: {command}")

            # Esegui in background per duration secondi
            # Per semplicità, esegui sincrono con timeout
            stdout, stderr, return_code = self.executor.execute(command, timeout=duration)

            # Leggi il file CSV generato
            csv_file = f"/tmp/wifi_scan-01.csv"
            if os.path.exists(csv_file):
                networks = self._parse_csv(csv_file)
                # Pulisci file temporanei
                self._cleanup_temp_files("/tmp/wifi_scan")
                return {
                    "success": True,
                    "data": {"networks": networks},
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": "Nessun file di output generato"
                }

        except Exception as e:
            logger.error(f"Errore durante scan WiFi: {e}")
            self._cleanup_temp_files("/tmp/wifi_scan")
            return {
                "success": False,
                "data": None,
                "error": f"Errore scan: {str(e)}"
            }

    def _is_monitor_mode(self, interface: str) -> bool:
        """Verifica se l'interfaccia è in modalità monitor"""
        stdout, stderr, return_code = self.executor.execute(f"iw dev {interface} info", shell=True)
        return "monitor" in stdout.lower()

    def _parse_csv(self, csv_file: str) -> List[Dict[str, Any]]:
        """Parsa il file CSV generato da airodump-ng"""
        networks = []
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Salta header
            in_networks = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("BSSID"):
                    in_networks = True
                    continue
                if in_networks and "," in line:
                    parts = line.split(",")
                    if len(parts) >= 14:
                        network = {
                            "bssid": parts[0].strip(),
                            "first_time_seen": parts[1].strip(),
                            "last_time_seen": parts[2].strip(),
                            "channel": parts[3].strip(),
                            "speed": parts[4].strip(),
                            "privacy": parts[5].strip(),
                            "cipher": parts[6].strip(),
                            "authentication": parts[7].strip(),
                            "power": parts[8].strip(),
                            "beacons": parts[9].strip(),
                            "iv": parts[10].strip(),
                            "lan_ip": parts[11].strip(),
                            "id_length": parts[12].strip(),
                            "essid": parts[13].strip() if len(parts) > 13 else "",
                            "key": parts[14].strip() if len(parts) > 14 else ""
                        }
                        networks.append(network)
        except Exception as e:
            logger.error(f"Errore parsing CSV: {e}")

        return networks

    def _cleanup_temp_files(self, prefix: str):
        """Pulisce file temporanei"""
        import glob
        for f in glob.glob(f"{prefix}*"):
            try:
                os.remove(f)
            except:
                pass