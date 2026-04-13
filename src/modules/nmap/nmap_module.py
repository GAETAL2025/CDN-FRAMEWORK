"""
Modulo Nmap: Integrazione con Nmap per scanning della rete
"""

import logging
from typing import Dict, Any
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Aggiungi src al path per import assoluti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor.executor import CommandExecutor

logger = logging.getLogger(__name__)


class NmapModule:
    """Modulo dedicato a Nmap"""

    SCAN_MODES = {
        "connect": "-sT",
        "syn": "-sS",
        "fast": "-F",
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
        "intense": "-T4 -A -v",
        "idle": "-sI",
        "ack": "-sA",
        "maimon": "-sM",
        "traceroute": "--traceroute"
    }

    TIMING_MODES = {
        "paranoid": "-T0",
        "sneaky": "-T1",
        "polite": "-T2",
        "normal": "-T3",
        "aggressive": "-T4",
        "insane": "-T5"
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
                "data": None,
                "error": "Nmap non disponibile. Installa con: sudo apt install nmap"
            }

        command = self._build_command(target, params)

        logger.info(f"Esecuzione scan Nmap su {target}")
        logger.info(f"Comando: {command}")

        stdout, stderr, return_code = self.executor.execute(command)
        success = return_code == 0

        if not success:
            return {
                "success": False,
                "data": None,
                "error": f"Scan fallito: {stderr.strip()}"
            }

        # Parse XML output
        try:
            parsed_data = self._parse_xml(stdout)
            return {
                "success": True,
                "data": parsed_data,
                "error": None
            }
        except Exception as e:
            logger.error(f"Errore parsing XML: {e}")
            return {
                "success": False,
                "data": None,
                "error": f"Errore parsing output: {str(e)}"
            }

    def _build_command(self, target: str, params: Dict[str, Any]) -> str:
        """Costruisce il comando Nmap con i parametri forniti"""
        cmd = [self.tool_name, "-oX", "-"]  # Always XML output

        scan_type = params.get("type", "connect").lower()  # Default to connect scan
        if scan_type in self.SCAN_MODES:
            cmd.append(self.SCAN_MODES[scan_type])
        else:
            # Permetti opzioni raw se l'utente inserisce stringhe personalizzate
            cmd.append(scan_type)

        if ports := params.get("ports"):
            cmd.append(f"-p {ports}")

        # Aggiungi timing
        timing = params.get("timing", "normal").lower()
        if timing in self.TIMING_MODES:
            cmd.append(self.TIMING_MODES[timing])

        # Aggiungi traceroute se richiesto
        if params.get("traceroute", False):
            cmd.append("--traceroute")

        if params.get("verbose", False):
            cmd.append("-v")

        if extra := params.get("extra"):
            cmd.append(extra)

        cmd.append(target)
        return " ".join(cmd)

    def _parse_xml(self, xml_output: str) -> Dict[str, Any]:
        """Parsa l'output XML di Nmap e restituisce dati strutturati"""
        root = ET.fromstring(xml_output)
        hosts = []

        for host in root.findall('host'):
            host_data = {"status": "unknown", "ports": []}

            # Stato host
            status_elem = host.find('status')
            if status_elem is not None:
                host_data["status"] = status_elem.get('state', 'unknown')

            # Porte
            ports_elem = host.find('ports')
            if ports_elem is not None:
                for port in ports_elem.findall('port'):
                    port_data = {
                        "port": int(port.get('portid', 0)),
                        "state": port.find('state').get('state', 'unknown') if port.find('state') is not None else 'unknown',
                        "service": port.find('service').get('name', 'unknown') if port.find('service') is not None else 'unknown'
                    }
                    host_data["ports"].append(port_data)

            hosts.append(host_data)

        # Per semplicità, assumiamo un singolo host
        if hosts:
            return hosts[0]
        else:
            return {"status": "down", "ports": []}

    def get_scan_modes(self) -> Dict[str, str]:
        """Restituisce le tipologie di scan supportate."""
        return {
            "connect": "Connect Scan - standard TCP (no root needed)",
            "syn": "SYN Scan - stealth, richiede root",
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
