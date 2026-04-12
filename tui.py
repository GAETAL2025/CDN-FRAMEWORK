"""
TUI (Text User Interface): Interfaccia terminale professionale tipo Metasploit
Usa textual per componenti interattivi nel terminale
"""

from textual.app import ComposeResult, SystemCommand
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Input, Label, Static, TextArea, OptionList
from textual.binding import Binding
from textual.screen import Screen
from textual.app import App
from textual.widgets import Header, Footer, Text
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.align import Align
from rich.text import Text as RichText
import sys
from pathlib import Path
import threading
import time

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.logger import setup_logger
from executor.executor import CommandExecutor
from modules.nmap.nmap_module import NmapModule

logger = setup_logger('CDN-TUI', log_level='INFO')


class ScanForm(Static):
    """Form per parametri scan"""
    
    def compose(self) -> ComposeResult:
        yield Label("🎯 [bold cyan]TARGET[/] (IP/Hostname/CIDR)")
        yield Input(id="target_input", placeholder="es: 192.168.1.1")
        
        yield Label("\n📌 [bold cyan]PORTE[/] (es: 22,80,443 o 1-1000)")
        yield Input(id="ports_input", placeholder="es: 22,80,443", value="22,80,443")
        
        yield Label("\n🔍 [bold cyan]TIPO SCAN[/]")
        yield OptionList(
            ("SYN Scan (veloce)", "syn"),
            ("Connect Scan", "connect"),
            ("Ping Scan", "ping"),
            id="scan_type"
        )
        
        yield Label("\n⚙️ [bold cyan]OPZIONI[/]")
        yield Input(id="verbose", placeholder="verbose (true/false)", value="false")


