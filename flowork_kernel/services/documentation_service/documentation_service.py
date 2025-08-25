#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\documentation_service\documentation_service.py
# JUMLAH BARIS : 60
#######################################################################

import os
import subprocess
import threading
from ..base_service import BaseService
class DocumentationService(BaseService):
    """
    A service that automatically runs 'mkdocs serve' in the background
    during development to provide live documentation.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.process = None
        self.dev_mode = True # Asumsikan kita selalu dalam mode development saat ini
    def start(self):
        """Starts the mkdocs serve process in a background thread."""
        if not self.dev_mode:
            return
        project_root = self.kernel.project_root_path
        if not os.path.exists(os.path.join(project_root, 'mkdocs.yml')):
            self.logger("DocumentationService: mkdocs.yml not found. Skipping server start.", "WARN")
            return
        thread = threading.Thread(target=self._run_mkdocs_serve, daemon=True)
        thread.start()
    def _run_mkdocs_serve(self):
        """The actual worker that runs the subprocess."""
        self.logger("DocumentationService: Starting 'mkdocs serve' in the background...", "INFO")
        command = ['poetry', 'run', 'mkdocs', 'serve']
        try:
            self.process = subprocess.Popen(
                command,
                cwd=self.kernel.project_root_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0 # Sembunyikan window terminal di Windows
            )
            self.logger(f"DocumentationService: 'mkdocs serve' is running with PID: {self.process.pid}", "SUCCESS")
        except FileNotFoundError:
            self.logger("DocumentationService: 'poetry' command not found. Make sure you are in a Poetry environment.", "CRITICAL")
        except Exception as e:
            self.logger(f"DocumentationService: Failed to start 'mkdocs serve': {e}", "CRITICAL")
    def stop(self):
        """Stops the mkdocs serve process when the application exits."""
        if self.process and self.process.poll() is None:
            self.logger(f"DocumentationService: Stopping 'mkdocs serve' process (PID: {self.process.pid})...", "INFO")
            self.process.terminate() # Matikan proses mkdocs
            try:
                self.process.wait(timeout=5)
                self.logger("DocumentationService: Process terminated successfully.", "SUCCESS")
            except subprocess.TimeoutExpired:
                self.logger("DocumentationService: Process did not terminate in time, forcing kill.", "WARN")
                self.process.kill()
