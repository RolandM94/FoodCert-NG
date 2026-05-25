from rest_framework.throttling import ScopedRateThrottle


class LoginRateThrottle(ScopedRateThrottle):
    scope = "login"


class PublicVerificationRateThrottle(ScopedRateThrottle):
    scope = "public_verification"


class SuspiciousReportRateThrottle(ScopedRateThrottle):
    scope = "suspicious_report"
