"""
CDN-FRAMEWORK - Entry Point
Punto di ingresso principale del programma
"""

import sys
import os
import logging
from pathlib import Path

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.logger import setup_logger
from cli.commands import CLIParser, CommandInfo
from executor.executor import CommandExecutor
from modules.nmap.nmap_module import NmapModule
from modules.wifi.wifi_module import WifiModule
from modules.aircrack.aircrack_module import AircrackModule
from modules.update.update_module import UpdateModule

# Setup logging
logger = setup_logger('CDN-FRAMEWORK', log_level='INFO')
VERSION = "1.1.0"


class CDNFramework:
    """Framework principale"""

    def __init__(self):
        self.executor = CommandExecutor()
        self.cli = CLIParser()
        self.update = UpdateModule(self.executor)
        self.nmap = NmapModule(self.executor)
        self.wifi = WifiModule(self.executor)
        self.air = AircrackModule(self.executor)

        self._register_commands()

    def _register_commands(self):
        """Registra i comandi disponibili"""
        self.cli.register_command(CommandInfo(
            name="scan",
            description="Esegui uno scan Nmap su un target",
            args_required=["target"],
            args_optional=["ports", "type", "output_format", "verbose", "extra"],
            handler=self.handle_scan
        ))

        self.cli.register_command(CommandInfo(
            name="wifi",
            description="Gestione interfacce WiFi e modalità monitor/managed",
            args_required=["action"],
            args_optional=["interface", "mode", "target", "count"],
            handler=self.handle_wifi
        ))

        self.cli.register_command(CommandInfo(
            name="airmon",
            description="Avvia o arresta la modalità monitor con airmon-ng",
            args_required=["action", "interface"],
            args_optional=[],
            handler=self.handle_airmon
        ))

        self.cli.register_command(CommandInfo(
            name="airodump",
            description="Esegui airodump-ng su un'interfaccia wireless",
            args_required=["interface"],
            args_optional=["output", "extra"],
            handler=self.handle_airodump
        ))

        self.cli.register_command(CommandInfo(
            name="aireplay",
            description="Esegui aireplay-ng per attacchi WiFi",
            args_required=["attack", "interface"],
            args_optional=["target", "count", "extra"],
            handler=self.handle_aireplay
        ))

        self.cli.register_command(CommandInfo(
            name="aircrack",
            description="Esegui aircrack-ng su un file di cattura",
            args_required=["capture"],
            args_optional=["wordlist", "extra"],
            handler=self.handle_aircrack
        ))

        self.cli.register_command(CommandInfo(
            name="help",
            description="Mostra l'aiuto",
            args_required=[],
            handler=self.handle_help
        ))

        self.cli.register_command(CommandInfo(
            name="version",
            description="Mostra la versione",
            args_required=[],
            handler=self.handle_version
        ))

    def ensure_root(self):
        """Verifica se lo strumento è avviato con sudo/root."""
        if os.name != "nt" and os.geteuid() != 0:
            print("❌ Questo tool deve essere avviato con sudo. Rilancia con sudo.")
            sys.exit(1)

    def auto_update(self):
        """Verifica la presenza di aggiornamenti nel repository Git e applica l'aggiornamento automatico."""
        if self.update.is_update_available():
            print("🔄 Aggiornamento automatico rilevato. Sincronizzo repository...")
            success, _, stderr = self.update.perform_update()
            if success:
                print("✅ Aggiornamento completato. Riavvio automatico...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            print("❌ Aggiornamento automatico fallito.")
            if stderr:
                print(stderr)

    def handle_scan(self, params: dict) -> int:
        """Handler per comando 'scan'"""
        target = params.get('target')
        if not target:
            print("❌ Target non specificato!")
            return 1

        print(f"\n🔍 Inizio scan Nmap su {target}")
        result = self.nmap.scan(target, params)

        if result['success']:
            print("\n✅ Scan completato!\n")
            print("Output:")
            print("-" * 60)
            print(result['output'])
            print("-" * 60)
            return 0

        print("\n❌ Scan fallito!")
        print(f"Errore: {result['error']}")
        return 1

    def handle_wifi(self, params: dict) -> int:
        """Handler per comando 'wifi'"""
        action = params.get('action', '').lower()
        if action == 'list':
            interfaces = self.wifi.get_interfaces_summary()
            if not interfaces:
                print("⚠️  Nessuna interfaccia WiFi trovata.")
                return 0
            print("\n🔌 Interfacce WiFi trovate:\n")
            for iface in interfaces:
                print(f"- {iface['name']} | type={iface.get('type')} | state={iface.get('state')}")
            return 0

        if action == 'status':
            interface = params.get('interface')
            if not interface:
                print("❌ Specifica l'interfaccia con -interface <nome>.")
                return 1
            state = self.wifi.get_interface_state(interface)
            print(f"\n📶 Stato interfaccia {interface}: {state}")
            return 0

        if action == 'mode':
            interface = params.get('interface')
            mode = params.get('mode', '').lower()
            if not interface or not mode:
                print("❌ Usa: sudo python3 main.py wifi mode <interface> -mode managed|monitor")
                return 1
            result = self.wifi.set_mode(interface, mode)
            if result['success']:
                print(f"✅ Modalità {mode} applicata a {interface}.")
                print(result['output'])
                return 0
            print(f"❌ Fallito: {result['error']}")
            return 1

        print("❌ Azione WiFi non riconosciuta. Usa list, status o mode.")
        return 1

    def handle_airmon(self, params: dict) -> int:
        """Handler per comando 'airmon'"""
        action = params.get('action', '').lower()
        interface = params.get('interface')
        if action not in ['start', 'stop'] or not interface:
            print("❌ Usa: sudo python3 main.py airmon <start|stop> <interface>")
            return 1
        result = self.air.run_airmon(interface, action)
        if result['success']:
            print(result['output'])
            return 0
        print(f"❌ Fallito: {result['error']}")
        return 1

    def handle_airodump(self, params: dict) -> int:
        """Handler per comando 'airodump'"""
        interface = params.get('interface')
        if not interface:
            print("❌ Specifica l'interfaccia con: sudo python3 main.py airodump <interface>")
            return 1
        output = params.get('output')
        extra = params.get('extra')
        result = self.air.run_airodump(interface, output, extra)
        if result['success']:
            print(result['output'])
            return 0
        print(f"❌ Fallito: {result['error']}")
        return 1

    def handle_aireplay(self, params: dict) -> int:
        """Handler per comando 'aireplay'"""
        attack = params.get('attack', '').lower()
        interface = params.get('interface')
        if not attack or not interface:
            print("❌ Usa: sudo python3 main.py aireplay <attack> <interface> -target <BSSID> -count <N>")
            return 1
        target = params.get('target')
        count = int(params.get('count', 10)) if params.get('count') else 10
        extra = params.get('extra')
        result = self.air.run_aireplay(interface, attack, target, count, extra)
        if result['success']:
            print(result['output'])
            return 0
        print(f"❌ Fallito: {result['error']}")
        return 1

    def handle_aircrack(self, params: dict) -> int:
        """Handler per comando 'aircrack'"""
        capture = params.get('capture')
        if not capture:
            print("❌ Specifica il file di cattura: sudo python3 main.py aircrack <capture>")
            return 1
        wordlist = params.get('wordlist')
        extra = params.get('extra')
        result = self.air.run_aircrack(capture, wordlist, extra)
        if result['success']:
            print(result['output'])
            return 0
        print(f"❌ Fallito: {result['error']}")
        return 1

    def handle_help(self, params: dict) -> int:
        """Handler per comando 'help'"""
        command = params.get('command') if params else None
        print(self.cli.get_help(command))
        return 0

    def handle_version(self, params: dict) -> int:
        """Handler per comando 'version'"""
        print(f"🔧 CDN-FRAMEWORK v{VERSION}")
        print("Strumento modulare per network reconnaissance")
        return 0

    def run(self, args: list) -> int:
        """
        Esegui il framework con gli argomenti forniti
        """
        self.ensure_root()
        self.auto_update()

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

        handler = self.cli.commands[command_name].handler
        return handler(params)


def main():
    """Punto di ingresso principale"""
    framework = CDNFramework()
    args = sys.argv[1:]
    exit_code = framework.run(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
