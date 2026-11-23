"""
RFC 6238 Time-Based One-Time Password (TOTP) Implementation.
Provides zero-dependency, cryptographically secure 2FA authentication,
compatible with Google Authenticator, Microsoft Authenticator, and 1Password.
"""

import hmac
import hashlib
import struct
import time
import base64
import secrets
from typing import List, Tuple, Optional
import urllib.parse


class TOTPManager:
    @staticmethod
    def generate_secret(length: int = 32) -> str:
        """Generates a random base32 secret key."""
        random_bytes = secrets.token_bytes(length)
        # Base32 encode and remove padding
        return base64.b32encode(random_bytes).decode('utf-8').rstrip('=')

    @staticmethod
    def generate_recovery_codes(count: int = 8, length: int = 10) -> List[str]:
        """Generates secure alphanumeric backup recovery codes."""
        codes = []
        alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # remove confusing chars 0, 1, I, O
        for _ in range(count):
            raw = "".join(secrets.choice(alphabet) for _ in range(length))
            # Format as XXXXX-XXXXX
            formatted = f"{raw[:5]}-{raw[5:]}"
            codes.append(formatted)
        return codes

    @classmethod
    def generate_totp(cls, secret: str, time_step: int = 30, digits: int = 6, for_time: Optional[float] = None) -> str:
        """Computes current TOTP token for given secret using RFC 6238 / RFC 4226."""
        if for_time is None:
            for_time = time.time()
            
        counter = int(for_time // time_step)
        
        # Pad secret if needed for base32 decoding
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
            
        key = base64.b32decode(secret.upper(), casefold=True)
        # Pack counter into 8-byte big-endian binary
        msg = struct.pack(">Q", counter)
        
        # Calculate HMAC-SHA1
        h = hmac.new(key, msg, hashlib.sha1).digest()
        
        # Dynamic truncation (RFC 4226)
        offset = h[-1] & 0x0F
        truncated_hash = struct.unpack(">I", h[offset:offset + 4])[0] & 0x7FFFFFFF
        
        token = truncated_hash % (10 ** digits)
        return str(token).zfill(digits)

    @classmethod
    def verify_totp(cls, secret: str, token: str, time_step: int = 30, window: int = 1) -> bool:
        """
        Verifies TOTP token against secret allowing window time drift (-1, 0, +1 time steps).
        """
        current_time = time.time()
        # Clean token input
        clean_token = token.strip().replace(" ", "")
        
        for i in range(-window, window + 1):
            check_time = current_time + (i * time_step)
            expected = cls.generate_totp(secret, time_step=time_step, for_time=check_time)
            if hmac.compare_digest(expected, clean_token):
                return True
        return False

    @staticmethod
    def get_provisioning_uri(secret: str, account_name: str, issuer_name: str = "FinFlow AI") -> str:
        """Returns standard otpauth:// URL for QR code generation."""
        label = f"{issuer_name}:{account_name}"
        params = {
            "secret": secret,
            "issuer": issuer_name,
            "algorithm": "SHA1",
            "digits": "6",
            "period": "30"
        }
        return f"otpauth://totp/{urllib.parse.quote(label)}?{urllib.parse.urlencode(params)}"
