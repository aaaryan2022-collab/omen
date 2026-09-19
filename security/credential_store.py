# ============================================
"""
Secure Credential Store using SQLite and DPAPI encryption.
"""

from typing import Optional, Dict
from database.database import Database, get_db
from security.secrets import encrypt_string, decrypt_string
from app.logging_config import logger


class CredentialStore:
    """Manages securely encrypted API tokens and OAuth credentials."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()
        self._init_table()

    def _init_table(self):
        conn = self.db.get_connection()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    service TEXT PRIMARY KEY,
                    encrypted_data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def set_credential(self, service: str, secret_value: str):
        """Encrypts and stores a credential for a service."""
        encrypted = encrypt_string(secret_value)
        conn = self.db.get_connection()
        with conn:
            conn.execute("""
                INSERT INTO credentials (service, encrypted_data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(service) DO UPDATE SET
                    encrypted_data = excluded.encrypted_data,
                    updated_at = CURRENT_TIMESTAMP
            """, (service, encrypted))
        logger.debug(f"Credential updated for service '{service}'")

    def get_credential(self, service: str) -> Optional[str]:
        """Retrieves and decrypts a credential."""
        conn = self.db.get_connection()
        row = conn.execute("SELECT encrypted_data FROM credentials WHERE service = ?", (service,)).fetchone()
        if not row:
            return None
        return decrypt_string(row["encrypted_data"])

    def delete_credential(self, service: str) -> bool:
        """Deletes a stored credential."""
        conn = self.db.get_connection()
        with conn:
            cursor = conn.execute("DELETE FROM credentials WHERE service = ?", (service,))
            return cursor.rowcount > 0


_store_instance: Optional[CredentialStore] = None


def get_credential_store() -> CredentialStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = CredentialStore()
    return _store_instance


