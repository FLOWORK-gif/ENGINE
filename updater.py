#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\updater.py
# JUMLAH BARIS : 89
#######################################################################

import os
import json
import hashlib
import requests
REPO_OWNER = "FLOWORK-gif"
REPO_NAME = "ASSET"
BRANCH = "main" # atau 'master' tergantung repo-mu
FINGERPRINT_FILENAME = "file_fingerprints.json"
LOCAL_PROJECT_PATH = "C:\\FLOWORK" # Path absolut ke folder Flowork di komputer user
def calculate_sha256(file_path):
    """Menghitung hash SHA-256 dari sebuah file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except IOError:
        return None
def get_remote_fingerprints():
    """Mengunduh file sidik jari dari GitHub."""
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{FINGERPRINT_FILENAME}"
    print(f"  Downloading fingerprint from: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Could not connect to GitHub to check for updates: {e}")
        return None
    except json.JSONDecodeError:
        print("  [ERROR] Fingerprint file on GitHub is corrupted.")
        return None
def download_file(relative_path):
    """Mengunduh satu file dari repo GitHub dan menyimpannya secara lokal."""
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{relative_path}"
    local_path = os.path.join(LOCAL_PROJECT_PATH, relative_path.replace('/', os.sep))
    print(f"  Downloading '{relative_path}'...")
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"    [FAIL] Could not download '{relative_path}': {e}")
        return False
def main():
    """Fungsi utama untuk menjalankan proses update."""
    print("Starting update check...")
    if not os.path.isdir(LOCAL_PROJECT_PATH):
        print(f"\n[WARNING] Project directory '{LOCAL_PROJECT_PATH}' not found.")
        print("Updater will not run. Please run the downloader first.")
        return
    remote_prints = get_remote_fingerprints()
    if not remote_prints:
        print("\nCould not get remote version info. Skipping update.")
        return
    files_to_update = []
    for relative_path, remote_hash in remote_prints.items():
        local_path = os.path.join(LOCAL_PROJECT_PATH, relative_path.replace('/', os.sep))
        if not os.path.exists(local_path):
            files_to_update.append({'path': relative_path, 'reason': 'New file'})
        else:
            local_hash = calculate_sha256(local_path)
            if local_hash != remote_hash:
                files_to_update.append({'path': relative_path, 'reason': 'File changed'})
    if not files_to_update:
        print("\n[SUCCESS] Your application is up to date!")
        return
    print(f"\nFound {len(files_to_update)} file(s) to update/add:")
    for f in files_to_update:
        print(f"  - {f['path']} ({f['reason']})")
    print("\nStarting download process...")
    success_count = 0
    for file_info in files_to_update:
        if download_file(file_info['path']):
            success_count += 1
    print(f"\nUpdate process finished. {success_count}/{len(files_to_update)} files updated successfully.")
if __name__ == "__main__":
    main()
