from django.urls import Resolver404, resolve
from rest_framework.test import APITestCase


UUID = "00000000-0000-0000-0000-000000000001"


class APIEndpointContractTests(APITestCase):
    """Chunk 12 endpoint map smoke tests.

    These tests intentionally assert URL resolution instead of response status so
    permissions, object existence, and request payload validation do not obscure
    whether the documented API surface is actually mounted.
    """

    endpoint_paths = [
        "/api/auth/register/",
        "/api/auth/login/",
        "/api/auth/logout/",
        "/api/auth/token/refresh/",
        "/api/auth/password-reset/",
        "/api/users/me/",
        "/api/users/",
        "/api/users/invite/",
        f"/api/users/{UUID}/status/",
        f"/api/users/{UUID}/unit/",
        "/api/states/",
        f"/api/states/{UUID}/lgas/",
        "/api/organizations/",
        f"/api/organizations/{UUID}/",
        f"/api/organizations/{UUID}/units/",
        f"/api/organizations/{UUID}/units/{UUID}/",
        f"/api/organizations/{UUID}/invites/",
        f"/api/organizations/{UUID}/invites/{UUID}/",
        "/api/food-handlers/",
        f"/api/food-handlers/{UUID}/",
        f"/api/food-handlers/{UUID}/business-branch/",
        f"/api/food-handlers/{UUID}/verify-nin/",
        f"/api/food-handlers/{UUID}/nin-verification/",
        "/api/employers/",
        f"/api/employers/{UUID}/",
        f"/api/employers/{UUID}/invite-food-handler/",
        "/api/medical-facilities/",
        f"/api/medical-facilities/{UUID}/",
        "/api/facility-accreditation/",
        f"/api/facility-accreditation/{UUID}/submit/",
        f"/api/facility-accreditation/{UUID}/approve/",
        f"/api/facility-accreditation/{UUID}/reject/",
        f"/api/facility-accreditation/{UUID}/suspend/",
        "/api/payments/assessment/initiate/",
        "/api/payments/subscription/initiate/",
        "/api/payments/verify/test-reference/",
        "/api/payments/webhook/",
        "/api/assessment-fees/",
        f"/api/assessment-fees/{UUID}/",
        "/api/subscription-plans/",
        f"/api/employers/{UUID}/subscribe/",
        f"/api/employers/{UUID}/subscription/",
        "/api/settlements/",
        f"/api/settlements/{UUID}/process/",
        f"/api/facilities/{UUID}/settlements/",
        "/api/appointments/",
        f"/api/appointments/{UUID}/",
        "/api/assessments/",
        f"/api/assessments/{UUID}/",
        f"/api/assessments/{UUID}/declaration/",
        f"/api/declarations/{UUID}/validate/",
        f"/api/assessments/{UUID}/physical-examination/",
        f"/api/assessments/{UUID}/lab-tests/",
        f"/api/lab-tests/{UUID}/result/",
        f"/api/lab-tests/{UUID}/review/",
        f"/api/assessments/{UUID}/vaccinations/",
        f"/api/food-handlers/{UUID}/vaccinations/",
        f"/api/assessments/{UUID}/fitness-decision/",
        "/api/certificate-requests/",
        f"/api/assessments/{UUID}/request-certificate/",
        f"/api/certificate-requests/{UUID}/approve/",
        f"/api/certificate-requests/{UUID}/reject/",
        "/api/certificates/generate/",
        "/api/certificates/",
        f"/api/certificates/{UUID}/",
        f"/api/certificates/{UUID}/download/",
        f"/api/certificates/{UUID}/revoke/",
        f"/api/certificates/{UUID}/suspend/",
        "/api/public/certificates/verify/FCN-LA-0001/",
        "/api/illness-reports/",
        f"/api/illness-reports/{UUID}/",
        f"/api/illness-reports/{UUID}/review/",
        f"/api/illness-reports/{UUID}/clearance/",
        "/api/inspections/",
        f"/api/inspections/{UUID}/",
        f"/api/inspections/{UUID}/submit/",
        f"/api/inspections/{UUID}/evidence/",
        "/api/dashboard/employer/",
        "/api/dashboard/facility/",
        "/api/dashboard/state/",
        "/api/dashboard/federal/",
        "/api/reports/employer-compliance/",
        "/api/reports/facility-performance/",
        "/api/reports/state-monthly/",
        "/api/reports/national/",
        "/api/reports/vaccination-coverage/",
        "/api/reports/illness-trends/",
        "/api/reports/inspection-outcomes/",
    ]

    def test_chunk_12_documented_api_paths_are_mounted(self):
        missing = []
        for path in self.endpoint_paths:
            try:
                resolve(path)
            except Resolver404:
                missing.append(path)
        self.assertEqual(missing, [])
