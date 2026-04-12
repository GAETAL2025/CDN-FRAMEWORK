"""
Modulo Nmap: Integrazione con Nmap per scanning della rete
"""

import logging
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Aggiungi src al path per import assoluti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor.executor import CommandExecutor

logger = logging.getLogger(__name__)


class NmapModule:
    """Modulo dedicato a Nmap"""
    
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
        
        Args:
            target: Indirizzo IP o hostname da scannare
            params: Dizionario con parametri aggiuntivi
                - ports: range di porte (es: '22,80,443' o '1-65535')
                - type: tipo di scan ('syn', 'connect', 'ping')
                - output_format: 'text' o 'xml'
        
        Returns:
            Dizionario con risultati
        """
        if not self.check_available():
            return {
                "success": False,
                "error": "Nmap non disponibile",
                "output": ""
            }
        
        # Costruisci comando Nmap
        command = self._build_command(target, params)
        
        logger.info(f"Esecuzione scan Nmap su {target}")
        logger.info(f"Comando: {command}")
        
        # Esegui comando
        stdout, stderr, return_code = self.executor.execute(command)
        
        success = return_code == 0
        
        result = {
            "success": success,
            "target": target,
            "command": command,
            "output": stdout,
            "error": stderr if not success else "",
            "return_code": return_code
        }
        
        if not success:
            logger.error(f"Scan fallito: {stderr}")
        else:
            logger.info(f"Scan completato con successo")
        
        return result
    
    def _build_command(self, target: str, params: Dict[str, Any]) -> str:
        """Costruisce il comando Nmap con i parametri forniti"""
        cmd = [self.tool_name]
        
        # Tipo di scan
        scan_type = params.get('type', 'syn').lower()
        if scan_type == 'syn':
            cmd.append('-sS')  # SYN scan
        elif scan_type == 'connect':
            cmd.append('-sT')  # Connect scan
        elif scan_type == 'ping':
            cmd.append('-sn')  # Ping scan
        else:
            cmd.append('-sS')  # Default: SYN
        
        # Range porte
        if 'ports' in params:
            cmd.append(f"-p {params['ports']}")
        
        # Formato output
        output_format = params.get('output_format', 'text').lower()
        if output_format == 'xml':
            # Genera file XML (lo salviamo come output)
            cmd.append('-oX -')  # Output XML a stdout
        
        # Verbose
        if params.get('verbose', False):
            cmd.append('-v')
        
        # Target
        cmd.append(target)
        
        return ' '.join(cmd)
    
    def get_info(self) -> Dict[str, str]:
        """Restituisce info sul modulo"""
        return {
            "name": "Nmap Module",
            "description": "Integrazione con Nmap per network scanning",
            "version": "1.0.0",
            "dependencies": ["nmap"]
        }
