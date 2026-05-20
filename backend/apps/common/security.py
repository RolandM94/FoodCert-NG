import mimetypes

from django.conf import settings
from rest_framework.exceptions import ValidationError


DEFAULT_ALLOWED_UPLOAD_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "")


def scan_uploaded_file(uploaded_file):
    """Optional virus scanning hook.

    A deployment can wire a real scanner behind this function later. For MVP,
    setting FOODCERT_REJECT_EICAR_TEST_FILE=true rejects the EICAR signature so
    automated environments can verify the hook is active without external I/O.
    """
    if not getattr(settings, "FOODCERT_REJECT_EICAR_TEST_FILE", False):
        return
    current_position = uploaded_file.tell() if hasattr(uploaded_file, "tell") else None
    sample = uploaded_file.read(1024)
    if current_position is not None:
        uploaded_file.seek(current_position)
    if b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in sample:
        raise ValidationError("Uploaded file failed the security scan.")


def validate_uploaded_file_security(uploaded_file, *, allowed_types=None, max_size=None):
    if not uploaded_file:
        return uploaded_file

    max_size = max_size or getattr(settings, "MAX_UPLOAD_SIZE_BYTES", 5 * 1024 * 1024)
    if uploaded_file.size > max_size:
        raise ValidationError(f"Uploaded file cannot exceed {max_size} bytes.")

    allowed_types = allowed_types or DEFAULT_ALLOWED_UPLOAD_TYPES
    content_type = getattr(uploaded_file, "content_type", "") or mimetypes.guess_type(uploaded_file.name)[0] or ""
    if content_type not in allowed_types:
        raise ValidationError("Uploaded file type is not allowed.")

    scan_uploaded_file(uploaded_file)
    return uploaded_file
