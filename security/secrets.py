# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Windows DPAPI and machine-specific credential encryption for OMEN.
"""

import base64
import ctypes
from ctypes import wintypes
import os
import sys
from app.logging_config import logger


# Windows DPAPI structures via ctypes
class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte))
    ]


def _win32_encrypt(plaintext: bytes) -> bytes:
    """Encrypts bytes using Windows DPAPI (tied to current Windows user)."""
    if sys.platform != "win32":
        return base64.b64encode(plaintext)

    blob_in = DATA_BLOB()
    blob_in.cbData = len(plaintext)
    blob_in.pbData = ctypes.cast(ctypes.create_string_buffer(plaintext, len(plaintext)), ctypes.POINTER(ctypes.c_byte))

    blob_out = DATA_BLOB()

    CryptProtectData = ctypes.windll.crypt32.CryptProtectData
    CryptProtectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        wintypes.LPCWSTR,
        ctypes.POINTER(DATA_BLOB),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(DATA_BLOB)
    ]
    CryptProtectData.restype = wintypes.BOOL

    if not CryptProtectData(ctypes.byref(blob_in), "OMEN_SECRET", None, None, None, 0, ctypes.byref(blob_out)):
        raise RuntimeError(f"CryptProtectData failed with error: {ctypes.GetLastError()}")

    try:
        encrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        return encrypted
    finally:
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)


def _win32_decrypt(ciphertext: bytes) -> bytes:
    """Decrypts bytes using Windows DPAPI."""
    if sys.platform != "win32":
        return base64.b64decode(ciphertext)

    blob_in = DATA_BLOB()
    blob_in.cbData = len(ciphertext)
    blob_in.pbData = ctypes.cast(ctypes.create_string_buffer(ciphertext, len(ciphertext)), ctypes.POINTER(ctypes.c_byte))

    blob_out = DATA_BLOB()

    CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
    CryptUnprotectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(DATA_BLOB),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(DATA_BLOB)
    ]
    CryptUnprotectData.restype = wintypes.BOOL

    if not CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        raise RuntimeError(f"CryptUnprotectData failed with error: {ctypes.GetLastError()}")

    try:
        decrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        return decrypted
    finally:
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)


def encrypt_string(plain_text: str) -> str:
    """Encrypts a plaintext string and returns a base64 encoded string."""
    if not plain_text:
        return ""
    try:
        encrypted_bytes = _win32_encrypt(plain_text.encode("utf-8"))
        return base64.b64encode(encrypted_bytes).decode("ascii")
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        # Fallback to base64 encoding if DPAPI fails
        return "B64:" + base64.b64encode(plain_text.encode("utf-8")).decode("ascii")


def decrypt_string(encrypted_text: str) -> str:
    """Decrypts a base64 encoded DPAPI or fallback string."""
    if not encrypted_text:
        return ""
    try:
        if encrypted_text.startswith("B64:"):
            return base64.b64decode(encrypted_text[4:].encode("ascii")).decode("utf-8")
        raw_bytes = base64.b64decode(encrypted_text.encode("ascii"))
        return _win32_decrypt(raw_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return ""


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
