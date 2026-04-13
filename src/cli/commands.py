"""
CLI Commands: Interpreta e gestisce i comandi inseriti dall'utente
Supporta: scan, wifi, help
"""

import logging
from typing import Dict, Callable, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CommandInfo:
    """Informazioni su un comando"""
    name: str
    description: str
    handler: Callable
    args_required: List[str] = None
    args_optional: List[str] = None
    
    def __post_init__(self):
        if self.args_required is None:
            self.args_required = []
        if self.args_optional is None:
            self.args_optional = []


class CLIParser:
    """Interpreta comando e argomenti da linea di comando"""
    
    def __init__(self):
        self.commands: Dict[str, CommandInfo] = {}
    
    def register_command(self, info: CommandInfo):
        """Registra un nuovo comando"""
        self.commands[info.name] = info
        logger.info(f"Comando registrato: {info.name}")
    
    def parse(self, args: List[str]) -> tuple[Optional[str], Optional[Dict]]:
        """
        Interpreta argomenti da terminale
        
        Args:
            args: Lista di argomenti (es: ['scan', '192.168.1.1', '-p', '22,80'])
        
        Returns:
            Tupla (comando, dizionario parametri)
        """
        if not args:
            return None, None
        
        command_name = args[0].lower()
        
        if command_name not in self.commands:
            logger.error(f"Comando sconosciuto: {command_name}")
            return None, None
        
        cmd_info = self.commands[command_name]
        
        # Valida argomenti obbligatori
        params = self._parse_params(args[1:], cmd_info)
        
        if params is None:
            return None, None
        
        return command_name, params
    
    def _parse_params(self, args: List[str], cmd_info: CommandInfo) -> Optional[Dict]:
        """Estrae parametri da lista di argomenti"""
        params = {}
        i = 0
        
        # Prendi argomenti posizionali obbligatori
        for required_arg in cmd_info.args_required:
            if i >= len(args):
                logger.error(f"Argomento obbligatorio mancante: {required_arg}")
                return None
            params[required_arg] = args[i]
            i += 1
        
        # Prendi flag opzionali
        while i < len(args):
            if args[i].startswith('-'):
                flag_name = args[i].lstrip('-')
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    params[flag_name] = args[i + 1]
                    i += 2
                else:
                    params[flag_name] = True
                    i += 1
            else:
                i += 1
        
        return params
    
    def get_help(self, command_name: Optional[str] = None) -> str:
        """Restituisce help per un comando specifico o generale"""
        if command_name and command_name in self.commands:
            cmd = self.commands[command_name]
            return f"""
{cmd.name}: {cmd.description}
Argomenti obbligatori: {', '.join(cmd.args_required) if cmd.args_required else 'Nessuno'}
Argomenti opzionali: {', '.join(cmd.args_optional) if cmd.args_optional else 'Nessuno'}
"""
        
        help_text = "\n=== NetHunterCDN ===\nComandi disponibili:\n"
        for cmd_name, cmd_info in self.commands.items():
            help_text += f"  {cmd_name}: {cmd_info.description}\n"
        return help_text
