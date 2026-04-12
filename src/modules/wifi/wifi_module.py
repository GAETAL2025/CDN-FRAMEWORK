"""
WiFi Module: ricerca interfacce WiFi e gestisce modalità managed/monitor.
"""

import logging
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Aggiungi src al path per import assoluti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor.executor import CommandExecutor

logger = logging.getLogger(__name__)


class WifiModule:
    """Modulo per gestione interfacce wireless."""

    def __init__(self, executor: CommandExecutor):
        self.executor = executor

    def list_interfaces(self) -> List[Dict[str, str]]:
        """Elenca le interfacce wireless disponibili."""
        stdout, stderr, return_code = self.executor.execute("iw dev", shell=True)
        interfaces: List[Dict[str, str]] = []
        current = None
        if return_code != 0:
            logger.error(f"Errore ottenendo interfacce wireless: {stderr}")
            return []

        for line in stdout.splitlines():
            line = line.strip()
            if line.startswith("Interface"):
                name = line.split()[1]
                current = {"name": name, "type": "unknown", "state": "unknown"}
                interfaces.append(current)
            elif line.startswith("type") and current is not None:
                current["type"] = line.split()[1]
            elif line.startswith("ssid") and current is not None:
                current["ssid"] = " ".join(line.split()[1:])

        return interfaces

    def get_interface_state(self, interface: str) -> str:
        """Restituisce lo stato operativo dell'interfaccia."""
        stdout, stderr, return_code = self.executor.execute(f"ip link show {interface}", shell=True)
        if return_code != 0:
            return "unknown"
        return "UP" if "state UP" in stdout else "DOWN"

    def get_interfaces_summary(self) -> List[Dict[str, str]]:
        """Restituisce un sommario delle interfacce WiFi."""
        interfaces = self.list_interfaces()
        for entry in interfaces:
            entry["state"] = self.get_interface_state(entry["name"])
        return interfaces

    def set_mode(self, interface: str, mode: str) -> Dict[str, str]:
        """Cambia la modalità dell'interfaccia WiFi tra managed e monitor."""
        if mode not in ["monitor", "managed"]:
            return {"success": False, "error": "Modalità non valida", "output": ""}

        # Preferiamo airmon-ng se presente
        if self.executor.check_command_exists("airmon-ng"):
            action = "start" if mode == "monitor" else "stop"
            cmd = f"sudo airmon-ng {action} {interface}"
            return self._run_command(cmd)

        if mode == "monitor":
            cmd = f"sudo ip link set {interface} down && sudo iw dev {interface} set type monitor && sudo ip link set {interface} up"
        else:
            cmd = f"sudo ip link set {interface} down && sudo iw dev {interface} set type managed && sudo ip link set {interface} up"
        return self._run_command(cmd)

    def _run_command(self, command: str) -> Dict[str, str]:
        stdout, stderr, return_code = self.executor.execute(command, timeout=60)
        return {
            "command": command,
            "output": stdout.strip(),
            "error": stderr.strip(),
            "success": return_code == 0,
            "return_code": return_code
        }
