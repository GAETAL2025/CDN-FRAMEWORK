"""
Executor: Modulo che esegue comandi shell e cattura output
Ponte tra CDN-FRAMEWORK e tool esterni (Nmap, Aircrack-ng, ecc)
"""

import subprocess
import logging
from typing import Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Esegue comandi di sistema e gestisce output/errori"""
    
    def __init__(self):
        self.last_return_code = None
        self.last_output = None
        self.last_error = None
    
    def execute(self, command: str, shell: bool = True, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        """
        Esegue un comando shell e cattura output
        
        Args:
            command: Comando da eseguire
            shell: Se True, esegui tramite shell
            timeout: Timeout in secondi (None = infinito)
        
        Returns:
            Tupla (stdout, stderr, return_code)
        """
        try:
            logger.info(f"Esecuzione comando: {command}")
            
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            self.last_return_code = result.returncode
            self.last_output = result.stdout
            self.last_error = result.stderr
            
            if result.returncode != 0:
                logger.warning(f"Comando terminato con codice {result.returncode}")
                logger.warning(f"stderr: {result.stderr}")
            
            return result.stdout, result.stderr, result.returncode
            
        except subprocess.TimeoutExpired:
            error_msg = f"Comando timeout dopo {timeout} secondi"
            logger.error(error_msg)
            self.last_error = error_msg
            return "", error_msg, -1
            
        except Exception as e:
            error_msg = f"Errore esecuzione comando: {str(e)}"
            logger.error(error_msg)
            self.last_error = error_msg
            return "", error_msg, -1
    
    def check_command_exists(self, command: str) -> bool:
        """
        Verifica se un comando esiste nel sistema
        
        Args:
            command: Nome del comando
        
        Returns:
            True se esiste, False altrimenti
        """
        stdout, stderr, return_code = self.execute(f"which {command}", shell=True)
        return return_code == 0
    
    def get_last_output(self) -> str:
        """Restituisce l'ultimo output catturato"""
        return self.last_output or ""
    
    def get_last_error(self) -> str:
        """Restituisce l'ultimo errore catturato"""
        return self.last_error or ""
    
    def get_last_return_code(self) -> int:
        """Restituisce l'ultimo return code"""
        return self.last_return_code or -1
