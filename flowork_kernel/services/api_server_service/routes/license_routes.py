#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\license_routes.py
# JUMLAH BARIS : 45
#######################################################################

from .base_api_route import BaseApiRoute
class LicenseRoutes(BaseApiRoute):
    """
    Manages API routes for license-related actions like activation.
    """
    def register_routes(self):
        return {
            "POST /api/v1/license/activate": self.handle_activate_license,
            "POST /api/v1/license/deactivate": self.handle_deactivate_license, # <<< MODIFIKASI: Tambahkan rute baru
        }
    def handle_activate_license(self, handler):
        """
        Handles the license activation request from the UI via ApiClient.
        """
        license_manager = self.service_instance.kernel.get_service("license_manager_service")
        if not license_manager:
            return handler._send_response(503, {"error": "LicenseManager service is not available."})
        body = handler._get_json_body()
        if not body or 'license_content' not in body:
            return handler._send_response(400, {"error": "Request body must contain 'license_content'."})
        license_content = body['license_content']
        success, message = license_manager.activate_license_on_server(license_content)
        if success:
            handler._send_response(200, {"status": "success", "message": message})
        else:
            handler._send_response(400, {"error": message})
    def handle_deactivate_license(self, handler):
        """
        Handles the license deactivation request from the UI via ApiClient.
        """
        license_manager = self.service_instance.kernel.get_service("license_manager_service")
        if not license_manager:
            return handler._send_response(503, {"error": "LicenseManager service is not available."})
        success, message = license_manager.deactivate_license_on_server()
        if success:
            handler._send_response(200, {"status": "success", "message": message})
        else:
            handler._send_response(400, {"error": message})
