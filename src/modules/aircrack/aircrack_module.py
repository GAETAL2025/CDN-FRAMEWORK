"""
Aircrack Module: integra aircrack-ng, airmon-ng, aireplay-ng e airodump-ng.
"""

import logging
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Aggiungi src al path per import assoluti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor.executor import CommandExecutor

logger = logging.getLogger(__name__)


class AircrackModule:
    """Modulo per i tool della suite Aircrack-ng."""

    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.tools = ["airmon-ng", "aircrack-ng", "aireplay-ng", "airodump-ng"]

    def check_available(self, tool: Optional[str] = None) -> bool:
        """Verifica se i tool richiesti sono disponibili."""
        if tool:
            return self.executor.check_command_exists(tool)

        available = True
        for tool_name in self.tools:
            if not self.executor.check_command_exists(tool_name):
                logger.warning(f"Tool non trovato: {tool_name}")
                available = False
        return available

    def run_airmon(self, interface: str, action: str) -> Dict[str, str]:
        """Avvia o arresta la modalità monitor su una interfaccia."""
        if action == "start":
            cmd = f"sudo airmon-ng start {interface}"
        else:
            cmd = f"sudo airmon-ng stop {interface}"
        return self._run_command(cmd)

    def run_airodump(self, interface: str, output_prefix: Optional[str] = None, extra: Optional[str] = None) -> Dict[str, str]:
        """Esegue airodump-ng su una interfaccia."""
        cmd = f"sudo airodump-ng {interface}"
        if output_prefix:
            cmd += f" --output-format csv --write {output_prefix}"
        if extra:
            cmd += f" {extra}"
        return self._run_command(cmd)

    def run_aireplay(self, interface: str, attack: str, target: Optional[str] = None, count: int = 10, extra: Optional[str] = None) -> Dict[str, str]:
        """Esegue aireplay-ng con l'attacco selezionato."""
        cmd = f"sudo aireplay-ng --{attack} {interface}"
        if target:
            cmd += f" --deauth {count} -a {target}"
        if extra:
            cmd += f" {extra}"
        return self._run_command(cmd)

    def run_aircrack(self, capture_file: str, wordlist: Optional[str] = None, extra: Optional[str] = None) -> Dict[str, str]:
        """Esegue aircrack-ng su un file di cattura."""
        cmd = f"sudo aircrack-ng {capture_file}"
        if wordlist:
            cmd += f" -w {wordlist}"
        if extra:
            cmd += f" {extra}"
        return self._run_command(cmd)

    def get_tool_help(self, tool: str) -> str:
        """Restituisce l'help di un tool della suite."""
        if tool not in self.tools:
            return "Tool non supportato."
        stdout, stderr, return_code = self.executor.execute(f"{tool} --help", shell=True)
        return stdout if return_code == 0 else stderr

    def _run_command(self, cmd: str) -> Dict[str, str]:
        stdout, stderr, return_code = self.executor.execute(cmd, timeout=120)
        return {
            "command": cmd,
            "output": stdout.strip(),
            "error": stderr.strip(),
            "success": return_code == 0,
            "return_code": return_code
        }

    def get_info(self) -> Dict[str, List[str]]:
        return {
            "name": "Aircrack Suite",
            "description": "Gestione aircrack-ng, airmon-ng, aireplay-ng e airodump-ng",
            "tools": self.tools
        }
