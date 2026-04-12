"""
GUI Tkinter: Interfaccia grafica moderna per CDN-FRAMEWORK
Dark theme con supporto per scan Nmap in tempo reale
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
from pathlib import Path
import queue

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.logger import setup_logger
from cli.commands import CLIParser, CommandInfo
from executor.executor import CommandExecutor
from modules.nmap.nmap_module import NmapModule

logger = setup_logger('CDN-GUI', log_level='INFO')


class CDNFrameworkGUI:
    """GUI moderna per CDN-FRAMEWORK"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CDN-FRAMEWORK - Gestore Scan Rete")
        self.root.geometry("1000x700")
        
        # Setup
        self.executor = CommandExecutor()
        self.nmap = NmapModule(self.executor)
        self.scan_in_progress = False
        self.output_queue = queue.Queue()
        
        # Tema dark
        self._setup_theme()
        self._create_widgets()
        
        # Aggiorna output da queue
        self.root.after(100, self._check_queue)
    
    def _setup_theme(self):
        """Configura tema dark professionale"""
        self.bg_primary = "#1e1e1e"
        self.bg_secondary = "#252526"
        self.fg_primary = "#ffffff"
        self.fg_secondary = "#a0a0a0"
        self.accent = "#007acc"
        self.error = "#f48771"
        self.success = "#4ec9b0"
        self.warning = "#dcdcaa"
        
        self.root.configure(bg=self.bg_primary)
        
        # Stile ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=self.bg_primary)
        style.configure('TLabel', background=self.bg_primary, foreground=self.fg_primary)
        style.configure('Header.TLabel', background=self.bg_primary, foreground=self.fg_primary, 
                       font=('Verdana', 12, 'bold'))
        style.configure('TButton', background=self.accent, foreground=self.fg_primary)
        style.configure('Accent.TButton', background=self.accent, foreground=self.fg_primary)
        style.map('TButton', background=[('active', '#005a9e')])
        
        # Entry style
        style.configure('TEntry', fieldbackground=self.bg_secondary, background=self.bg_secondary,
                       foreground=self.fg_primary, borderwidth=1)
    
    def _create_widgets(self):
        """Crea interfaccia grafica"""
        # Header
        self._create_header()
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel: Input
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self._create_input_panel(left_frame)
        
        # Right panel: Output + Log
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self._create_output_panel(right_frame)
    
    def _create_header(self):
        """Crea header con logo e info"""
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(header_frame, text="🔧 CDN-FRAMEWORK", 
                               style='Header.TLabel', font=('Verdana', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="Network Reconnaissance Tool",
                                  foreground=self.fg_secondary)
        subtitle_label.pack(side=tk.LEFT, padx=20)
        
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        
        self.status_label = ttk.Label(status_frame, text="● Pronto", 
                                      foreground=self.success)
        self.status_label.pack()
    
    def _create_input_panel(self, parent):
        """Crea panel input sinistra"""
        # Title
        title = ttk.Label(parent, text="Parametri Scan", style='Header.TLabel')
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame input
        input_frame = tk.Frame(parent, bg=self.bg_secondary, relief=tk.FLAT, bd=1)
        input_frame.pack(fill=tk.X, pady=5)
        
        # Target
        ttk.Label(parent, text="Target (IP/Hostname):").pack(anchor=tk.W, pady=(10, 5))
        self.target_entry = ttk.Entry(parent, width=40)
        self.target_entry.pack(fill=tk.X, pady=(0, 10))
        self.target_entry.insert(0, "localhost")
        
        # Porte
        ttk.Label(parent, text="Porte:").pack(anchor=tk.W, pady=(0, 5))
        ports_frame = ttk.Frame(parent)
        ports_frame.pack(fill=tk.X, pady=(0, 10))
        
        hint_label = tk.Label(ports_frame, text="Es: 22,80,443 o 1-1000", 
                             fg=self.fg_secondary, bg=self.bg_primary, font=('Verdana', 9))
        hint_label.pack(side=tk.LEFT)
        self.ports_entry = ttk.Entry(ports_frame, width=20)
        self.ports_entry.pack(side=tk.RIGHT)
        self.ports_entry.insert(0, "22,80,443")
        
        # Tipo scan
        ttk.Label(parent, text="Tipo Scan:").pack(anchor=tk.W, pady=(0, 5))
        self.scan_type_var = tk.StringVar(value="syn")
        scan_types = ttk.Frame(parent)
        scan_types.pack(fill=tk.X, pady=(0, 10))
        
        for scan_type in ["syn", "connect", "ping"]:
            ttk.Radiobutton(scan_types, text=scan_type.upper(), variable=self.scan_type_var, 
                           value=scan_type).pack(side=tk.LEFT, padx=5)
        
        # Opzioni
        ttk.Label(parent, text="Opzioni:").pack(anchor=tk.W, pady=(0, 5))
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.verbose_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Verbose", variable=self.verbose_var).pack(side=tk.LEFT)
        
        self.xml_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Formato XML", variable=self.xml_var).pack(side=tk.LEFT, padx=20)
        
        # Pulsanti
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.scan_button = ttk.Button(btn_frame, text="🔍 Avvia Scan", command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.clear_button = ttk.Button(btn_frame, text="🗑️  Cancella", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar
        ttk.Label(parent, text="Progresso:").pack(anchor=tk.W, pady=(15, 5))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)
        
        # Info sezione
        info_frame = tk.Frame(parent, bg=self.bg_secondary, relief=tk.FLAT, bd=1)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        info_label = ttk.Label(info_frame, text="📖 Informazioni", style='Header.TLabel')
        info_label.pack(anchor=tk.W, padx=10, pady=10)
        
        info_text = """
• SYN Scan: Scan veloce (richiede sudo)
• Connect: Scan standard senza sudo
• Ping: Verifica semplice host

⚠️  Installa Nmap:
  sudo apt install nmap

📝 Tip: Usa CIDR per reti:
  192.168.1.0/24
        """
        
        info_display = tk.Label(info_frame, text=info_text, justify=tk.LEFT, 
                               fg=self.fg_secondary, bg=self.bg_secondary, 
                               font=('Courier', 9))
        info_display.pack(anchor=tk.NW, padx=10, pady=10)
    
    def _create_output_panel(self, parent):
        """Crea panel output destra"""
        # Tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Output
        output_frame = ttk.Frame(self.notebook)
        self.notebook.add(output_frame, text="📊 Output Scan")
        self._create_output_tab(output_frame)
        
        # Tab 2: Log
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📝 Log Sistema")
        self._create_log_tab(log_frame)
        
        # Tab 3: Help
        help_frame = ttk.Frame(self.notebook)
        self.notebook.add(help_frame, text="❓ Help")
        self._create_help_tab(help_frame)
    
    def _create_output_tab(self, parent):
        """Tab risultati scan"""
        ttk.Label(parent, text="Risultati Scan Nmap:", style='Header.TLabel').pack(anchor=tk.W, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20,
                                                     bg=self.bg_secondary, fg=self.fg_primary,
                                                     font=('Courier', 9), insertbackground=self.accent)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tag per colori
        self.output_text.tag_config('success', foreground=self.success)
        self.output_text.tag_config('error', foreground=self.error)
        self.output_text.tag_config('warning', foreground=self.warning)
        self.output_text.tag_config('info', foreground=self.accent)
    
    def _create_log_tab(self, parent):
        """Tab log sistema"""
        ttk.Label(parent, text="Log Attività Sistema:", style='Header.TLabel').pack(anchor=tk.W, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20,
                                                   bg=self.bg_secondary, fg=self.fg_secondary,
                                                   font=('Courier', 8), insertbackground=self.accent)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tag colori log
        self.log_text.tag_config('debug', foreground="#808080")
        self.log_text.tag_config('info', foreground=self.accent)
        self.log_text.tag_config('warning', foreground=self.warning)
        self.log_text.tag_config('error', foreground=self.error)
    
    def _create_help_tab(self, parent):
        """Tab help"""
        help_text = tk.Text(parent, wrap=tk.WORD, bg=self.bg_secondary, 
                           fg=self.fg_primary, font=('Verdana', 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
🔧 CDN-FRAMEWORK - Guida Rapida

█ COSA PUOI FARE:
  • Eseguire scan Nmap su host singoli
  • Scansioni di reti CIDR (192.168.1.0/24)
  • Scegliere tipo di scan (SYN, Connect, Ping)
  • Specificare porte personalizzate
  • Visualizzare risultati in real-time
  • Salvare output (prossima release)

█ PARAMETRI:

  TARGET: Indirizzo IP, hostname o CIDR
  Esempi: 
    - 192.168.1.1
    - localhost
    - 192.168.1.0/24

  PORTE: Range singole o comma-separated
  Esempi:
    - 22,80,443
    - 1-1000
    - 1-65535

  TIPO SCAN:
    • SYN: Veloce, accurato (richiede sudo)
    • CONNECT: Standard, senza root
    • PING: Solo verifica disponibilità

  OPZIONI:
    • Verbose: Output dettagliato
    • XML: Output in formato XML

█ PREREQUISITI:

  1. Installa Nmap:
     sudo apt install nmap

  2. Per SYN scan, esegui con sudo:
     sudo python3 gui.py

█ COMANDI TERMINALE EQUIVALENTI:

  # CLI versione
  python3 main.py scan 192.168.1.1 -ports 22,80

  # SYN scan
  sudo python3 main.py scan 192.168.1.1 -type syn

█ TIPS & TRICKS:

  • SYN è il più veloce ma richiede root
  • Per reti intere usa CIDR: 192.168.1.0/24
  • Scan rapido? Usa tipo PING first
  • Output XML salvabile (feature prossima)

█ TROUBLESHOOTING:

  ❌ "nmap: command not found"
     → sudo apt install nmap

  ❌ "Operation not permitted"
     → SYN scan richiede root: sudo python3 gui.py

  ❌ Timeout
     → Target potrebbe essere offline
     → Prova con range porte più piccolo

  ❌ Permission denied
     → File log directory: mkdir -p logs

█ CONTATTI & INFO:

  Versione: 1.0.0
  GitHub: https://github.com/GAETAL2025/CDN-FRAMEWORK
  Author: GAETAL2025

Domande? Vedi README.md nel progetto!
"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, command=help_text.yview)
        help_text.config(yscroll=scrollbar.set)
    
    def start_scan(self):
        """Avvia scan in thread separato"""
        if self.scan_in_progress:
            messagebox.showwarning("Attenzione", "Scan già in corso!")
            return
        
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Errore", "Specifica un target!")
            return
        
        self.scan_in_progress = True
        self.scan_button.config(state=tk.DISABLED)
        self.status_label.config(text="● Scan in corso...", foreground=self.warning)
        self.output_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        # Avvia thread
        thread = threading.Thread(target=self._scan_thread, args=(target,), daemon=True)
        thread.start()
    
    def _scan_thread(self, target):
        """Esegui scan in background"""
        try:
            params = {
                'target': target,
                'ports': self.ports_entry.get() or None,
                'type': self.scan_type_var.get(),
                'verbose': self.verbose_var.get(),
                'output_format': 'xml' if self.xml_var.get() else 'text'
            }
            
            self.output_queue.put(('log', f'[INFO] Inizio scan su {target}...'))
            self.progress_var.set(25)
            
            result = self.nmap.scan(target, params)
            
            self.progress_var.set(75)
            
            if result['success']:
                self.output_queue.put(('output', f"✅ Scan Completato!\n\n{result['output']}"))
                self.output_queue.put(('log', f"[SUCCESS] Scan terminato con successo"))
                self.output_queue.put(('status', ('success', '● Completato')))
                self.progress_var.set(100)
            else:
                self.output_queue.put(('output', f"❌ Errore Scan:\n\n{result['error']}"))
                self.output_queue.put(('log', f"[ERROR] {result['error']}"))
                self.output_queue.put(('status', ('error', '● Errore')))
        
        except Exception as e:
            self.output_queue.put(('output', f"❌ Eccezione:\n\n{str(e)}"))
            self.output_queue.put(('log', f"[ERROR] Eccezione: {str(e)}"))
            self.output_queue.put(('status', ('error', '● Errore')))
        
        finally:
            self.scan_in_progress = False
            self.output_queue.put(('button_enable', None))
    
    def _check_queue(self):
        """Controlla output queue"""
        try:
            while True:
                msg_type, data = self.output_queue.get_nowait()
                
                if msg_type == 'output':
                    self.output_text.insert(tk.END, data)
                    self.output_text.see(tk.END)
                
                elif msg_type == 'log':
                    if '[ERROR]' in data:
                        tag = 'error'
                    elif '[WARNING]' in data:
                        tag = 'warning'
                    elif '[SUCCESS]' in data:
                        tag = 'success'
                    else:
                        tag = 'info'
                    
                    self.log_text.insert(tk.END, data + '\n', tag)
                    self.log_text.see(tk.END)
                
                elif msg_type == 'status':
                    color, text = data
                    color_map = {
                        'success': self.success,
                        'error': self.error,
                        'warning': self.warning
                    }
                    self.status_label.config(text=text, foreground=color_map.get(color, self.accent))
                
                elif msg_type == 'button_enable':
                    self.scan_button.config(state=tk.NORMAL)
        
        except queue.Empty:
            pass
        
        # Richiedi prossimo check
        self.root.after(100, self._check_queue)
    
    def clear_output(self):
        """Cancella output"""
        self.output_text.delete(1.0, tk.END)
        self.progress_var.set(0)


def main():
    """Punto di ingresso GUI"""
    root = tk.Tk()
    app = CDNFrameworkGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
