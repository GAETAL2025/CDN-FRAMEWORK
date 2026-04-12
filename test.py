"""
Test per CDN-FRAMEWORK
Testa: CLI parsing, Executor, Nmap Module
"""

import sys
from pathlib import Path

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.logger import setup_logger
from cli.commands import CLIParser, CommandInfo
from executor.executor import CommandExecutor
from modules.nmap.nmap_module import NmapModule

logger = setup_logger('CDN-TEST', log_level='DEBUG')


def test_executor():
    """Test 1: Executor - esecuzione comandi shell"""
    print("\n" + "="*60)
    print("TEST 1: EXECUTOR")
    print("="*60)
    
    executor = CommandExecutor()
    
    # Test comando semplice
    stdout, stderr, code = executor.execute("echo 'Test executor'")
    print(f"Comando: echo 'Test executor'")
    print(f"Output: {stdout}")
    print(f"Return code: {code}")
    assert code == 0, "Executor fallito"
    print("✅ Test executor PASSATO")


def test_cli_parser():
    """Test 2: CLI Parser - parsing comandi"""
    print("\n" + "="*60)
    print("TEST 2: CLI PARSER")
    print("="*60)
    
    parser = CLIParser()
    
    # Registra comando di test
    parser.register_command(CommandInfo(
        name="test",
        description="Comando di test",
        args_required=["arg1"],
        args_optional=["arg2"],
        handler=lambda x: None
    ))
    
    # Test parsing
    cmd, params = parser.parse(["test", "value1", "-flag", "value2"])
    print(f"Input: ['test', 'value1', '-flag', 'value2']")
    print(f"Comando: {cmd}")
    print(f"Parametri: {params}")
    
    assert cmd == "test", "Comando non corretto"
    assert params["arg1"] == "value1", "Argomento posizionale non estratto"
    assert params.get("flag") == "value2", "Flag non estratto"
    print("✅ Test CLI parser PASSATO")


def test_nmap_command_building():
    """Test 3: Nmap Module - costruzione comando"""
    print("\n" + "="*60)
    print("TEST 3: NMAP COMMAND BUILDING")
    print("="*60)
    
    executor = CommandExecutor()
    nmap = NmapModule(executor)
    
    # Test costruzione comando
    params = {
        'type': 'syn',
        'ports': '22,80,443',
        'verbose': True
    }
    
    cmd = nmap._build_command('192.168.1.1', params)
    print(f"Target: 192.168.1.1")
    print(f"Parametri: {params}")
    print(f"Comando generato: {cmd}")
    
    assert 'nmap' in cmd, "Comando non contiene 'nmap'"
    assert '-sS' in cmd, "Comando non contiene '-sS' (SYN scan)"
    assert '192.168.1.1' in cmd, "Target non nel comando"
    print("✅ Test Nmap command building PASSATO")


def test_nmap_availability():
    """Test 4: Nmap - verifica disponibilità"""
    print("\n" + "="*60)
    print("TEST 4: NMAP AVAILABILITY")
    print("="*60)
    
    executor = CommandExecutor()
    nmap = NmapModule(executor)
    
    available = nmap.check_available()
    print(f"Nmap disponibile: {available}")
    
    if available:
        print("✅ Test Nmap availability PASSATO (Nmap installato)")
    else:
        print("⚠️  Nmap non installato - usa: sudo apt install nmap")


def test_help_command():
    """Test 5: Help command"""
    print("\n" + "="*60)
    print("TEST 5: HELP COMMAND")
    print("="*60)
    
    parser = CLIParser()
    parser.register_command(CommandInfo(
        name="scan",
        description="Esegui scan",
        handler=lambda x: None
    ))
    
    help_text = parser.get_help()
    print(help_text)
    assert "scan" in help_text, "Comando non nel help"
    print("✅ Test help command PASSATO")


def test_invalid_input():
    """Test 6: Input non valido"""
    print("\n" + "="*60)
    print("TEST 6: INVALID INPUT")
    print("="*60)
    
    executor = CommandExecutor()
    
    # Comando che non esiste
    stdout, stderr, code = executor.execute("nonexistent_command_xyzabc")
    print(f"Comando inesistente eseguito")
    print(f"Return code: {code}")
    assert code != 0, "Dovrebbe fallire"
    print("✅ Test invalid input PASSATO")


def run_all_tests():
    """Esegui tutti i test"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🧪 CDN-FRAMEWORK TEST SUITE 🧪" + " "*12 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Executor", test_executor),
        ("CLI Parser", test_cli_parser),
        ("Nmap Command Building", test_nmap_command_building),
        ("Nmap Availability", test_nmap_availability),
        ("Help Command", test_help_command),
        ("Invalid Input", test_invalid_input),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test FALLITO: {name}")
            print(f"   Errore: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test ERRORE: {name}")
            print(f"   Eccezione: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RISULTATI: {passed} passati, {failed} falliti")
    print("="*60 + "\n")


if __name__ == '__main__':
    run_all_tests()
