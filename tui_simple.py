"""
TUI Semplice: menu interattivo con rich
Versione rosso/nero con titoli grandi e gestione WiFi/Aircrack.
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

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.logger import setup_logger
from executor.executor import CommandExecutor
from modules.nmap.nmap_module import NmapModule
from modules.wifi.wifi_module import WifiModule
from modules.aircrack.aircrack_module import AircrackModule
from modules.update.update_module import UpdateModule

logger = setup_logger('CDN-TUI-SIMPLE', log_level='INFO')
VERSION = "1.1.0"
AUTHOR = "GAETAL2025"


class CDNTUISimple:
    """TUI semplice tipo Metasploit con Rich"""

    def __init__(self):
        self.console = Console()
        self.executor = CommandExecutor()
        self.nmap = NmapModule(self.executor)
        self.wifi = WifiModule(self.executor)
        self.air = AircrackModule(self.executor)
        self.update = UpdateModule(self.executor)
        self.last_output = None

        self.ensure_root()
        self.auto_update()

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

    def check_and_kill_interfering_processes(self):
        """Uccide i processi che potrebbero interferire con il monitor mode (NetworkManager, ecc.)."""
        self.console.print(Panel("[bold yellow]🔧 Controllo e uccisione processi interferenti...[/bold yellow]", style="yellow on black", border_style="yellow"))
        result = self.executor.run_command("airmon-ng check kill", sudo=True)
        if result["success"]:
            self.console.print(Panel("[bold green]✅ Processi interferenti uccisi con successo.[/bold green]", style="green on black", border_style="green"))
        else:
            self.console.print(Panel(f"[bold red]❌ Errore nell'uccisione processi: {result['error']}[/bold red]", style="red on black", border_style="red"))

    def auto_update(self):
        """Verifica la presenza di aggiornamenti e applica l'aggiornamento automatico."""
        if self.update.is_update_available():
            self.console.print(Panel("[bold red]Aggiornamento automatico rilevato. Sincronizzo repository...[/bold red]", style="red on black", border_style="red"))
            success, _, stderr = self.update.perform_update()
            if success:
                self.console.print(Panel("[bold green]Aggiornamento completato. Riavvio in corso...[/bold green]", style="red on black", border_style="green"))
                os.execv(sys.executable, [sys.executable] + sys.argv)
            self.console.print(Panel(f"[bold yellow]Aggiornamento fallito:[/bold yellow]\n{stderr}", style="red on black", border_style="red"))

    def print_header(self):
        """Mostra header del menu principale."""
        try:
            with open('ascii-art.txt', 'r') as f:
                logo_lines = [line.rstrip() for line in f]
        except FileNotFoundError:
            logo_lines = ["CDN FRAMEWORK LOGO NOT FOUND"]

        logo_art = Text(
            "\n".join(logo_lines),
            style="bold red on black",
            justify="center"
        )

        self.console.clear()
        self.console.print(logo_art)
        header_panel = Panel(
            Align.center(Text("CDN FRAMEWORK", style="bold bright_red on black"), vertical="middle"),
            title="[bold bright_red]🚀 CDN FRAMEWORK 🚀[/bold bright_red]",
            subtitle=f"[bright_white]Author: {AUTHOR} | Version: {VERSION}[/bright_white]",
            border_style="bright_red",
            style="black on grey7",
            expand=True,
        )
        self.console.print(header_panel)
        self.console.print()

    def print_menu(self):
        """Mostra il menu principale"""
        menu_items = [
            "[bold cyan]1)[/] 🔍 [cyan]Scansione Nmap[/cyan]",
            "[bold green]2)[/] 🛰️  [green]Aircrack Suite[/green]",
            "[bold yellow]3)[/] 📡 [yellow]WiFi Interfaces[/yellow]",
            "[bold magenta]4)[/] 📊 [magenta]Visualizza ultimo Output[/magenta]",
            "[bold blue]5)[/] ⚙️  [blue]Impostazioni[/blue]",
            "[bold white]6)[/] 📝 [white]Help[/white]",
            "[bold red]7)[/] ❌ [red]Exit[/red]"
        ]
        menu = Panel(
            "\n".join(menu_items),
            title="[bold red]MAIN MENU[/bold red]",
            border_style="bright_red",
            style="black on grey11",
            padding=(1, 2)
        )
        self.console.print(menu)
        self.console.print(Align.center(Text(f"Author: {AUTHOR}", style="white on black")))

    def get_menu_choice(self) -> str:
        """Legge la scelta dell'utente dal menu."""
        return Prompt.ask("[bold bright_white on black]➤ Scegli un'opzione[/bold bright_white on black]", choices=["1", "2", "3", "4", "5", "6", "7"])

    def run(self):
        """Avvia la UI principale."""
        while True:
            self.print_header()
            self.print_menu()
            choice = self.get_menu_choice()
            if choice == "1":
                self.scan_menu()
            elif choice == "2":
                self.aircrack_menu()
            elif choice == "3":
                self.wifi_menu()
            elif choice == "4":
                self.view_last_output()
            elif choice == "5":
                self.show_settings()
                update_choice = Confirm.ask("[bold bright_white]🔄 Vuoi eseguire un aggiornamento manuale?[/bold bright_white]", default=False)
                if update_choice:
                    self.console.print(Panel("[bold bright_red]🔄 Aggiornamento manuale in corso...[/bold bright_red]", style="red on black", border_style="bright_red"))
                    success, _, stderr = self.update.perform_update()
                    if success:
                        self.console.print(Panel("[bold bright_green]✅ Aggiornamento completato. Riavvio necessario.[/bold bright_green]", style="green on black", border_style="green"))
                    else:
                        self.console.print(Panel(f"[bold bright_red]❌ Aggiornamento fallito: {stderr}[/bold bright_red]", style="red on black", border_style="red"))
                Prompt.ask("[bold bright_white]⏎ Premi invio per tornare al menu[/bold bright_white]", default="")
            elif choice == "6":
                self.show_help()
                Prompt.ask("Premi invio per tornare al menu", default="")
            else:
                self.console.print(Panel("[bold bright_red]👋 Uscita in corso... Arrivederci![/bold bright_red]", style="red on black", border_style="bright_red"))
                break

    def scan_menu(self):
        """Menu per lanciare gli scan Nmap."""
        self.console.clear()
        self.console.print(Panel("[bold bright_red]🔍 Nmap Scan Options[/bold bright_red]", style="red on black", border_style="bright_red"))
        self.show_scan_modes()

        target = Prompt.ask("[bold bright_white]🎯 Target IP/Host[/bold bright_white]", default="127.0.0.1")
        if not target:
            self.console.print(Panel("[bold yellow]⚠️  Nessun target fornito, ritorno al menu.[/bold yellow]", style="yellow on black", border_style="yellow"))
            return
        if not self.validate_ip(target) and not target == "localhost":
            self.console.print(Panel("[bold yellow]⚠️  Target non valido, usa un IP valido o 'localhost'.[/bold yellow]", style="yellow on black", border_style="yellow"))
            return

        ports = Prompt.ask("[bold bright_white]🔌 Porte (es. 22,80,443 o 1-1000)[/bold bright_white]", default="22,80,443")
        scan_type = Prompt.ask(
            "[bold bright_white]⚡ Tipo di scan[/bold bright_white]",
            choices=list(self.nmap.get_scan_modes().keys()),
            default="syn"
        )
        output_format = Prompt.ask("[bold bright_white]📄 Formato output[/bold bright_white]", choices=["text", "xml"], default="text")
        verbose = Confirm.ask("[bold bright_white]🔊 Verbose?[/bold bright_white]", default=False)
        extra = Prompt.ask("[bold bright_white]⚙️  Opzioni Nmap extra (lascia vuoto se non serve)[/bold bright_white]", default="")

        self._execute_scan(target, ports, scan_type, verbose, output_format, extra)
        Prompt.ask("[bold bright_white]⏎ Premi invio per tornare al menu[/bold bright_white]", default="")

    def show_scan_modes(self):
        """Visualizza tutte le opzioni di scan supportate da Nmap."""
        table = Table(show_header=True, header_style="bold bright_white on black", border_style="bright_red", style="white on black", title="[bold bright_red]📋 Tipi di Scan Disponibili[/bold bright_red]", title_style="bold bright_red")
        table.add_column("Tipo", style="cyan", justify="center")
        table.add_column("Descrizione", style="green")
        for scan_type, description in self.nmap.get_scan_modes().items():
            table.add_row(scan_type, description)
        self.console.print(table)

    def _execute_scan(self, target: str, ports: str, scan_type: str, verbose: bool, output_format: str, extra: str):
        """Esegue lo scan Nmap con una progress bar."""
        self.console.print(Panel(f"[bold bright_red]🚀 Avvio scan su {target} con tipo {scan_type}[/bold bright_red]", style="red on black", border_style="bright_red"))
        params = {
            "ports": ports,
            "type": scan_type,
            "verbose": verbose,
            "output_format": output_format,
            "extra": extra.strip() if extra else None
        }

        result_container = [None]
        with Progress(
            SpinnerColumn(style="bright_red"),
            TextColumn("[progress.description]{task.description}", style="bright_white"),
            BarColumn(bar_width=None, style="bright_red"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%", style="bright_green"),
            transient=True,
            console=self.console,
        ) as progress:
            task = progress.add_task("🔍 Scanning in corso...", total=100)

            def scan_thread():
                result_container[0] = self.nmap.scan(target, params)
                progress.update(task, completed=100)

            thread = threading.Thread(target=scan_thread, daemon=True)
            thread.start()

            while not progress.finished:
                progress.advance(task, 2)
                time.sleep(0.04)
                if result_container[0] is not None:
                    break

            thread.join(timeout=120)

        if result_container[0] and result_container[0]["success"]:
            self.last_output = result_container[0]["output"]
            self.console.print(Panel(result_container[0]["output"], title="[bold bright_green]✅ SCAN COMPLETED[/bold bright_green]", border_style="green", style="green on black"))
        else:
            error_message = result_container[0]["error"] if result_container[0] else "Errore sconosciuto"
            self.console.print(Panel(error_message, title="[bold bright_red]❌ SCAN FAILED[/bold bright_red]", border_style="red", style="red on black"))

    def aircrack_menu(self):
        """Menu per la suite Aircrack-ng."""
        self.console.clear()
        self.check_and_kill_interfering_processes()
        while True:
            self.console.print(Panel("[bold bright_green]🛰️  Aircrack-ng Suite[/bold bright_green]", style="green on black", border_style="bright_green"))
            submenu = Panel(
                "\n".join([
                    "[bold green]1)[/] 🔧 airmon-ng (start/stop monitor mode)",
                    "[bold green]2)[/] 📡 airodump-ng (capture packets)",
                    "[bold green]3)[/] ⚡ aireplay-ng (deauth/fakeauth)",
                    "[bold green]4)[/] 🔑 aircrack-ng (crack WEP/WPA)",
                    "[bold green]5)[/] 🔙 Torna al menu principale"
                ]),
                title="[bold bright_green]AIRCRACK SUBMENU[/bold bright_green]",
                border_style="bright_green",
                style="black on grey11"
            )
            self.console.print(submenu)
            choice = Prompt.ask("[bold bright_white]🛠️  Scegli un'opzione[/bold bright_white]", choices=["1", "2", "3", "4", "5"])

            if choice == "1":
                self.airmon_menu()
            elif choice == "2":
                self.airodump_menu()
            elif choice == "3":
                self.aireplay_menu()
            elif choice == "4":
                self.aircrack_menu_run()
            else:
                break
        else:
            return

    def airmon_menu(self):
        interface = Prompt.ask("[bold bright_white]🔌 Interfaccia wireless[/bold bright_white]", default="wlan0")
        action = Prompt.ask("[bold bright_white]⚙️  Azione[/bold bright_white]", choices=["start", "stop"], default="start")
        result = self.air.run_airmon(interface, action)
        self._print_tool_result(result, f"airmon-ng {action} {interface}")
        Prompt.ask("[bold bright_white]⏎ Premi invio per continuare[/bold bright_white]", default="")

    def airodump_menu(self):
        interface = Prompt.ask("[bold bright_white]🔌 Interfaccia monitor[/bold bright_white]", default="wlan0")
        output = Prompt.ask("[bold bright_white]💾 Prefisso output (optional)[/bold bright_white]", default="capture")
        extra = Prompt.ask("[bold bright_white]⚙️  Opzioni extra (optional)[/bold bright_white]", default="")
        result = self.air.run_airodump(interface, output, extra.strip() or None)
        self._print_tool_result(result, f"airodump-ng {interface}")
        Prompt.ask("[bold bright_white]⏎ Premi invio per continuare[/bold bright_white]", default="")

    def aireplay_menu(self):
        attack = Prompt.ask("[bold bright_white]⚡ Attacco aireplay-ng[/bold bright_white]", choices=["deauth", "fakeauth", "interactive"], default="deauth")
        interface = Prompt.ask("[bold bright_white]🔌 Interfaccia monitor[/bold bright_white]", default="wlan0")
        target = Prompt.ask("[bold bright_white]🎯 Target BSSID (se richiesto)[/bold bright_white]", default="")
        count = Prompt.ask("[bold bright_white]🔢 Numero di pacchetti (count)[/bold bright_white]", default="10")
        extra = Prompt.ask("[bold bright_white]⚙️  Opzioni extra (optional)[/bold bright_white]", default="")
        result = self.air.run_aireplay(interface, attack, target if target else None, int(count), extra.strip() or None)
        self._print_tool_result(result, f"aireplay-ng --{attack} {interface}")
        Prompt.ask("[bold bright_white]⏎ Premi invio per continuare[/bold bright_white]", default="")

    def aircrack_menu_run(self):
        capture = Prompt.ask("[bold bright_white]📁 File di cattura (.cap)[/bold bright_white]", default="capture.cap")
        wordlist = Prompt.ask("[bold bright_white]📖 Wordlist (optional)[/bold bright_white]", default="")
        extra = Prompt.ask("[bold bright_white]⚙️  Opzioni extra (optional)[/bold bright_white]", default="")
        result = self.air.run_aircrack(capture, wordlist.strip() or None, extra.strip() or None)
        self._print_tool_result(result, f"aircrack-ng {capture}")
        Prompt.ask("[bold bright_white]⏎ Premi invio per continuare[/bold bright_white]", default="")

    def wifi_menu(self):
        """Menu per gestione interfacce WiFi."""
        self.console.clear()
        while True:
            self.console.print(Panel("[bold bright_yellow]📡 WiFi Interface Manager[/bold bright_yellow]", style="yellow on black", border_style="bright_yellow"))
            submenu = Panel(
                "\n".join([
                    "[bold yellow]1)[/] 📋 Lista interfacce WiFi",
                    "[bold yellow]2)[/] 🔄 Cambia modalità (monitor/managed)",
                    "[bold yellow]3)[/] 🔙 Torna al menu principale"
                ]),
                title="[bold bright_yellow]WIFI SUBMENU[/bold bright_yellow]",
                border_style="bright_yellow",
                style="black on grey11"
            )
            self.console.print(submenu)
            choice = Prompt.ask("[bold bright_white]📡 Scegli un'opzione[/bold bright_white]", choices=["1", "2", "3"], default="1")
            if choice == "1":
                self.show_wifi_interfaces()
            elif choice == "2":
                self.change_wifi_mode()
            else:
                break

    def show_wifi_interfaces(self):
        interfaces = self.wifi.get_interfaces_summary()
        if not interfaces:
            self.console.print(Panel("[bold yellow]⚠️  Nessuna interfaccia WiFi trovata.[/bold yellow]", style="yellow on black", border_style="yellow"))
            Prompt.ask("[bold bright_white]⏎ Premi invio per continuare[/bold bright_white]", default="")
            return
        table = Table(show_header=True, header_style="bold bright_white on black", border_style="bright_yellow", style="white on black", title="[bold bright_yellow]📋 Interfacce WiFi[/bold bright_yellow]", title_style="bold bright_yellow")
        table.add_column("Interfaccia", style="cyan", justify="center")
        table.add_column("Tipo", style="green")
        table.add_column("Stato", style="magenta")
        for interface in interfaces:
            table.add_row(interface["name"], interface.get("type", "unknown"), interface.get("state", "unknown"))
        self.console.print(table)
        Prompt.ask("[bold bright_white]⏎ Premi invio per continuare[/bold bright_white]", default="")

    def change_wifi_mode(self):
        interface = Prompt.ask("[bold bright_white]🔌 Interfaccia wireless[/bold bright_white]", default="wlan0")
        mode = Prompt.ask("[bold bright_white]🔄 Modalità[/bold bright_white]", choices=["monitor", "managed"], default="monitor")
        result = self.wifi.set_mode(interface, mode)
        self._print_tool_result(result, f"Cambia modalità {interface} -> {mode}")
        Prompt.ask("[bold bright_white]⏎ Premi invio per continuare[/bold bright_white]", default="")

    def _print_tool_result(self, result: dict, title: str):
        if result["success"]:
            self.console.print(Panel(result["output"] or "[bold bright_green]✅ Operazione completata con successo![/bold bright_green]", title=f"[bold bright_green]✅ {title} SUCCESS[/bold bright_green]", border_style="green", style="green on black"))
        else:
            self.console.print(Panel(result["error"] or "Errore sconosciuto", title=f"[bold bright_red]❌ {title} FAILED[/bold bright_red]", border_style="red", style="red on black"))

    def view_last_output(self):
        self.console.clear()
        if not self.last_output:
            self.console.print(Panel("[bold yellow]⚠️  Nessuno output disponibile.[/bold yellow]", style="yellow on black", border_style="yellow"))
            Prompt.ask("[bold bright_white]⏎ Premi invio per tornare al menu[/bold bright_white]", default="")
            return
        self.console.print(Panel(self.last_output, title="[bold bright_magenta]📊 LAST OUTPUT[/bold bright_magenta]", border_style="bright_magenta", style="magenta on black"))
        save_choice = Confirm.ask("[bold bright_white]💾 Vuoi salvare questo output su file?[/bold bright_white]", default=False)
        if save_choice:
            filename = Prompt.ask("[bold bright_white]📁 Nome del file[/bold bright_white]", default="scan_output.txt")
            try:
                with open(filename, 'w') as f:
                    f.write(self.last_output)
                self.console.print(Panel(f"[bold bright_green]✅ Output salvato in {filename}[/bold bright_green]", style="green on black", border_style="green"))
            except Exception as e:
                self.console.print(Panel(f"[bold bright_red]❌ Errore nel salvataggio: {e}[/bold bright_red]", style="red on black", border_style="red"))
        Prompt.ask("[bold bright_white]⏎ Premi invio per tornare al menu[/bold bright_white]", default="")

    def show_settings(self):
        self.console.clear()
        import platform
        status_nmap = "[bright_green]✅ Installed[/bright_green]" if self.nmap.check_available() else "[bright_red]❌ Missing[/bright_red]"
        system_info = "\n".join([
            f"[bold bright_cyan]🖥️  Sistema:[/bold bright_cyan] {platform.system()} {platform.release()}",
            f"[bold bright_cyan]🐍 Python:[/bold bright_cyan] {platform.python_version()}",
            f"[bold bright_blue]🔍 Nmap:[/bold bright_blue] {status_nmap}",
            "[bold bright_green]🛰️  Aircrack suite:[/bold bright_green] [bright_green]✅ Enabled[/bright_green]",
            "[bold bright_yellow]📡 WiFi mode switching:[/bold bright_yellow] [bright_green]✅ Enabled[/bright_green]",
            "[bold bright_magenta]🔄 Aggiornamento automatico Git:[/bold bright_magenta] [bright_green]✅ Enabled[/bright_green]",
            "[bold bright_red]🔒 Root required:[/bold bright_red] [bright_green]✅ Enabled[/bright_green]"
        ])
        self.console.print(Panel(system_info, title="[bold bright_blue]⚙️  SYSTEM INFO & SETTINGS[/bold bright_blue]", border_style="bright_blue", style="blue on black"))

    def show_help(self):
        self.console.clear()
        help_text = "\n".join([
            "[bold bright_white]🚀 CDN FRAMEWORK HELP[/bold bright_white]",
            "",
            "[bold cyan]1) 🔍 Scan Nmap:[/bold cyan] scegli target, porte, tipo e opzioni extra.",
            "[bold green]2) 🛰️  Aircrack suite:[/bold green] airmon-ng, airodump-ng, aireplay-ng, aircrack-ng.",
            "[bold yellow]3) 📡 WiFi interfaces:[/bold yellow] lista ed switch managed/monitor.",
            "[bold magenta]4) 📊 Visualizza output:[/bold magenta] mostra l'ultimo risultato dello scan.",
            "[bold blue]5) ⚙️  Impostazioni:[/bold blue] stato dei tool installati.",
            "[bold white]6) 📝 Help:[/bold white] questo menu.",
            "[bold red]7) ❌ Exit:[/bold red] esci dal programma.",
            "",
            "[bold bright_red]⚠️  Tool rich red/black, eseguito solo con sudo.[/bold bright_red]",
            "[bold bright_green]🔄 Aggiornamento automatico: controlla origin/main al lancio.[/bold bright_green]",
            "",
            "[bold cyan]Comandi Nmap utili:[/bold cyan]",
            "  syn, connect, ping, udp, fin, null, xmas, version, os, aggressive, quick, intense",
            "",
            "[bold green]Esempi:[/bold green]",
            "  sudo python3 main.py scan 192.168.1.1 -ports 1-1000 -type syn -verbose",
            "  sudo python3 main.py wifi list",
            "  sudo python3 main.py airmon start wlan0"
        ])
        self.console.print(Panel(help_text, border_style="bright_white", style="white on black"))


if __name__ == '__main__':
    app = CDNTUISimple()
    app.run()