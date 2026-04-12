"""
Modulo Nmap: Integrazione con Nmap per scanning della rete
"""

import logging
from typing import Dict, Any
import sys
from pathlib import Path

# Aggiungi src al path per import assoluti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor.executor import CommandExecutor

logger = logging.getLogger(__name__)


class NmapModule:
    """Modulo dedicato a Nmap"""

    SCAN_MODES = {
        "syn": "-sS",
        "connect": "-sT",
        "ping": "-sn",
        "udp": "-sU",
        "fin": "-sF",
        "null": "-sN",
        "xmas": "-sX",
        "version": "-sV",
        "os": "-O",
        "stealth": "-sS",
        "aggressive": "-A",
        "quick": "-T4 -F",
        "intense": "-T4 -A -v"
    }

    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.tool_name = "nmap"

    def check_available(self) -> bool:
        """Verifica se Nmap è installato"""
        if self.executor.check_command_exists(self.tool_name):
            logger.info("Nmap è disponibile sul sistema")
            return True
        else:
            logger.error("Nmap non trovato! Installa con: sudo apt install nmap")
            return False

    def scan(self, target: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Esegue uno scan con Nmap
        """
        if not self.check_available():
            return {
                "success": False,
                "error": "Nmap non disponibile",
                "output": ""
            }

        command = self._build_command(target, params)

        logger.info(f"Esecuzione scan Nmap su {target}")
        logger.info(f"Comando: {command}")

        stdout, stderr, return_code = self.executor.execute(command)
        success = return_code == 0

        return {
            "success": success,
            "target": target,
            "command": command,
            "output": stdout.strip(),
            "error": stderr.strip() if not success else "",
            "return_code": return_code
        }

    def _build_command(self, target: str, params: Dict[str, Any]) -> str:
        """Costruisce il comando Nmap con i parametri forniti"""
        cmd = [self.tool_name]

        scan_type = params.get("type", "syn").lower()
        if scan_type in self.SCAN_MODES:
            cmd.append(self.SCAN_MODES[scan_type])
        else:
            # Permetti opzioni raw se l'utente inserisce stringhe personalizzate
            cmd.append(scan_type)

        if ports := params.get("ports"):
            cmd.append(f"-p {ports}")

        output_format = params.get("output_format", "text").lower()
        if output_format == "xml":
            cmd.append("-oX -")

        if params.get("verbose", False):
            cmd.append("-v")

        if extra := params.get("extra"):
            cmd.append(extra)

        cmd.append(target)
        return " ".join(cmd)

    def get_scan_modes(self) -> Dict[str, str]:
        """Restituisce le tipologie di scan supportate."""
        return {
            "syn": "SYN Scan - stealth, richiede root",
            "connect": "Connect Scan - standard TCP",
            "ping": "Ping Scan - host discovery",
            "udp": "UDP Scan - verifica porte UDP",
            "fin": "FIN Scan - stealth su TCP",
            "null": "NULL Scan - stealth su TCP",
            "xmas": "XMAS Scan - stealth su TCP",
            "version": "Version Detection - -sV",
            "os": "OS Detection - -O",
            "stealth": "Stealth Scan - alias SYN",
            "aggressive": "Aggressive Scan - -A completo",
            "quick": "Quick Scan - -T4 -F veloce",
            "intense": "Intense Scan - -T4 -A -v dettagliato"
        }

    def get_info(self) -> Dict[str, str]:
        """Restituisce info sul modulo"""
        return {
            "name": "Nmap Module",
            "description": "Integrazione con Nmap per network scanning",
            "version": "1.1.0",
            "dependencies": ["nmap"]
        }
