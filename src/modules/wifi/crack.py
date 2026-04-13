"""
WiFi Crack Module: Cracking WPA/WPA2 con aircrack-ng
"""

import logging
from typing import Dict, Any, Optional
import sys
import os
import subprocess
from pathlib import Path

# Aggiungi src al path per import assoluti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor.executor import CommandExecutor

logger = logging.getLogger(__name__)


class WifiCrackModule:
    """Modulo per cracking WiFi con aircrack-ng"""

    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.aircrack_tool = "aircrack-ng"

    def check_available(self) -> bool:
        """Verifica se aircrack-ng è disponibile"""
        if self.executor.check_command_exists(self.aircrack_tool):
            logger.info("aircrack-ng disponibile")
            return True
        else:
            logger.error("aircrack-ng non trovato. Installa con: sudo apt install aircrack-ng")
            return False

    def crack_wpa(self, cap_file: str, bssid: str, wordlist: str) -> Dict[str, Any]:
        """
        Cracca WPA/WPA2 usando aircrack-ng con wordlist
        """
        if not self.check_available():
            return {
                "success": False,
                "data": None,
                "error": "aircrack-ng non disponibile"
            }

        if not os.path.exists(cap_file):
            return {
                "success": False,
                "data": None,
                "error": f"File di cattura {cap_file} non trovato"
            }

        if not os.path.exists(wordlist):
            return {
                "success": False,
                "data": None,
                "error": f"Wordlist {wordlist} non trovata"
            }

        try:
            print(f"🔓 Avvio cracking su {cap_file}")
            print(f"📖 Wordlist: {wordlist}")
            print("⏳ Questo potrebbe richiedere molto tempo...")

            # Comando aircrack-ng
            crack_cmd = f"{self.aircrack_tool} -w {wordlist} -b {bssid} {cap_file}"
            logger.info(f"Esecuzione: {crack_cmd}")

            # Esegui il comando (può essere lungo)
            result = subprocess.run(
                crack_cmd.split(),
                capture_output=True,
                text=True,
                timeout=3600  # 1 ora timeout
            )

            # Analizza output
            if result.returncode == 0 and "KEY FOUND" in result.stdout:
                # Estrai la chiave
                lines = result.stdout.split('\n')
                key_line = None
                for line in lines:
                    if "KEY FOUND" in line:
                        key_line = line
                        break

                if key_line:
                    # Parsing semplice della chiave
                    key = key_line.split('[')[-1].split(']')[0].strip()
                    return {
                        "success": True,
                        "data": {
                            "key_found": True,
                            "key": key,
                            "bssid": bssid,
                            "cap_file": cap_file
                        },
                        "error": None
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "error": "Chiave trovata ma non parsabile"
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": "Chiave non trovata nella wordlist"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "data": None,
                "error": "Timeout durante cracking (1 ora)"
            }
        except Exception as e:
            logger.error(f"Errore durante cracking: {e}")
            return {
                "success": False,
                "data": None,
                "error": f"Errore cracking: {str(e)}"
            }