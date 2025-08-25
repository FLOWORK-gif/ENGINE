#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\update_service\update_service.py
# JUMLAH BARIS : 105
#######################################################################

import requests
import json
import webbrowser
from tkinter import messagebox
from packaging.version import parse as parse_version
from ..base_service import BaseService
from flowork_kernel.exceptions import MandatoryUpdateRequiredError
import base64
from cryptography.hazmat.primitives import hashes as crypto_hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
class UpdateService(BaseService):
    """
    Handles checking for application updates from a remote source.
    [MODIFIED] Now includes digital signature verification for the update manifest.
    """
    REMOTE_CONFIG_PUBLIC_KEY_PEM_STRING = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAysqZG2+F82W0TgLHmF3Y
0GRPEZvXvmndTY84N/wA1ljt+JxMBVsmcVTkv8f1TrmFRD19IDzl2Yzb2lgqEbEy
GFxHhudC28leDsVEIp8B+oYWVm8Mh242YKYK8r5DAvr9CPQivnIjZ4BWgKKddMTd
harVxLF2CoSoTs00xWKd6VlXfoW9wdBvoDVifL+hCMepgLLdQQE4HbamPDJ3bpra
pCgcAD5urmVoJEUJdjd+Iic27RBK7jD1dWDO2MASMh/0IyXyM8i7RDymQ88gZier
U0OdWzeCWGyl4EquvR8lj5GNz4vg2f+oEY7h9AIC1f4ARtoihc+apSntqz7nAqa/
sQIDAQAB
-----END PUBLIC KEY-----"""
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.update_url = "https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/update.json"
        self.signature_url = "https://raw.githubusercontent.com/FLOWORK-gif/ASSET/refs/heads/main/update.sig"
        self.config_public_key = self._load_public_key()
    def _load_public_key(self):
        """Loads the public key for verifying the update manifest."""
        try:
            pem_data = self.REMOTE_CONFIG_PUBLIC_KEY_PEM_STRING.strip().encode('utf-8')
            public_key = serialization.load_pem_public_key(pem_data)
            self.logger("UpdateService: Public key for update verification loaded successfully.", "SUCCESS")
            return public_key
        except Exception as e:
            self.logger(f"UpdateService: CRITICAL: Failed to load public key: {e}. Update verification will fail.", "CRITICAL")
            return None
    def check_for_updates(self):
        self.logger("UpdateService: Checking for updates from remote URL...", "INFO")
        try:
            update_data, is_verified = self._fetch_and_verify_update_manifest()
            if not is_verified:
                self.logger("UpdateService: Update check aborted because the manifest signature is invalid or missing.", "CRITICAL")
                return
            latest_version_str = update_data.get("version")
            is_mandatory = update_data.get("is_mandatory", False)
            download_url = update_data.get("download_url")
            if not latest_version_str or not download_url:
                self.logger("UpdateService: Remote update.json is missing 'version' or 'download_url'.", "WARN")
                return
            current_version = parse_version(self.kernel.APP_VERSION)
            latest_version = parse_version(latest_version_str)
            if latest_version > current_version:
                self.logger(f"Update available: {latest_version_str}. Current version: {self.kernel.APP_VERSION}", "WARN")
                changelog = "\n".join([f"- {item}" for item in update_data.get("changelog", [])])
                message = f"A new version ({latest_version_str}) is available!\n\nChangelog:\n{changelog}\n\nDo you want to download it now?"
                if is_mandatory:
                    messagebox.showerror("Mandatory Update Required", f"A mandatory update to version {latest_version_str} is required to continue using the application.")
                    webbrowser.open(download_url)
                    raise MandatoryUpdateRequiredError(f"Mandatory update to {latest_version_str} required.")
                else:
                    if messagebox.askyesno("Update Available", message):
                        webbrowser.open(download_url)
            else:
                self.logger("Application is up to date.", "SUCCESS")
        except requests.exceptions.RequestException as e:
            self.logger(f"Could not connect to update server: {e}", "WARN")
        except MandatoryUpdateRequiredError:
            raise # Re-raise to be caught by the startup service
        except Exception as e:
            self.logger(f"An error occurred during update check: {e}", "ERROR")
    def _fetch_and_verify_update_manifest(self):
        """Fetches both update.json and its signature, then verifies them."""
        if not self.config_public_key:
            return None, False
        response = requests.get(self.update_url, timeout=10)
        response.raise_for_status()
        update_content_bytes = response.content
        update_data = json.loads(update_content_bytes)
        sig_response = requests.get(self.signature_url, timeout=10)
        sig_response.raise_for_status()
        signature_b64 = sig_response.text.strip()
        signature_bytes = base64.b64decode(signature_b64)
        try:
            self.config_public_key.verify(
                signature_bytes,
                update_content_bytes,
                padding.PKCS1v15(),
                crypto_hashes.SHA256()
            )
            self.logger("Update manifest signature VERIFIED successfully.", "SUCCESS")
            return update_data, True
        except InvalidSignature:
            self.logger("Update manifest signature VERIFICATION FAILED. The file may be tampered with.", "CRITICAL")
            return None, False
