"""
CDN-FRAMEWORK - Entry Point
Punto di ingresso principale del programma
"""

import sys
import logging
from pathlib import Path

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.logger import setup_logger
from cli.commands import CLIParser, CommandInfo
from executor.executor import CommandExecutor
from modules.nmap.nmap_module import NmapModule

# Setup logging
logger = setup_logger('CDN-FRAMEWORK', log_level='INFO')


class CDNFramework:
    """Framework principale"""
    
    def __init__(self):
        self.executor = CommandExecutor()
        self.cli = CLIParser()
        self.nmap = NmapModule(self.executor)
        
        self._register_commands()
    
    def _register_commands(self):
        """Registra i comandi disponibili"""
        
        # Comando: scan
        self.cli.register_command(CommandInfo(
            name="scan",
            description="Esegui uno scan Nmap su un target",
            args_required=["target"],
            args_optional=["ports", "type", "verbose"],
            handler=self.handle_scan
        ))
        
        # Comando: wifi
        self.cli.register_command(CommandInfo(
            name="wifi",
            description="Modulo WiFi (non ancora implementato)",
            handler=self.handle_wifi
        ))
        
        # Comando: help
        self.cli.register_command(CommandInfo(
            name="help",
            description="Mostra l'aiuto",
            handler=self.handle_help
        ))
        
        # Comando: version
        self.cli.register_command(CommandInfo(
            name="version",
            description="Mostra la versione",
            handler=self.handle_version
        ))
    
    def handle_scan(self, params: dict) -> int:
        """Handler per comando 'scan'"""
        target = params.get('target')
        
        if not target:
            print("❌ Target non specificato!")
            return 1
        
        print(f"\n🔍 Inizio scan Nmap su {target}")
        
        result = self.nmap.scan(target, params)
        
        if result['success']:
            print(f"\n✅ Scan completato!\n")
            print("Output:")
            print("-" * 60)
            print(result['output'])
            print("-" * 60)
            return 0
        else:
            print(f"\n❌ Scan fallito!")
            print(f"Errore: {result['error']}")
            return 1
    
    def handle_wifi(self, params: dict) -> int:
        """Handler per comando 'wifi'"""
        print("⚠️  Modulo WiFi non ancora implementato (Fase successiva)")
        return 0
    
    def handle_help(self, params: dict) -> int:
        """Handler per comando 'help'"""
        command = params.get('command') if params else None
        print(self.cli.get_help(command))
        return 0
    
    def handle_version(self, params: dict) -> int:
        """Handler per comando 'version'"""
        print("🔧 CDN-FRAMEWORK v1.0.0")
        print("Strumento modulare per network reconnaissance")
        return 0
    
    def run(self, args: list) -> int:
        """
        Esegui il framework con gli argomenti forniti
        
        Args:
            args: Argomenti da linea di comando
        
        Returns:
            Codice di uscita (0 = successo, 1 = errore)
        """
        if not args:
            print(self.cli.get_help())
            return 0
        
        command_name, params = self.cli.parse(args)
        
        if not command_name:
            print("❌ Comando non valido!")
            print(self.cli.get_help())
            return 1
        
        if params is None:
            params = {}
        
        # Esegui handler
        handler = self.cli.commands[command_name].handler
        return handler(params)


def main():
    """Punto di ingresso principale"""
    framework = CDNFramework()
    
    # Gli argomenti sono: scriptname, comando, arg1, arg2, ...
    # Prendiamo solo comando e argomenti (salta programme name)
    args = sys.argv[1:]
    
    exit_code = framework.run(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
