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
from modules.wifi.scan import WifiScanModule
from modules.wifi.capture import WifiCaptureModule
from modules.wifi.crack import WifiCrackModule
from modules.aircrack.aircrack_module import AircrackModule
from modules.update.update_module import UpdateModule

# Setup logging
logger = setup_logger('NetRecon', log_level='INFO')
VERSION = "1.1.0"


class NetRecon:
    """Framework principale"""

    def __init__(self):
        self.executor = CommandExecutor()
        self.cli = CLIParser()
        self.update = UpdateModule(self.executor)
        self.nmap = NmapModule(self.executor)
        self.wifi = WifiModule(self.executor)
        self.wifi_scan = WifiScanModule(self.executor)
        self.wifi_capture = WifiCaptureModule(self.executor)
        self.wifi_crack = WifiCrackModule(self.executor)
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
            name="help",
            description="Mostra l'aiuto",
            args_required=[],
            handler=self.handle_help
        ))

        self.cli.register_command(CommandInfo(
            name="wifi",
            description="Gestione interfacce WiFi e scan reti",
            args_required=["action"],
            args_optional=["interface", "mode", "duration"],
            handler=self.handle_wifi
        ))

        self.cli.register_command(CommandInfo(
            name="wifi-capture",
            description="Cattura handshake WiFi da una rete specifica",
            args_required=["bssid", "channel"],
            args_optional=["interface", "duration"],
            handler=self.handle_wifi_capture
        ))

        self.cli.register_command(CommandInfo(
            name="wifi-crack",
            description="Cracca WPA/WPA2 da file di cattura",
            args_required=["cap_file", "bssid"],
            args_optional=["wordlist"],
            handler=self.handle_wifi_crack
        ))

        # For v0.1, only scan, help, and wifi commands are active
        # Other commands commented out to focus on core functionality

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

        # Validate target
        import re
        if not (re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target) or re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', target)):
            print("❌ Target non valido! Usa un IP o hostname valido.")
            return 1

        print(f"\n🔍 Inizio scan Nmap su {target}")
        result = self.nmap.scan(target, params)

        if result['success']:
            data = result['data']
            print("\n✅ Scan completato!\n")
            print(f"Host: {target}")
            print(f"Stato: {data['status']}")
            if data['ports']:
                print("Porte aperte:")
                for port in data['ports']:
                    if port['state'] == 'open':
                        print(f"  {port['port']}/tcp - {port['service']}")
            else:
                print("Nessuna porta aperta rilevata.")
            return 0

        print("\n❌ Scan fallito!")
        print(f"Errore: {result['error']}")
        return 1

    def handle_wifi(self, params: dict) -> int:
        """Handler per comando 'wifi'"""
        action = params.get('action', '').lower()
        if action == 'list':
            interfaces = self.wifi.list_interfaces()
            if not interfaces:
                print("⚠️  Nessuna interfaccia WiFi trovata.")
                return 0
            print("\n🔌 Interfacce WiFi trovate:\n")
            for iface in interfaces:
                print(f"- {iface['name']} | type={iface.get('type')}")
            return 0

        if action == 'scan':
            interface = params.get('interface')
            duration = int(params.get('duration', 10))
            if not interface:
                print("❌ Specifica l'interfaccia con -interface <nome>.")
                return 1
            print(f"\n🔍 Inizio scan WiFi su {interface} per {duration} secondi")
            result = self.wifi_scan.scan(interface, duration)
            if result['success']:
                networks = result['data']['networks']
                print(f"\n✅ Scan completato! Trovate {len(networks)} reti:\n")
                for net in networks[:10]:  # Mostra max 10
                    print(f"ESSID: {net['essid']} | BSSID: {net['bssid']} | Canale: {net['channel']} | Sicurezza: {net['privacy']}")
                if len(networks) > 10:
                    print(f"... e altre {len(networks)-10} reti")
                return 0
            print(f"❌ Scan fallito: {result['error']}")
            return 1

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

        print("❌ Azione WiFi non riconosciuta. Usa list, scan, status o mode.")
        return 1

    def handle_wifi_capture(self, params: dict) -> int:
        """Handler per comando 'wifi-capture'"""
        bssid = params.get('bssid')
        channel = int(params.get('channel', 0))
        interface = params.get('interface', 'wlan0mon')
        duration = int(params.get('duration', 60))

        if not bssid or channel == 0:
            print("❌ Specifica BSSID e canale. Es: wifi-capture <BSSID> -channel <num>")
            return 1

        print(f"🎯 Cattura handshake per {bssid} su canale {channel}")
        result = self.wifi_capture.capture_handshake(interface, bssid, channel, duration)

        if result['success']:
            data = result['data']
            print("✅ Cattura completata!")
            print(f"📁 File: {data['cap_file']}")
            if data['handshake_captured']:
                print("🔓 Handshake catturato! Pronto per cracking.")
            else:
                print("⚠️ Handshake non rilevato. Riprova con più tempo o più deauth.")
            return 0
        else:
            print(f"❌ Cattura fallita: {result['error']}")
            return 1

    def handle_wifi_crack(self, params: dict) -> int:
        """Handler per comando 'wifi-crack'"""
        cap_file = params.get('cap_file')
        bssid = params.get('bssid')
        wordlist = params.get('wordlist', '/usr/share/wordlists/rockyou.txt')

        if not cap_file or not bssid:
            print("❌ Specifica file CAP e BSSID. Es: wifi-crack <file.cap> <BSSID> -wordlist <file>")
            return 1

        print(f"🔓 Cracking {bssid} con wordlist {wordlist}")
        result = self.wifi_crack.crack_wpa(cap_file, bssid, wordlist)

        if result['success']:
            data = result['data']
            print("🎉 CHIAVE TROVATA!")
            print(f"🔑 Password: {data['key']}")
            return 0
        else:
            print(f"❌ Cracking fallito: {result['error']}")
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
        print(f"NetRecon v{VERSION}")
        print("Strumento modulare per network reconnaissance")
        return 0

    def run(self, args: list) -> int:
        """
        Esegui il framework con gli argomenti forniti
        """
        # self.ensure_root()
        # self.auto_update()

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
    framework = NetRecon()
    args = sys.argv[1:]
    exit_code = framework.run(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
