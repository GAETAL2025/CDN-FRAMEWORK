#!/bin/bash
# CDN-FRAMEWORK - GitHub Push Script
# Usa questo script per fare il push su GitHub

set -e

cd /home/ghost/Scrivania/CDN-FRAMEWORK

echo "🚀 CDN-FRAMEWORK - Push su GitHub"
echo "=================================="

# Verifica status
echo ""
echo "📝 Status attuale:"
git status

# Verifica remote
echo ""
echo "🔗 Remote configurato:"
git remote -v

# Istruzioni push
echo ""
echo "⏭️  Prossimi step:"
echo ""
echo "Opzione 1: SSH (Consigliato)"
echo "  1. Genera SSH key: ssh-keygen -t ed25519 -C 'your_email@example.com'"
echo "  2. Aggiungi su GitHub: https://github.com/settings/keys"
echo "  3. Cambia remote: git remote set-url origin git@github.com:GAETAL2025/CDN-FRAMEWORK.git"
echo "  4. Push: git push -u origin master"
echo ""

echo "Opzione 2: HTTPS con Token"
echo "  1. Genera Personal Access Token: https://github.com/settings/tokens"
echo "  2. Esegui: git push -u origin master"
echo "  3. Username: GAETAL2025"
echo "  4. Password: <tuo-token>"
echo ""

echo "Opzione 3: Credenziali memorizzate"
echo "  1. Configura credential helper:"
echo "     git config --global credential.helper store"
echo "  2. First push chiederà credenziali (saranno salvate)"
echo "  3. Push: git push -u origin master"
echo ""

echo "✅ Repository locale pronto!"
echo "✅ Commit effettuato (master branch)"
echo ""
echo "Una volta autenticato, esegui: git push -u origin master"
