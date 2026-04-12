"""
TUI Semplice (Alternative): Menu interattivo con rich
Versione leggera senza dipendenze pesanti
"""

import sys
from pathlib import Path
import threading
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.align import Align
from rich.text import Text as RichText
from rich.layout import Layout
from rich import print as rprint

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.logger import setup_logger
from executor.executor import CommandExecutor
from modules.nmap.nmap_module import NmapModule

logger = setup_logger('CDN-TUI-SIMPLE', log_level='INFO')


class CDNTUISimple:
    """TUI semplice tipo Metasploit con Rich"""
    
    def __init__(self):
        self.console = Console()
        self.executor = CommandExecutor()
        self.nmap = NmapModule(self.executor)
        self.last_output = None
    
    def print_header(self):
        """Mostra header"""
        header = """
[bold cyan]
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  🔧 [bold magenta]CDN-FRAMEWORK[/][bold cyan] - TUI Scanner                    ║
║                                                           ║
║  Network Reconnaissance Tool                             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
[/]
        """
        self.console.print(header)
    
    def print_menu(self):
        """Mostra menu principale"""
        menu = """
[bold yellow]┌─ MAIN MENU ─────────────────────────────────────────┐[/]
[yellow]│[/]
[yellow]│  [bold]1)[/] 🔍 Start Scan          Esegui uno scan Nmap
[yellow]│  [bold]2)[/] 📊 View Last Output    Mostra ultimo risultato
[yellow]│  [bold]3)[/] ⚙️  Settings           Configura parametri
[yellow]│  [bold]4)[/] 📝 Help                Mostra aiuto
[yellow]│  [bold]5)[/] ❌ Exit                Esci dal programma
[yellow]│[/]
[yellow]└──────────────────────────────────────────────────────┘[/]
        """
        self.console.print(menu)
    
    def get_menu_choice(self) -> str:
        """Leggi scelta menu"""
        while True:
            choice = Prompt.ask("[bold cyan]Select option[/]", choices=["1", "2", "3", "4", "5"])
            return choice
    
    def start_scan(self):
        """Menu scan"""
        self.console.print("\n[bold cyan]┌─ NEW SCAN ───────────────────────────────────┐[/]")
        
        # Target
        target = Prompt.ask("[bold]Target[/]", default="localhost")
        if not target:
            self.console.print("[red]❌ Target non specificato![/]")
            return
        
        # Ports
        ports = Prompt.ask("[bold]Ports[/]", default="22,80,443")
        
        # Scan Type
        scan_type = Prompt.ask(
            "[bold]Scan Type[/]",
            choices=["syn", "connect", "ping"],
            default="syn"
        )
        
        # Verbose
        verbose = Confirm.ask("[bold]Verbose output?[/]", default=False)
        
        self.console.print("[yellow]└─────────────────────────────────────────────┘[/]\n")
        
        # Esegui scan
        self._execute_scan(target, ports, scan_type, verbose)
    
    def _execute_scan(self, target: str, ports: str, scan_type: str, verbose: bool):
        """Esegui scan con progress bar"""
        self.console.print(f"\n[bold cyan]🔍 Scansione {target}...[/]\n")
        
        params = {
            'ports': ports if ports else None,
            'type': scan_type,
            'verbose': verbose
        }
        
        # Progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Scanning...", total=100)
            
            # Esegui in thread
            result = [None]
            
            def scan_thread():
                result[0] = self.nmap.scan(target, params)
                progress.update(task, completed=100)
            
            thread = threading.Thread(target=scan_thread, daemon=True)
            thread.start()
            
            # Simula progress
            for i in range(100):
                if result[0] is not None:
                    break
                progress.update(task, advance=1)
                time.sleep(0.05)
            
            thread.join(timeout=120)
        
        # Mostra risultati
        if result[0]:
            scan_result = result[0]
            if scan_result['success']:
                self.last_output = scan_result['output']
                
                # Panel risultati
                output_panel = Panel(
                    scan_result['output'],
                    title=f"[bold green]✅ SCAN COMPLETE - {target}[/]",
                    border_style="green",
                    expand=True
                )
                self.console.print(output_panel)
                
                self.console.print("[green]✅ Scan completato con successo![/]\n")
            else:
                error_panel = Panel(
                    scan_result['error'],
                    title="[bold red]❌ SCAN FAILED[/]",
                    border_style="red",
                    expand=True
                )
                self.console.print(error_panel)
                self.console.print(f"[red]❌ Errore: {scan_result['error']}[/]\n")
    
    def view_last_output(self):
        """Mostra ultimo output"""
        if not self.last_output:
            self.console.print("[yellow]⚠️  Nessuno output disponibile![/]\n")
            return
        
        panel = Panel(
            self.last_output,
            title="[bold blue]📊 LAST OUTPUT[/]",
            border_style="blue",
            expand=True
        )
        self.console.print(panel)
        self.console.print()
    
    def show_settings(self):
        """Mostra/modifica settings"""
        settings = """
[bold cyan]⚙️  AVAILABLE SETTINGS
[/]
[yellow]Nmap Module:[/]
  • Version: 1.0.0
  • Status: """
        
        if self.nmap.check_available():
            settings += "[green]✅ Installed[/]"
        else:
            settings += "[red]❌ Not installed[/]"
        
        settings += """

[yellow]Scan Options:[/]
  • Default Ports: 22,80,443
  • Default Type: SYN
  • Timeout: Disabled

[yellow]Output Format:[/]
  • Text: Enabled
  • XML: Available (use -output xml)

[yellow]Tips:[/]
  • Use CIDR notation: 192.168.1.0/24
  • SYN scan requires root/sudo
  • Large port ranges increase scan time
        """
        
        panel = Panel(settings, title="[bold green]⚙️  SETTINGS[/]", border_style="green")
        self.console.print(panel)
        self.console.print()
    
    def show_help(self):
        """Mostra help completo"""
        help_text = """
[bold cyan]CDN-FRAMEWORK - HELP[/]

[bold yellow]SCAN TYPES:[/]
  [bold]SYN Scan[/]
    • Veloce e accurato
    • Richiede permessi root (sudo)
    • Consigliato per scans accurati

  [bold]Connect Scan[/]
    • Scan standard
    • Funziona senza root
    • Leggermente più lento di SYN

  [bold]Ping Scan[/]
    • Solo verifica disponibilità
    • Molto veloce
    • Útile per host discovery

[bold yellow]PORT SPECIFICATIONS:[/]
  • Singola porta: 22
  • Multiple porte: 22,80,443
  • Range: 1-1000
  • Mix: 22,80-443,3306

[bold yellow]TARGET FORMATS:[/]
  • Singolo IP: 192.168.1.1
  • Hostname: example.com
  • CIDR Network: 192.168.1.0/24
  • IP Range: 192.168.1.1-50

[bold yellow]EXAMPLES:[/]
  $ ./tui.py    # Avvia TUI
  $ main.py scan 192.168.1.1 -ports 22,80
  $ main.py scan example.com -type syn -verbose

[bold yellow]PREREQUISITES:[/]
  • Nmap: sudo apt install nmap
  • Python 3.8+
  • rich: pip install rich

[bold yellow]TIPS:[/]
  • Use 'View Last Output' per scorrere risultati
  • Large scans possono richiedere tempo
  • CIDR /24 = 256 hosts
  • Add -verbose per più dettagli
        """
        
        panel = Panel(help_text, title="[bold cyan]ℹ️  HELP[/]", border_style="cyan")
        self.console.print(panel)
        self.console.print()
    
    def run(self):
        """Main loop"""
        self.print_header()
        
        # Check Nmap
        if self.nmap.check_available():
            self.console.print("[green]✅ Nmap disponibile[/]\n")
        else:
            self.console.print("[yellow]⚠️  Nmap non installato. Installa: sudo apt install nmap[/]\n")
        
        while True:
            self.print_menu()
            choice = self.get_menu_choice()
            
            if choice == "1":
                self.start_scan()
            elif choice == "2":
                self.view_last_output()
            elif choice == "3":
                self.show_settings()
            elif choice == "4":
                self.show_help()
            elif choice == "5":
                self.console.print("[bold yellow]Goodbye! 👋[/]\n")
                break
            
            input("\nPress [Enter] per continuare...")
            self.console.clear()


def main():
    """Punto di ingresso"""
    try:
        tui = CDNTUISimple()
        tui.run()
    except KeyboardInterrupt:
        print("\n\n[red]❌ Interrupted by user[/]")
        sys.exit(0)


if __name__ == '__main__':
    main()
