from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        if data is None or response is None or isinstance(data, bytes):
            return super().render(data, accepted_media_type, renderer_context)
        if isinstance(data, dict) and "success" in data:
            return super().render(data, accepted_media_type, renderer_context)

        if response.status_code >= 400:
            payload = {
                "success": False,
                "error": self._error_message(data),
                "code": self._error_code(response.status_code),
                "details": data,
            }
            return super().render(payload, accepted_media_type, renderer_context)

        payload = {
            "success": True,
            "data": data,
            "message": "",
        }
        return super().render(payload, accepted_media_type, renderer_context)

    def _error_message(self, data):
        if isinstance(data, dict):
            detail = data.get("detail") or data.get("error")
            if detail:
                return str(detail)
        return "Validation failed."

    def _error_code(self, status_code):
        if status_code == 400:
            return "VALIDATION_ERROR"
        if status_code == 401:
            return "AUTHENTICATION_REQUIRED"
        if status_code == 403:
            return "PERMISSION_DENIED"
        if status_code == 404:
            return "NOT_FOUND"
        if status_code == 409:
            return "CONFLICT"
        return "INTERNAL_ERROR" if status_code >= 500 else "VALIDATION_ERROR"
