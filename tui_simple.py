"""
NetHunterCDN TUI: Interfaccia testuale avanzata tipo Metasploit
Versione completa con grafica MSF-like, rosso/nero, moduli interattivi.
"""

import sys
import os
import re
from pathlib import Path
import threading
import time
import platform
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.live import Live
from rich.layout import Layout

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.logger import setup_logger
from executor.executor import CommandExecutor
from modules.nmap.nmap_module import NmapModule
from modules.wifi.wifi_module import WifiModule
from modules.wifi.scan import WifiScanModule
from modules.wifi.capture import WifiCaptureModule
from modules.wifi.crack import WifiCrackModule
from modules.aircrack.aircrack_module import AircrackModule
from modules.update.update_module import UpdateModule

logger = setup_logger('NetHunterCDN-TUI', log_level='INFO')
VERSION = "1.1.0"
AUTHOR = "GAETAL2025"


class NetHunterCDNTUI:
    """TUI avanzata tipo Metasploit per NetHunterCDN"""

    def __init__(self):
        self.console = Console()
        self.executor = CommandExecutor()
        self.nmap = NmapModule(self.executor)
        self.wifi = WifiModule(self.executor)
        self.wifi_scan = WifiScanModule(self.executor)
        self.wifi_capture = WifiCaptureModule(self.executor)
        self.wifi_crack = WifiCrackModule(self.executor)
        self.air = AircrackModule(self.executor)
        self.update = UpdateModule(self.executor)
        self.last_output = None

        # Stato TUI
        self.current_module = None
        self.module_options = {}
        self.global_options = {
            'target': None,
            'interface': 'wlan0',
            'verbose': False
        }

        self.ensure_root()
        self.auto_update()

    def show_banner(self):
        """Mostra il banner tipo Metasploit."""
        banner = """
[bold red]
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    [bold white]NetHunterCDN v{VERSION}[/bold white]                                   ║
║                                                                              ║
║                [bold yellow]Network Reconnaissance & WiFi Security Framework[/bold yellow]                ║
║                                                                              ║
║        [bold cyan]═╗ ╔═ ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╗[/bold cyan]        ║
║        [bold cyan]╔╝ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║ ║[/bold cyan]        ║
║        [bold cyan]╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝[/bold cyan]        ║
║                                                                              ║
║        [bold green]Author:[/bold green] [white]{AUTHOR}[/white]    [bold green]Platform:[/bold green] [white]{platform}[/white]    [bold green]Arch:[/bold green] [white]{arch}[/white] ║
║                                                                              ║
║        [bold magenta]Type 'help' for commands, 'use <module>' to load modules[/bold magenta]         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
[/bold red]
        """.format(
            VERSION=VERSION,
            AUTHOR=AUTHOR,
            platform=platform.system(),
            arch=platform.machine()
        )

        self.console.print(banner, style="red on black")

    def validate_ip(self, ip: str) -> bool:
        """Valida un indirizzo IP."""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        parts = ip.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True

    def ensure_root(self):
        """Verifica che il tool sia eseguito con privilegi root/sudo."""
        if os.name != "nt" and os.geteuid() != 0:
            self.console.print(Panel("[bold red]Questo tool deve essere avviato con sudo. Rilancia con sudo.[/bold red]", style="red on black"))
            sys.exit(1)

    def auto_update(self):
        """Verifica la presenza di aggiornamenti e applica l'aggiornamento automatico."""
        if self.update.is_update_available():
            self.console.print(Panel("[bold red]Aggiornamento automatico rilevato. Sincronizzo repository...[/bold red]", style="red on black", border_style="red"))
            success, _, stderr = self.update.perform_update()
            if success:
                self.console.print(Panel("[bold green]Aggiornamento completato. Riavvio in corso...[/bold green]", style="red on black", border_style="green"))
                os.execv(sys.executable, [sys.executable] + sys.argv)
            self.console.print(Panel(f"[bold yellow]Aggiornamento fallito:[/bold yellow]\n{stderr}", style="red on black", border_style="red"))

    def run(self):
        """Loop principale della TUI."""
        self.show_banner()

        while True:
            try:
                # Prompt tipo MSF
                prompt = f"[bold red]nhcdn[/bold red] > "
                if self.current_module:
                    prompt = f"[bold red]nhcdn[/bold red] [bold yellow]({self.current_module})[/bold yellow] > "

                command = Prompt.ask(prompt).strip()

                if not command:
                    continue

                self.handle_command(command)

            except KeyboardInterrupt:
                self.console.print("\n[bold yellow]Uscita...[/bold yellow]")
                break
            except Exception as e:
                self.console.print(f"[bold red]Errore: {e}[/bold red]")
                continue

    def handle_command(self, command: str):
        """Gestisce i comandi inseriti."""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == 'help' or cmd == '?':
            self.show_help()
        elif cmd == 'exit' or cmd == 'quit':
            self.console.print("[bold yellow]Arrivederci![/bold yellow]")
            sys.exit(0)
        elif cmd == 'version':
            self.console.print(f"[bold green]NetHunterCDN v{VERSION}[/bold green]")
        elif cmd == 'banner':
            self.show_banner()
        elif cmd == 'use':
            if args:
                self.use_module(' '.join(args))
            else:
                self.console.print("[bold red]Uso: use <module>[/bold red]")
        elif cmd == 'show':
            if args and args[0] == 'modules':
                self.show_modules()
            elif args and args[0] == 'options':
                self.show_options()
            else:
                self.console.print("[bold red]Uso: show modules|options[/bold red]")
        elif cmd == 'set':
            if len(args) >= 2:
                self.set_option(args[0], ' '.join(args[1:]))
            else:
                self.console.print("[bold red]Uso: set <option> <value>[/bold red]")
        elif cmd == 'run' or cmd == 'exploit':
            self.run_module()
        elif cmd == 'back':
            self.current_module = None
            self.module_options = {}
            self.console.print("[bold yellow]Tornato al contesto principale[/bold yellow]")
        elif cmd == 'scan':
            if args:
                self.quick_scan(' '.join(args))
            else:
                self.console.print("[bold red]Uso: scan <target>[/bold red]")
        elif cmd == 'wifi':
            if args and args[0] == 'scan':
                self.quick_wifi_scan()
            else:
                self.console.print("[bold red]Uso: wifi scan[/bold red]")
        elif cmd == 'clear':
            self.clear_screen()
        elif cmd == 'clean':
            self.clean_files()
        else:
            self.console.print(f"[bold red]Comando sconosciuto: {cmd}[/bold red]")

    def show_help(self):
        """Mostra l'aiuto dei comandi."""
        help_text = """
[bold cyan]Comandi principali:[/bold cyan]

[bold green]Core Commands:[/bold green]
    help, ?          - Mostra questo aiuto
    version          - Mostra versione
    banner           - Mostra banner
    exit, quit       - Esci dalla console
    clear            - Pulisce il terminale
    clean            - Cancella log, cap, csv salvati

[bold green]Module Commands:[/bold green]
    use <module>     - Carica un modulo
    show modules     - Mostra moduli disponibili
    show options     - Mostra opzioni del modulo corrente
    set <opt> <val>  - Imposta un'opzione
    run, exploit     - Esegui il modulo corrente
    back             - Torna al contesto principale

[bold green]Quick Commands:[/bold green]
    scan <target>    - Scan Nmap veloce
    wifi scan        - Scan reti WiFi

[bold green]Tipi Nmap disponibili:[/bold green]
    connect, syn, fin, null, xmas, udp, idle, ack, maimon, fast, aggressive
        """
        self.console.print(Panel(help_text, title="[bold red]NetHunterCDN Help[/bold red]", border_style="red"))

    def show_modules(self):
        """Mostra i moduli disponibili."""
        table = Table(title="[bold red]Moduli Disponibili[/bold red]")
        table.add_column("Modulo", style="cyan", no_wrap=True)
        table.add_column("Descrizione", style="white")

        modules = {
            "nmap/scan": "Scanner Nmap completo con XML parsing",
            "wifi/scan": "Scanner reti WiFi con airodump-ng",
            "wifi/capture": "Cattura handshake WiFi",
            "wifi/crack": "Cracking WPA/WPA2 con aircrack-ng"
        }

        for mod, desc in modules.items():
            table.add_row(mod, desc)

        self.console.print(table)

    def use_module(self, module_name: str):
        """Carica un modulo."""
        if module_name == "nmap/scan":
            self.current_module = "nmap/scan"
            self.module_options = {
                'target': {'value': None, 'required': True, 'description': 'Target IP o hostname'},
                'type': {'value': 'syn', 'required': False, 'description': 'Tipo scan: connect, syn, fin, null, xmas, udp, idle, ack, maimon, fast, aggressive, traceroute'},
                'ports': {'value': None, 'required': False, 'description': 'Porte specifiche (es. 22,80,443)'},
                'timing': {'value': 'normal', 'required': False, 'description': 'Timing: paranoid, sneaky, polite, normal, aggressive, insane'},
                'traceroute': {'value': 'no', 'required': False, 'description': 'Abilita traceroute: yes, no'}
            }
            self.console.print(f"[bold green]Modulo caricato: {module_name}[/bold green]")
        elif module_name == "wifi/scan":
            self.current_module = "wifi/scan"
            self.module_options = {
                'interface': {'value': 'wlan0', 'required': True, 'description': 'Interfaccia WiFi'},
                'duration': {'value': 10, 'required': False, 'description': 'Durata scan in secondi'}
            }
            self.console.print(f"[bold green]Modulo caricato: {module_name}[/bold green]")
        elif module_name == "wifi/capture":
            self.current_module = "wifi/capture"
            self.module_options = {
                'interface': {'value': 'wlan0mon', 'required': True, 'description': 'Interfaccia in monitor mode'},
                'bssid': {'value': None, 'required': True, 'description': 'BSSID della rete target'},
                'channel': {'value': None, 'required': True, 'description': 'Canale della rete'},
                'duration': {'value': 60, 'required': False, 'description': 'Durata cattura in secondi'}
            }
            self.console.print(f"[bold green]Modulo caricato: {module_name}[/bold green]")
        elif module_name == "wifi/crack":
            self.current_module = "wifi/crack"
            self.module_options = {
                'cap_file': {'value': None, 'required': True, 'description': 'File .cap con handshake'},
                'bssid': {'value': None, 'required': True, 'description': 'BSSID della rete'},
                'wordlist': {'value': '/usr/share/wordlists/rockyou.txt', 'required': False, 'description': 'File wordlist'}
            }
            self.console.print(f"[bold green]Modulo caricato: {module_name}[/bold green]")
        else:
            self.console.print(f"[bold red]Modulo non trovato: {module_name}[/bold red]")

    def show_options(self):
        """Mostra le opzioni del modulo corrente."""
        if not self.current_module:
            self.console.print("[bold red]Nessun modulo caricato. Usa 'use <module>'[/bold red]")
            return

        table = Table(title=f"[bold red]Opzioni per {self.current_module}[/bold red]")
        table.add_column("Opzione", style="cyan", no_wrap=True)
        table.add_column("Valore", style="yellow")
        table.add_column("Richiesta", style="green")
        table.add_column("Descrizione", style="white")

        for opt, data in self.module_options.items():
            required = "Sì" if data['required'] else "No"
            value = str(data['value']) if data['value'] is not None else "Non impostato"
            table.add_row(opt, value, required, data['description'])

        self.console.print(table)

    def set_option(self, option: str, value: str):
        """Imposta un'opzione del modulo."""
        if not self.current_module:
            self.console.print("[bold red]Nessun modulo caricato[/bold red]")
            return

        if option in self.module_options:
            # Converti tipi se necessario
            if option == 'duration' or option == 'channel':
                try:
                    value = int(value)
                except:
                    self.console.print(f"[bold red]Valore non valido per {option}[/bold red]")
                    return
            self.module_options[option]['value'] = value
            self.console.print(f"[bold green]{option} => {value}[/bold green]")
        else:
            self.console.print(f"[bold red]Opzione non trovata: {option}[/bold red]")

    def run_module(self):
        """Esegue il modulo corrente."""
        if not self.current_module:
            self.console.print("[bold red]Nessun modulo caricato[/bold red]")
            return

        # Verifica opzioni richieste
        missing = []
        for opt, data in self.module_options.items():
            if data['required'] and data['value'] is None:
                missing.append(opt)

        if missing:
            self.console.print(f"[bold red]Opzioni richieste mancanti: {', '.join(missing)}[/bold red]")
            return

        self.console.print(f"[bold yellow]Esecuzione modulo: {self.current_module}[/bold yellow]")

        if self.current_module == "nmap/scan":
            self.run_nmap_scan()
        elif self.current_module == "wifi/scan":
            self.run_wifi_scan()
        elif self.current_module == "wifi/capture":
            self.run_wifi_capture()
        elif self.current_module == "wifi/crack":
            self.run_wifi_crack()

    def run_nmap_scan(self):
        """Esegue scan Nmap con tutti i tipi di scansione."""
        target = self.module_options['target']['value']
        scan_type = self.module_options['type']['value']
        ports = self.module_options['ports']['value']
        timing = self.module_options['timing']['value']
        traceroute = self.module_options['traceroute']['value']

        params = {}
        if scan_type:
            params['type'] = scan_type
        if ports:
            params['ports'] = ports
        if timing:
            params['timing'] = timing
        if traceroute and traceroute.lower() == 'yes':
            params['traceroute'] = True

        with self.console.status("[bold green]Scanning...[/bold green]", spinner="dots"):
            result = self.nmap.scan(target, params)

        if result['success']:
            data = result['data']
            self.console.print(f"\n[bold green]Host: {target}[/bold green]")
            self.console.print(f"[bold green]Stato: {data['status']}[/bold green]")
            if data['ports']:
                self.console.print("[bold green]Porte aperte:[/bold green]")
                for port in data['ports']:
                    if port['state'] == 'open':
                        self.console.print(f"  [cyan]{port['port']}/tcp[/cyan] - [white]{port['service']}[/white]")
            else:
                self.console.print("[yellow]Nessuna porta aperta rilevata[/yellow]")
        else:
            self.console.print(f"[bold red]Scan fallito: {result['error']}[/bold red]")

    def run_wifi_scan(self):
        """Esegue scan WiFi."""
        interface = self.module_options['interface']['value']
        duration = self.module_options['duration']['value']

        with self.console.status("[bold green]Scanning WiFi...[/bold green]", spinner="dots"):
            result = self.wifi_scan.scan(interface, duration)

        if result['success']:
            networks = result['data']['networks']
            self.console.print(f"\n[bold green]Reti trovate: {len(networks)}[/bold green]")
            table = Table()
            table.add_column("ESSID", style="cyan")
            table.add_column("BSSID", style="yellow")
            table.add_column("Canale", style="green")
            table.add_column("Sicurezza", style="red")

            for net in networks[:10]:  # Max 10
                table.add_row(
                    net.get('essid', 'Hidden'),
                    net.get('bssid', 'Unknown'),
                    net.get('channel', 'Unknown'),
                    net.get('privacy', 'Unknown')
                )
            self.console.print(table)
        else:
            self.console.print(f"[bold red]Scan WiFi fallito: {result['error']}[/bold red]")

    def run_wifi_capture(self):
        """Esegue cattura WiFi."""
        interface = self.module_options['interface']['value']
        bssid = self.module_options['bssid']['value']
        channel = self.module_options['channel']['value']
        duration = self.module_options['duration']['value']

        with self.console.status("[bold green]Catturando handshake...[/bold green]", spinner="dots"):
            result = self.wifi_capture.capture_handshake(interface, bssid, channel, duration)

        if result['success']:
            data = result['data']
            self.console.print(f"[bold green]Cattura completata![/bold green]")
            self.console.print(f"File: {data['cap_file']}")
            if data['handshake_captured']:
                self.console.print("[bold green]Handshake catturato![/bold green]")
            else:
                self.console.print("[yellow]Handshake non rilevato[/yellow]")
        else:
            self.console.print(f"[bold red]Cattura fallita: {result['error']}[/bold red]")

    def run_wifi_crack(self):
        """Esegue cracking WiFi."""
        cap_file = self.module_options['cap_file']['value']
        bssid = self.module_options['bssid']['value']
        wordlist = self.module_options['wordlist']['value']

        with self.console.status("[bold green]Crackando...[/bold green]", spinner="dots"):
            result = self.wifi_crack.crack_wpa(cap_file, bssid, wordlist)

        if result['success']:
            data = result['data']
            self.console.print(f"[bold green]CHIAVE TROVATA: {data['key']}[/bold green]")
        else:
            self.console.print(f"[bold red]Cracking fallito: {result['error']}[/bold red]")

    def quick_scan(self, target: str):
        """Scan veloce Nmap."""
        if not self.validate_ip(target):
            self.console.print("[bold red]Target non valido[/bold red]")
            return

        with self.console.status("[bold green]Quick scan...[/bold green]", spinner="dots"):
            result = self.nmap.scan(target, {'type': 'fast'})

        if result['success']:
            data = result['data']
            self.console.print(f"[bold green]Host: {target} - Stato: {data['status']}[/bold green]")
            open_ports = [p for p in data['ports'] if p['state'] == 'open']
            if open_ports:
                self.console.print(f"[bold green]Porte aperte: {len(open_ports)}[/bold green]")
            else:
                self.console.print("[yellow]Nessuna porta aperta[/yellow]")
        else:
            self.console.print(f"[bold red]Scan fallito: {result['error']}[/bold red]")

    def quick_wifi_scan(self):
        """Scan veloce WiFi."""
        with self.console.status("[bold green]WiFi scan...[/bold green]", spinner="dots"):
            result = self.wifi_scan.scan('wlan0', 5)

        if result['success']:
            networks = result['data']['networks']
            self.console.print(f"[bold green]Reti trovate: {len(networks)}[/bold green]")
        else:
            self.console.print(f"[bold red]Scan fallito: {result['error']}[/bold red]")

    def clear_screen(self):
        """Pulisce il terminale."""
        os.system('clear' if os.name == 'posix' else 'cls')
        self.console.print("[bold green]Terminale pulito[/bold green]")

    def clean_files(self):
        """Cancella i file di log, capture e csv salvati."""
        import glob
        
        file_types = ['*.log', '*.cap', '*.pcap', '*.csv']
        deleted_count = 0
        
        self.console.print("[bold yellow]🗑️  Ricerca file da cancellare...[/bold yellow]")
        
        for pattern in file_types:
            files = glob.glob(os.path.join(os.getcwd(), pattern))
            for file in files:
                try:
                    os.remove(file)
                    deleted_count += 1
                    self.console.print(f"[bold red]❌ Cancellato:[/bold red] {os.path.basename(file)}")
                except Exception as e:
                    self.console.print(f"[bold yellow]⚠️  Errore cancellazione {os.path.basename(file)}: {e}[/bold yellow]")
        
        # Cancella anche i file di log degli handler
        log_dirs = [
            os.path.expanduser('~/.nethuntercdn/logs'),
            os.path.join(os.getcwd(), 'logs'),
            os.path.join(os.getcwd(), '.logs')
        ]
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                try:
                    for file in glob.glob(os.path.join(log_dir, '*.log')):
                        os.remove(file)
                        deleted_count += 1
                        self.console.print(f"[bold red]❌ Cancellato:[/bold red] {os.path.basename(file)}")
                except Exception as e:
                    self.console.print(f"[bold yellow]⚠️  Errore in {log_dir}: {e}[/bold yellow]")
        
        if deleted_count > 0:
            self.console.print(f"\n[bold green]✅ Pulizia completata! {deleted_count} file cancellati.[/bold green]")
        else:
            self.console.print("[bold green]✅ Nessun file da cancellare.[/bold green]")


def main():
    """Punto di ingresso TUI."""
    tui = NetHunterCDNTUI()
    tui.run()


if __name__ == '__main__':
    main()
