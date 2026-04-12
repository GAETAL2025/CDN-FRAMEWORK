#!/bin/bash
# Quick Start Script per CDN-FRAMEWORK

echo "🔧 CDN-FRAMEWORK - Quick Start"
echo "=============================="
echo ""

# Verifica Nmap
echo "1️⃣  Verifica Nmap..."
if ! command -v nmap &> /dev/null; then
    echo "❌ Nmap non installato"
    echo "   Installa con: sudo apt install nmap"
    exit 1
fi
echo "✅ Nmap trovato"
echo ""

# Verifica Python
echo "2️⃣  Verifica Python 3.8+..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION trovato"
echo ""

# Test suite
echo "3️⃣  Esegui test suite..."
python3 test.py
echo ""

# CLI esempio
echo "4️⃣  Prova CLI..."
echo "   Comando: python3 main.py scan localhost -ports 22"
echo "   Info: python3 main.py help"
echo ""

# GUI
echo "5️⃣  Interfaccia Grafica (GUI)..."
echo "   Comando: python3 gui.py"
echo "   ⚠️  Nota: Richiede display grafico (X11/Wayland)"
echo ""

echo "════════════════════════════════════════════════"
echo "✅ Setup completato!"
echo ""
echo "📖 Consulta README.md per documentazione"
echo "📊 Vedi MILESTONE.md per status del progetto"
echo "🐙 GitHub: https://github.com/GAETAL2025/CDN-FRAMEWORK"
