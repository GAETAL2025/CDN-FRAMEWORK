"""
Update Module: verifica aggiornamenti dal repository Git e applica l'aggiornamento automatico.
"""

import logging
import os
from typing import Tuple
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class UpdateModule:
    """Modulo di aggiornamento automatico."""

    def __init__(self, executor):
        self.executor = executor
        self.remote_branch = "origin/main"
        self.git_cmd = "git"

    def is_git_repo(self) -> bool:
        """Verifica se la cartella corrente è un repository Git."""
        stdout, stderr, return_code = self.executor.execute("git rev-parse --is-inside-work-tree", shell=True)
        return return_code == 0 and stdout.strip() == "true"

    def has_git_available(self) -> bool:
        return self.executor.check_command_exists(self.git_cmd)

    def get_current_commit(self) -> str:
        stdout, stderr, return_code = self.executor.execute("git rev-parse HEAD", shell=True)
        return stdout.strip() if return_code == 0 else ""

    def get_remote_commit(self) -> str:
        stdout, stderr, return_code = self.executor.execute(f"git rev-parse {self.remote_branch}", shell=True)
        return stdout.strip() if return_code == 0 else ""

    def fetch_remote(self) -> bool:
        stdout, stderr, return_code = self.executor.execute(f"git fetch origin main --quiet", shell=True, timeout=30)
        if return_code != 0:
            logger.warning(f"Fetch remote fallito: {stderr}")
            return False
        return True

    def is_update_available(self) -> bool:
        if not self.has_git_available():
            logger.debug("Git non disponibile, salto aggiornamento automatico")
            return False
        if not self.is_git_repo():
            logger.debug("Non è un repository Git, salto aggiornamento automatico")
            return False
        if not self.fetch_remote():
            return False

        local_commit = self.get_current_commit()
        remote_commit = self.get_remote_commit()

        logger.debug(f"Local commit: {local_commit}")
        logger.debug(f"Remote commit: {remote_commit}")

        return local_commit and remote_commit and local_commit != remote_commit

    def perform_update(self) -> Tuple[bool, str, str]:
        stdout, stderr, return_code = self.executor.execute("git pull --ff-only origin main", shell=True, timeout=60)
        success = return_code == 0
        if not success:
            logger.error(f"Aggiornamento automatico fallito: {stderr}")
        return success, stdout, stderr