class OutputPanel(Static):
    """Panel per visualizzare output"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.output_text = ""
    
    def render(self):
        if not self.output_text:
            return Panel("[dim]Output scans apparirà qui...[/]", 
                        title="📊 OUTPUT", border_style="blue")
        return Panel(self.output_text, title="📊 OUTPUT", border_style="green", expand=False)
    
    def update_output(self, text: str):
        self.output_text = text
        self.refresh()


class LogPanel(Static):
    """Panel per log sistema"""
    
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def render(self):
        log_text = "\n".join(self.logs[-10:])  # Ultimi 10 log
        if not log_text:
            return Panel("[dim]Log attività...[/]", title="📝 LOG", border_style="blue")
        return Panel(log_text, title="📝 LOG", border_style="yellow", max_height=8)
    
    def add_log(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        
        if level == "ERROR":
            log_msg = f"[red]{timestamp} [ERROR][/] {message}"
        elif level == "SUCCESS":
            log_msg = f"[green]{timestamp} [SUCCESS][/] {message}"
        elif level == "WARNING":
            log_msg = f"[yellow]{timestamp} [WARNING][/] {message}"
        else:
            log_msg = f"[cyan]{timestamp} [INFO][/] {message}"
        
        self.logs.append(log_msg)
        self.refresh()


class CDNTUIScreen(Screen):
    """Screen principale TUI"""
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Vertical():
            # Title
            yield Label("[bold cyan]═══════════════════════════════════════════════════════[/]")
            yield Label("[bold magenta]🔧 CDN-FRAMEWORK - TUI Scanner[/]")
            yield Label("[dim]Network Reconnaissance Tool[/]")
            yield Label("[bold cyan]═══════════════════════════════════════════════════════[/]\n")
            
            # Main content
            with Horizontal():
                # Left panel: Form
                with Vertical(id="left_panel"):
                    yield Label("[bold cyan]⚙️  PARAMETRI SCAN[/]")
                    self.form = ScanForm(id="scan_form")
                    yield self.form
                
                # Right panels: Output + Log
                with Vertical(id="right_panel"):
                    self.output_panel = OutputPanel(id="output")
                    yield self.output_panel
                    
                    self.log_panel = LogPanel(id="logs")
                    yield self.log_panel
            
            # Buttons
            with Horizontal(id="button_panel"):
                yield Button("🔍 START SCAN", id="scan_button", variant="primary")
                yield Button("🗑️  CLEAR", id="clear_button")
                yield Button("ℹ️  HELP", id="help_button")
                yield Button("❌ QUIT", id="quit_button")
        
        yield Footer()
    
    def on_mount(self):
        """Setup iniziale"""
        self.executor = CommandExecutor()
        self.nmap = NmapModule(self.executor)
        
        # Mostra info iniziale
        self.log_panel.add_log("CDN-FRAMEWORK TUI inizializzato", "INFO")
        
        # Verifica Nmap
        if self.nmap.check_available():
            self.log_panel.add_log("Nmap disponibile", "SUCCESS")
        else:
            self.log_panel.add_log("Nmap non disponibile! Installa: sudo apt install nmap", "ERROR")
    
    def on_button_pressed(self, event: Button.Pressed):
        """Gestisci click pulsanti"""
        button_id = event.button.id
        
        if button_id == "scan_button":
            self.start_scan()
        elif button_id == "clear_button":
            self.clear_output()
        elif button_id == "help_button":
            self.show_help()
        elif button_id == "quit_button":
            self.app.exit()
    
    def start_scan(self):
        """Avvia scan"""
        target_input = self.query_one("#target_input", Input)
        target = target_input.value.strip()
        
        if not target:
            self.log_panel.add_log("Specifica un target!", "ERROR")
            return
        
        ports_input = self.query_one("#ports_input", Input)
        ports = ports_input.value or "22,80,443"
        
        # Tipo scan
        scan_type_option = self.query_one("#scan_type", OptionList)
        if scan_type_option.highlighted is not None:
            scan_type = scan_type_option.highlighted
        else:
            scan_type = "syn"
        
        # Verbose
        verbose_input = self.query_one("#verbose", Input)
        verbose = verbose_input.value.lower() == "true"
        
        self.log_panel.add_log(f"Inizio scan su {target}...", "INFO")
        
        # Esegui in thread
        thread = threading.Thread(
            target=self._scan_thread, 
            args=(target, ports, scan_type, verbose),
            daemon=True
        )
        thread.start()
    
    def _scan_thread(self, target: str, ports: str, scan_type: str, verbose: bool):
        """Esegui scan in background"""
        try:
            params = {
                'ports': ports if ports else None,
                'type': scan_type,
                'verbose': verbose
            }
            
            result = self.nmap.scan(target, params)
            
            if result['success']:
                self.output_panel.update_output(result['output'])
                self.log_panel.add_log("Scan completato!", "SUCCESS")
            else:
                self.output_panel.update_output(f"❌ ERRORE:\n{result['error']}")
                self.log_panel.add_log(f"Scan fallito: {result['error']}", "ERROR")
        
        except Exception as e:
            self.output_panel.update_output(f"❌ ECCEZIONE:\n{str(e)}")
            self.log_panel.add_log(str(e), "ERROR")
    
    def clear_output(self):
        """Cancella output"""
        self.output_panel.output_text = ""
        self.output_panel.refresh()
        self.log_panel.add_log("Output cancellato", "INFO")
    
    def show_help(self):
        """Mostra help"""
        help_text = """
CDN-FRAMEWORK - Network Reconnaissance Tool

PARAMETERS:
  TARGET: IP, hostname o CIDR (es: 192.168.1.1)
  PORTE: Range (es: 22,80,443 o 1-1000)
  SCAN TYPE: SYN, Connect, Ping
  
SCAN TYPES:
  • SYN: Veloce, accurato (richiede root)
  • CONNECT: Standard, senza root
  • PING: Verifica semplice disponibilità

SHORTCUTS:
  Q: Quit | CTRL+C: Exit
        """
        self.output_panel.update_output(help_text)
        self.log_panel.add_log("Help mostrato", "INFO")


class CDNFrameworkTUI(App):
    """App principale TUI"""
    
    TITLE = "CDN-FRAMEWORK TUI"
    SUBTITLE = "Network Reconnaissance Tool"
    
    CSS = """
    Screen {
        background: $panel;
    }
    
    #left_panel {
        width: 40%;
        height: 100%;
        border: solid $accent;
    }
    
    #right_panel {
        width: 60%;
        height: 100%;
    }
    
    #output {
        height: 60%;
        margin: 1;
    }
    
    #logs {
        height: 20%;
        margin: 1;
    }
    
    #button_panel {
        height: auto;
        margin: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    Input {
        margin: 0 1 1 1;
    }
    
    Label {
        margin: 0 1;
    }
    """
    
    def on_mount(self):
        self.push_screen(CDNTUIScreen())


def main():
    """Punto di ingresso TUI"""
    app = CDNFrameworkTUI()
    app.run()


if __name__ == '__main__':
    main()
