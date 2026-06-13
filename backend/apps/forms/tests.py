from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.audit.models import AuditAction, AuditLog
from apps.employers.models import Employer, EstablishmentCategory
from apps.forms.exporting import flatten_response_for_export
from apps.forms.models import (
    AssignmentStatus,
    FormAssignment,
    FormPrimaryModule,
    FormRecipient,
    FormRecipientStatus,
    FormResponse,
    FormResponseActivityLog,
    FormResponseAttachment,
    FormSyncStatus,
    FormTemplate,
    FormTemplatePurpose,
    FormTemplateStatus,
    FormTemplateVersion,
    OfflineSyncQueue,
    ResponseStatus,
)
from apps.inspections.models import Inspection
from apps.locations.models import LGA, State
from apps.organizations.models import Organization, OrganizationType

User = get_user_model()


def payload(response):
    return response.data.get("data", response.data)


class FormsEngineFoundationTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY)
        self.admin = User.objects.create_user(
            username="state-form-admin",
            email="state-form-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            organization=self.org,
        )
        self.respondent = User.objects.create_user(
            username="inspector-form-user",
            email="inspector-form-user@example.com",
            password="StrongPass123!",
            role=UserRole.INSPECTOR,
            organization=self.org,
        )
        self.client.force_authenticate(self.admin)

    def create_template(self):
        return FormTemplate.objects.create(
            title="Food Business Inspection Checklist",
            description="Inspection field capture form.",
            purpose=FormTemplatePurpose.INSPECTION_CHECKLIST,
            owner_organization=self.org,
            target_respondent_type="inspector",
            primary_module=FormPrimaryModule.INSPECTIONS,
            default_context_type="inspection",
            created_by=self.admin,
        )

    def test_template_version_assignment_response_foundation_models(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={"sections": [{"key": "hygiene", "questions": [{"key": "has_water", "type": "yes_no"}]}]},
            logic_json={"rules": []},
            settings_json={"allow_offline": True},
            published_by=self.admin,
            published_at=timezone.now(),
            status=FormTemplateStatus.PUBLISHED,
        )
        assignment = FormAssignment.objects.create(
            title="Ikeja inspection",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
            recipient_role="inspector",
            context_type="inspection",
            context_id="inspection-001",
            allow_offline=True,
            status=AssignmentStatus.ACTIVE,
        )
        recipient = FormRecipient.objects.create(
            assignment=assignment,
            recipient_type="user",
            recipient_id=str(self.respondent.id),
            organization=self.org,
        )
        response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            recipient=recipient,
            respondent_user=self.respondent,
            respondent_organization=self.org,
            context_type="inspection",
            context_id="inspection-001",
            response_json={"has_water": True},
            status=ResponseStatus.DRAFT,
            sync_status=FormSyncStatus.SYNC_PENDING,
            device_id="field-tablet-1",
        )
        attachment = FormResponseAttachment.objects.create(
            response=response,
            question_key="evidence_photo",
            file_url="https://storage.example/evidence.jpg",
            file_name="evidence.jpg",
            mime_type="image/jpeg",
            uploaded_by=self.respondent,
            sync_status=FormSyncStatus.SYNCED,
        )
        activity = FormResponseActivityLog.objects.create(response=response, actor=self.respondent, action="draft_saved")
        sync_job = OfflineSyncQueue.objects.create(
            user=self.respondent,
            assignment=assignment,
            response=response,
            local_response_id="local-123",
            operation_type="submit_response",
            payload_json={"response_json": {"has_water": True}},
        )

        self.assertEqual(template.primary_module, FormPrimaryModule.INSPECTIONS)
        self.assertTrue(assignment.allow_offline)
        self.assertEqual(response.recipient, recipient)
        self.assertEqual(response.sync_status, FormSyncStatus.SYNC_PENDING)
        self.assertEqual(attachment.question_key, "evidence_photo")
        self.assertEqual(activity.action, "draft_saved")
        self.assertEqual(sync_job.status, FormSyncStatus.SYNC_PENDING)

    def test_recipient_is_unique_per_assignment_target(self):
        template = self.create_template()
        assignment = FormAssignment.objects.create(
            title="Monthly facility report",
            template=template,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="organization",
            assigned_to_id=str(self.org.id),
        )
        FormRecipient.objects.create(
            assignment=assignment,
            recipient_type="organization",
            recipient_id=str(self.org.id),
            organization=self.org,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                FormRecipient.objects.create(
                    assignment=assignment,
                    recipient_type="organization",
                    recipient_id=str(self.org.id),
                    organization=self.org,
                )

    def test_publish_endpoint_stores_schema_logic_and_settings_version(self):
        template = self.create_template()

        response = self.client.post(
            f"/api/forms/templates/{template.id}/publish/",
            {
                "schema_json": {"sections": [{"key": "overview", "title": "Overview"}]},
                "logic_json": {"rules": [{"when": "has_water", "equals": False}]},
                "settings_json": {"allow_offline": True},
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["status"], FormTemplateStatus.PUBLISHED)
        version = template.versions.get(version_number=1)
        self.assertEqual(version.schema_json["sections"][0]["key"], "overview")
        self.assertTrue(version.settings_json["allow_offline"])

    def test_response_actions_create_activity_logs_and_update_tracking_fields(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []})
        assignment = FormAssignment.objects.create(
            title="Branch inspection",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )

        draft = self.client.post(
            f"/api/forms/responses/{form_response.id}/save_draft/",
            {"response_json": {"has_water": True}, "device_id": "tablet-1"},
            format="json",
        )
        submit = self.client.post(f"/api/forms/responses/{form_response.id}/submit/", format="json")
        review = self.client.post(
            f"/api/forms/responses/{form_response.id}/review/",
            {"review_notes": "Looks complete."},
            format="json",
        )

        self.assertEqual(draft.status_code, 200)
        self.assertEqual(submit.status_code, 200)
        self.assertEqual(review.status_code, 200)
        form_response.refresh_from_db()
        self.assertEqual(form_response.status, ResponseStatus.REVIEWED)
        self.assertIsNotNone(form_response.submitted_at)
        self.assertIsNotNone(form_response.reviewed_at)
        self.assertEqual(
            list(form_response.activity_logs.order_by("created_at").values_list("action", flat=True)),
            ["draft_saved", "submitted", "reviewed"],
        )

    def test_submit_blocks_invalid_required_and_format_fields(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "contact",
                        "title": "Contact",
                        "questions": [
                            {"key": "manager_name", "label": "Manager name", "type": "short_text", "required": True},
                            {"key": "manager_email", "label": "Manager email", "type": "email", "required": True},
                            {"key": "score", "label": "Compliance score", "type": "number", "required": True, "validation": {"min_value": 1, "max_value": 100}},
                        ],
                    }
                ]
            },
        )
        assignment = FormAssignment.objects.create(
            title="Branch inspection validation",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )

        invalid = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {"response_json": {"manager_email": "not-an-email", "score": 150}},
            format="json",
        )
        self.assertEqual(invalid.status_code, 400)
        invalid_payload = payload(invalid)
        self.assertEqual(invalid_payload["error"], "Validation failed.")
        self.assertEqual({item["key"] for item in invalid_payload["errors"]}, {"manager_name", "manager_email", "score"})

        valid = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {"response_json": {"manager_name": "Amina Bello", "manager_email": "amina@example.com", "score": 95}},
            format="json",
        )
        self.assertEqual(valid.status_code, 200)
        form_response.refresh_from_db()
        self.assertEqual(form_response.status, ResponseStatus.SUBMITTED)

    def test_submit_respects_skip_logic_for_hidden_and_conditionally_required_fields(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "certification",
                        "title": "Certification",
                        "questions": [
                            {"key": "has_certificate", "label": "Has certificate?", "type": "yes_no", "required": True},
                            {"key": "certificate_number", "label": "Certificate number", "type": "short_text", "required": True},
                            {"key": "explanation", "label": "Explanation", "type": "long_text", "required": False},
                        ],
                    }
                ]
            },
            logic_json={
                "rules": [
                    {
                        "target_type": "question",
                        "target_key": "certificate_number",
                        "action": "hide",
                        "conditions": [{"question_key": "has_certificate", "operator": "equals", "value": False}],
                    },
                    {
                        "target_type": "question",
                        "target_key": "explanation",
                        "action": "require",
                        "conditions": [{"question_key": "has_certificate", "operator": "equals", "value": False}],
                    },
                ]
            },
        )
        assignment = FormAssignment.objects.create(
            title="Logic validation",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )

        missing_conditional = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {"response_json": {"has_certificate": False}},
            format="json",
        )
        self.assertEqual(missing_conditional.status_code, 400)
        self.assertEqual({item["key"] for item in payload(missing_conditional)["errors"]}, {"explanation"})

        valid = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {"response_json": {"has_certificate": False, "explanation": "Handler is awaiting renewal."}},
            format="json",
        )
        self.assertEqual(valid.status_code, 200)

    def test_repeat_group_validation_enforces_repeats_and_nested_required_fields(self):
        template = self.create_template()
        schema = {
            "sections": [
                {
                    "key": "handlers",
                    "title": "Observed Handlers",
                    "questions": [
                        {
                            "key": "observed_handlers",
                            "label": "Observed food handlers",
                            "type": "repeat_group",
                            "required": True,
                            "validation": {"min_repeats": 1, "max_repeats": 2},
                            "questions": [
                                {"key": "handler_name", "label": "Handler name", "type": "short_text", "required": True},
                                {"key": "certificate_qr", "label": "Certificate QR", "type": "certificate_qr_scan", "required": True},
                                {"key": "temperature", "label": "Temperature", "type": "decimal", "required": False, "validation": {"min_value": 35, "max_value": 39}},
                            ],
                        }
                    ],
                }
            ]
        }
        version = FormTemplateVersion.objects.create(template=template, version_number=1, schema_json=schema)
        assignment = FormAssignment.objects.create(
            title="Repeat validation",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )

        empty = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {"response_json": {"observed_handlers": []}},
            format="json",
        )
        self.assertEqual(empty.status_code, 400)
        self.assertEqual({item["key"] for item in payload(empty)["errors"]}, {"observed_handlers"})

        missing_nested = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {"response_json": {"observed_handlers": [{"certificate_qr": "FCNG-LA-001"}]}},
            format="json",
        )
        self.assertEqual(missing_nested.status_code, 400)
        self.assertIn("observed_handlers.0.handler_name", {item["key"] for item in payload(missing_nested)["errors"]})

        too_many = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {
                "response_json": {
                    "observed_handlers": [
                        {"handler_name": "Amina", "certificate_qr": "FCNG-LA-001"},
                        {"handler_name": "Bola", "certificate_qr": "FCNG-LA-002"},
                        {"handler_name": "Chidi", "certificate_qr": "FCNG-LA-003"},
                    ]
                }
            },
            format="json",
        )
        self.assertEqual(too_many.status_code, 400)
        self.assertIn("observed_handlers", {item["key"] for item in payload(too_many)["errors"]})

        valid = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {
                "response_json": {
                    "observed_handlers": [
                        {"handler_name": "Amina", "certificate_qr": "FCNG-LA-001", "temperature": 36.7},
                        {"handler_name": "Bola", "certificate_qr": "FCNG-LA-002", "temperature": 37.1},
                    ]
                }
            },
            format="json",
        )
        self.assertEqual(valid.status_code, 200)

    def test_repeat_group_export_flattening_uses_stable_item_columns(self):
        schema = {
            "sections": [
                {
                    "key": "handlers",
                    "questions": [
                        {
                            "key": "observed_handlers",
                            "type": "repeat_group",
                            "questions": [
                                {"key": "handler_name", "type": "short_text"},
                                {"key": "certificate_qr", "type": "certificate_qr_scan"},
                            ],
                        }
                    ],
                }
            ]
        }
        flattened = flatten_response_for_export(
            schema,
            {
                "observed_handlers": [
                    {"handler_name": "Amina", "certificate_qr": "FCNG-LA-001"},
                    {"handler_name": "Bola", "certificate_qr": "FCNG-LA-002"},
                ]
            },
        )

        self.assertEqual(flattened["observed_handlers.__count"], 2)
        self.assertEqual(flattened["observed_handlers[1].handler_name"], "Amina")
        self.assertEqual(flattened["observed_handlers[2].certificate_qr"], "FCNG-LA-002")

    def test_media_attachment_upload_captures_secure_metadata(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []})
        assignment = FormAssignment.objects.create(
            title="Media upload",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )
        upload = SimpleUploadedFile("kitchen.jpg", b"fake image data", content_type="image/jpeg")

        result = self.client.post(
            f"/api/forms/responses/{form_response.id}/attachments/",
            {"question_key": "kitchen_photo", "file": upload, "gps_latitude": "6.524400", "gps_longitude": "3.379200"},
            format="multipart",
        )

        self.assertEqual(result.status_code, 201, result.data)
        attachment = form_response.attachments.get(question_key="kitchen_photo")
        self.assertEqual(attachment.file_name, "kitchen.jpg")
        self.assertEqual(attachment.mime_type, "image/jpeg")
        self.assertEqual(attachment.file_type, "image")
        self.assertEqual(attachment.file_size, len(b"fake image data"))
        self.assertEqual(str(attachment.gps_latitude), "6.524400")
        self.assertEqual(form_response.activity_logs.filter(action="attachment_uploaded").count(), 1)

    def test_media_validation_enforces_required_type_and_size_rules(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "evidence",
                        "title": "Evidence",
                        "questions": [
                            {
                                "key": "inspection_photos",
                                "label": "Inspection photos",
                                "type": "image_upload",
                                "required": True,
                                "validation": {
                                    "min_files": 1,
                                    "max_files": 2,
                                    "allowed_file_types": "jpg,png",
                                    "max_file_size": 10,
                                },
                            }
                        ],
                    }
                ]
            },
        )
        assignment = FormAssignment.objects.create(
            title="Media validation",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )

        missing = self.client.post(f"/api/forms/responses/{form_response.id}/submit/", {"response_json": {}}, format="json")
        self.assertEqual(missing.status_code, 400)
        self.assertEqual({item["key"] for item in payload(missing)["errors"]}, {"inspection_photos"})

        invalid = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {
                "response_json": {
                    "inspection_photos": [
                        {"file_name": "evidence.pdf", "mime_type": "application/pdf", "file_size": 12}
                    ]
                }
            },
            format="json",
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual({item["key"] for item in payload(invalid)["errors"]}, {"inspection_photos"})

        valid = self.client.post(
            f"/api/forms/responses/{form_response.id}/submit/",
            {
                "response_json": {
                    "inspection_photos": [
                        {"file_name": "evidence.jpg", "mime_type": "image/jpeg", "file_size": 9}
                    ]
                }
            },
            format="json",
        )
        self.assertEqual(valid.status_code, 200)

    def test_offline_package_and_sync_submit_response(self):
        template = self.create_template()
        schema = {
            "sections": [
                {
                    "key": "inspection",
                    "questions": [
                        {"key": "manager_name", "label": "Manager name", "type": "short_text", "required": True}
                    ],
                }
            ]
        }
        version = FormTemplateVersion.objects.create(template=template, version_number=1, schema_json=schema, settings_json={"allow_offline": True})
        assignment = FormAssignment.objects.create(
            title="Offline inspection",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
            allow_offline=True,
            status=AssignmentStatus.ACTIVE,
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )
        self.client.force_authenticate(self.respondent)

        package = self.client.get(f"/api/forms/offline/assignments/{assignment.id}/package/")
        self.assertEqual(package.status_code, 200)
        self.assertEqual(package.data["assignment"]["id"], str(assignment.id))
        self.assertEqual(package.data["response"]["id"], str(form_response.id))

        synced = self.client.post(
            "/api/forms/offline/sync/",
            {
                "local_response_id": "local-offline-1",
                "operation_type": "submit_response",
                "payload_json": {
                    "assignment_id": str(assignment.id),
                    "response_id": str(form_response.id),
                    "response_json": {"manager_name": "Amina Bello"},
                    "device_id": "field-tablet-2",
                    "offline_created_at": timezone.now().isoformat(),
                },
            },
            format="json",
        )

        self.assertEqual(synced.status_code, 200)
        self.assertEqual(synced.data["status"], FormSyncStatus.SYNCED)
        form_response.refresh_from_db()
        self.assertEqual(form_response.status, ResponseStatus.SUBMITTED)
        self.assertEqual(form_response.sync_status, FormSyncStatus.SYNCED)
        self.assertEqual(form_response.response_json["manager_name"], "Amina Bello")

    def test_offline_sync_returns_validation_failure_without_losing_payload(self):
        template = self.create_template()
        schema = {
            "sections": [
                {
                    "key": "inspection",
                    "questions": [
                        {"key": "manager_name", "label": "Manager name", "type": "short_text", "required": True}
                    ],
                }
            ]
        }
        version = FormTemplateVersion.objects.create(template=template, version_number=1, schema_json=schema, settings_json={"allow_offline": True})
        assignment = FormAssignment.objects.create(
            title="Offline inspection validation",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
            allow_offline=True,
            status=AssignmentStatus.ACTIVE,
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )
        self.client.force_authenticate(self.respondent)

        failed = self.client.post(
            "/api/forms/offline/sync/",
            {
                "local_response_id": "local-offline-invalid",
                "operation_type": "submit_response",
                "payload_json": {
                    "assignment_id": str(assignment.id),
                    "response_id": str(form_response.id),
                    "response_json": {},
                },
            },
            format="json",
        )

        self.assertEqual(failed.status_code, 409)
        self.assertEqual(failed.data["status"], FormSyncStatus.SYNC_FAILED)
        self.assertEqual(failed.data["errors"][0]["key"], "manager_name")
        sync_job = OfflineSyncQueue.objects.get(local_response_id="local-offline-invalid")
        self.assertEqual(sync_job.status, FormSyncStatus.SYNC_FAILED)
        self.assertEqual(sync_job.payload_json["response_json"], {})

    def test_submission_tracking_updates_recipient_progress_and_summary(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []})
        assignment = FormAssignment.objects.create(
            title="Tracking assignment",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
            status=AssignmentStatus.ACTIVE,
        )
        recipient = FormRecipient.objects.create(
            assignment=assignment,
            recipient_type="user",
            recipient_id=str(self.respondent.id),
            organization=self.org,
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            recipient=recipient,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )

        draft = self.client.post(
            f"/api/forms/responses/{form_response.id}/save_draft/",
            {"response_json": {"field": "value"}},
            format="json",
        )
        self.assertEqual(draft.status_code, 200)
        recipient.refresh_from_db()
        self.assertEqual(recipient.status, FormRecipientStatus.IN_PROGRESS)
        self.assertIsNotNone(recipient.started_at)

        summary = self.client.get(f"/api/forms/assignments/{assignment.id}/summary/")
        self.assertEqual(summary.status_code, 200)
        self.assertEqual(summary.data["status_summary"]["total_recipients"], 1)
        self.assertEqual(summary.data["status_summary"]["in_progress"], 1)
        self.assertEqual(summary.data["response_rate"], 100.0)
        self.assertEqual(summary.data["completion_rate"], 0.0)

    def test_submission_tracking_marks_overdue_and_sends_reminders(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []})
        assignment = FormAssignment.objects.create(
            title="Overdue assignment",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
            due_date=timezone.now() - timezone.timedelta(days=1),
            status=AssignmentStatus.ACTIVE,
        )
        recipient = FormRecipient.objects.create(
            assignment=assignment,
            recipient_type="user",
            recipient_id=str(self.respondent.id),
            organization=self.org,
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            recipient=recipient,
            respondent_user=self.respondent,
            respondent_organization=self.org,
        )

        assignments = self.client.get("/api/forms/assignments/")
        self.assertEqual(assignments.status_code, 200)
        assignment.refresh_from_db()
        recipient.refresh_from_db()
        form_response.refresh_from_db()
        self.assertEqual(assignment.status, AssignmentStatus.OVERDUE)
        self.assertEqual(recipient.status, FormRecipientStatus.OVERDUE)
        self.assertEqual(form_response.status, ResponseStatus.OVERDUE)

        reminder = self.client.post(f"/api/forms/assignments/{assignment.id}/send-reminder/")
        self.assertEqual(reminder.status_code, 200)
        self.assertEqual(reminder.data["reminded_count"], 1)
        recipient.refresh_from_db()
        self.assertIsNotNone(recipient.notified_at)

    def test_response_exports_flatten_repeat_groups_and_log_activity(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "handlers",
                        "questions": [
                            {
                                "key": "observed_handlers",
                                "label": "Observed handlers",
                                "type": "repeat_group",
                                "questions": [
                                    {"key": "handler_name", "label": "Handler name", "type": "short_text"},
                                ],
                            }
                        ],
                    }
                ]
            },
        )
        assignment = FormAssignment.objects.create(
            title="Export assignment",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
            status=AssignmentStatus.ACTIVE,
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
            response_json={"observed_handlers": [{"handler_name": "Amina"}]},
            status=ResponseStatus.SUBMITTED,
        )

        csv_result = self.client.get(f"/api/forms/exports/responses/?assignment={assignment.id}&format=csv")
        self.assertEqual(csv_result.status_code, 200)
        self.assertIn("text/csv", csv_result["Content-Type"])
        self.assertIn("observed_handlers[1].handler_name", csv_result.content.decode())
        self.assertIn("Amina", csv_result.content.decode())

        json_result = self.client.get(f"/api/forms/exports/responses/?assignment={assignment.id}&format=json")
        self.assertEqual(json_result.status_code, 200)
        self.assertEqual(json_result.json()[0]["observed_handlers[1].handler_name"], "Amina")
        self.assertGreaterEqual(form_response.activity_logs.filter(action="exported").count(), 2)

    def test_attachment_zip_export_includes_index_and_uploaded_files(self):
        template = self.create_template()
        version = FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []})
        assignment = FormAssignment.objects.create(
            title="Attachment export",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="user",
            assigned_to_id=str(self.respondent.id),
            status=AssignmentStatus.ACTIVE,
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=self.org,
            status=ResponseStatus.SUBMITTED,
        )
        FormResponseAttachment.objects.create(
            response=form_response,
            question_key="evidence_photo",
            file=SimpleUploadedFile("evidence.txt", b"evidence data", content_type="text/plain"),
            file_name="evidence.txt",
            mime_type="text/plain",
            uploaded_by=self.respondent,
        )

        result = self.client.get(f"/api/forms/exports/attachments/?assignment={assignment.id}")

        self.assertEqual(result.status_code, 200)
        self.assertIn("application/zip", result["Content-Type"])
        import zipfile
        from io import BytesIO

        with zipfile.ZipFile(BytesIO(result.content)) as archive:
            names = archive.namelist()
            self.assertIn("attachments-index.csv", names)
            self.assertTrue(any(name.endswith("evidence.txt") for name in names))
            self.assertIn("evidence_photo", archive.read("attachments-index.csv").decode())
        self.assertEqual(form_response.activity_logs.filter(action="exported").count(), 1)

    def test_analytics_support_filters_structured_fields_and_inspection_scores(self):
        state = State.objects.create(name="Lagos", code="LA")
        lga = LGA.objects.create(name="Ikeja", state=state)
        employer_org = Organization.objects.create(
            name="Analytics Foods",
            organization_type=OrganizationType.EMPLOYER,
            state=state,
            lga=lga,
        )
        employer = Employer.objects.create(
            business_name="Analytics Foods",
            establishment_category=EstablishmentCategory.RESTAURANT_CAFE,
            contact_person_name="Ada",
            contact_person_phone="08030000000",
            contact_person_email="analytics@example.com",
            address="1 Food Road",
            state=state,
            lga=lga,
            organization=employer_org,
        )
        template = self.create_template()
        template.status = FormTemplateStatus.PUBLISHED
        template.primary_module = FormPrimaryModule.INSPECTIONS
        template.save(update_fields=["status", "primary_module", "updated_at"])
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "hygiene",
                        "title": "Hygiene",
                        "questions": [
                            {"key": "has_water", "label": "Has water", "type": "yes_no"},
                            {"key": "risk", "label": "Risk", "type": "risk_rating"},
                            {"key": "private_note", "label": "Private note", "type": "single_choice", "sensitivity": "medical", "options": ["A", "B"]},
                        ],
                    }
                ]
            },
            status=FormTemplateStatus.PUBLISHED,
            published_by=self.admin,
            published_at=timezone.now(),
        )
        inspection = Inspection.objects.create(
            inspector=self.respondent,
            employer=employer,
            compliance_score=75,
        )
        assignment = FormAssignment.objects.create(
            title="Analytics inspection",
            template=template,
            template_version=version,
            purpose=FormTemplatePurpose.INSPECTION_CHECKLIST,
            assigned_by=self.admin,
            assigned_to_type="organization",
            assigned_to_id=str(employer_org.id),
            context_type="inspection",
            context_id=str(inspection.id),
            status=AssignmentStatus.ACTIVE,
        )
        FormRecipient.objects.create(
            assignment=assignment,
            recipient_type="organization",
            recipient_id=str(employer_org.id),
            organization=employer_org,
        )
        FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.respondent,
            respondent_organization=employer_org,
            context_type="inspection",
            context_id=str(inspection.id),
            response_json={"has_water": True, "risk": "high", "private_note": "A"},
            status=ResponseStatus.SUBMITTED,
            risk_rating="high",
            submitted_at=timezone.now(),
        )

        response = self.client.get(
            f"/api/forms/reports/analytics/?assignment={assignment.id}&organization={employer_org.id}&state={state.id}&lga={lga.id}&primary_module=inspections&context_type=inspection"
        )

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["summary"]["total_responses"], 1)
        self.assertEqual(data["assignment_stats"][0]["assignment_id"], str(assignment.id))
        self.assertEqual(data["organization_breakdown"][0]["organization_name"], "Analytics Foods")
        self.assertEqual(data["location_breakdown"][0]["state_name"], "Lagos")
        self.assertEqual(data["inspection_analytics"]["inspection_count"], 1)
        self.assertEqual(data["inspection_analytics"]["average_score"], 75.0)
        question_keys = {row["question_key"] for row in data["structured_response_analytics"]}
        self.assertIn("has_water", question_keys)
        self.assertIn("risk", question_keys)
        self.assertNotIn("private_note", question_keys)


class PortalAssignedFormsTests(APITestCase):
    def setUp(self):
        self.state_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY)
        self.employer_org = Organization.objects.create(name="Tasty Foods", organization_type=OrganizationType.EMPLOYER)
        self.other_employer_org = Organization.objects.create(name="Other Foods", organization_type=OrganizationType.EMPLOYER)
        self.facility_org = Organization.objects.create(name="Mainland Clinic", organization_type=OrganizationType.MEDICAL_FACILITY)
        self.admin = User.objects.create_user(
            username="portal-form-admin",
            email="portal-form-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            organization=self.state_org,
        )
        self.employer_user = User.objects.create_user(
            username="employer-forms-user",
            email="employer-forms@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
        )
        self.facility_user = User.objects.create_user(
            username="facility-forms-user",
            email="facility-forms@example.com",
            password="StrongPass123!",
            role=UserRole.FACILITY_ADMIN,
            organization=self.facility_org,
        )

    def _template(self, *, title, purpose, primary_module, context_type):
        template = FormTemplate.objects.create(
            title=title,
            purpose=purpose,
            owner_organization=self.state_org,
            target_respondent_type="organization",
            primary_module=primary_module,
            default_context_type=context_type,
            status=FormTemplateStatus.PUBLISHED,
            created_by=self.admin,
        )
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={"sections": [{"key": "main", "title": "Main", "questions": [{"key": "notes", "label": "Notes", "type": "long_text"}]}]},
            status=FormTemplateStatus.PUBLISHED,
            published_by=self.admin,
            published_at=timezone.now(),
        )
        return template, version

    def _assignment(self, *, template, version, org, purpose, context_type):
        assignment = FormAssignment.objects.create(
            title=template.title,
            template=template,
            template_version=version,
            purpose=purpose,
            assigned_by=self.admin,
            assigned_to_type="organization",
            assigned_to_id=str(org.id),
            context_type=context_type,
            context_id=str(org.id),
            status=AssignmentStatus.ACTIVE,
            allow_offline=True,
        )
        FormRecipient.objects.create(
            assignment=assignment,
            recipient_type="organization",
            recipient_id=str(org.id),
            organization=org,
        )
        return assignment

    def test_employer_portal_lists_scoped_assignments_and_response_history(self):
        template, version = self._template(
            title="Employer compliance return",
            purpose=FormTemplatePurpose.EMPLOYER_COMPLIANCE,
            primary_module=FormPrimaryModule.EMPLOYERS,
            context_type="employer",
        )
        assignment = self._assignment(
            template=template,
            version=version,
            org=self.employer_org,
            purpose=FormTemplatePurpose.EMPLOYER_COMPLIANCE,
            context_type="employer",
        )
        other_assignment = self._assignment(
            template=template,
            version=version,
            org=self.other_employer_org,
            purpose=FormTemplatePurpose.EMPLOYER_COMPLIANCE,
            context_type="employer",
        )
        FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            respondent_user=self.employer_user,
            respondent_organization=self.employer_org,
            context_type="employer",
            context_id=str(self.employer_org.id),
            response_json={"notes": "Submitted return"},
            status=ResponseStatus.SUBMITTED,
            submitted_at=timezone.now(),
        )

        self.client.force_authenticate(self.employer_user)
        response = self.client.get("/api/employer/assigned-forms/")
        self.assertEqual(response.status_code, 200)
        rows = response.data
        self.assertEqual([row["id"] for row in rows], [str(assignment.id)])
        self.assertNotIn(str(other_assignment.id), [row["id"] for row in rows])
        self.assertEqual(rows[0]["response_status"], ResponseStatus.SUBMITTED)
        self.assertEqual(len(rows[0]["response_history"]), 1)

        submitted = self.client.get("/api/employer/assigned-forms/?status=submitted")
        returned = self.client.get("/api/employer/assigned-forms/?status=returned")
        self.assertEqual(len(submitted.data), 1)
        self.assertEqual(len(returned.data), 0)
        self.assertEqual(self.client.get("/api/facility/assigned-forms/").status_code, 403)

    def test_facility_portal_can_start_assigned_facility_form(self):
        template, version = self._template(
            title="Facility monthly report",
            purpose=FormTemplatePurpose.FACILITY_MONTHLY_REPORT,
            primary_module=FormPrimaryModule.FACILITIES,
            context_type="facility",
        )
        assignment = self._assignment(
            template=template,
            version=version,
            org=self.facility_org,
            purpose=FormTemplatePurpose.FACILITY_MONTHLY_REPORT,
            context_type="facility",
        )

        self.client.force_authenticate(self.facility_user)
        response = self.client.get("/api/facility/assigned-forms/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.data], [str(assignment.id)])

        start = self.client.post(
            f"/api/facility/assigned-forms/{assignment.id}/response/",
            {"response_json": {"notes": "Facility data"}},
            format="json",
        )
        self.assertEqual(start.status_code, 201)
        self.assertEqual(payload(start)["context_id"], str(self.facility_org.id))
        self.assertEqual(str(payload(start)["respondent_organization"]), str(self.facility_org.id))


class FormsPermissionsPrivacyAuditTests(APITestCase):
    def setUp(self):
        self.state_org = Organization.objects.create(name="State MOH Forms", organization_type=OrganizationType.STATE_MINISTRY)
        self.employer_org = Organization.objects.create(name="Privacy Foods", organization_type=OrganizationType.EMPLOYER)
        self.other_org = Organization.objects.create(name="Other Privacy Foods", organization_type=OrganizationType.EMPLOYER)
        self.admin = User.objects.create_user(
            username="privacy-admin",
            email="privacy-admin@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            organization=self.state_org,
        )
        self.employer_user = User.objects.create_user(
            username="privacy-employer",
            email="privacy-employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.employer_org,
        )
        self.other_user = User.objects.create_user(
            username="other-privacy-employer",
            email="other-privacy-employer@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=self.other_org,
        )
        self.template = FormTemplate.objects.create(
            title="Privacy Form",
            purpose=FormTemplatePurpose.EMPLOYER_COMPLIANCE,
            owner_organization=self.state_org,
            target_respondent_type="organization",
            primary_module=FormPrimaryModule.EMPLOYERS,
            default_context_type="employer",
            status=FormTemplateStatus.PUBLISHED,
            created_by=self.admin,
        )
        self.version = FormTemplateVersion.objects.create(
            template=self.template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "main",
                        "title": "Main",
                        "questions": [
                            {"key": "public_answer", "label": "Public answer", "type": "short_text"},
                            {"key": "medical_answer", "label": "Medical answer", "type": "short_text", "sensitivity": "medical"},
                            {
                                "key": "handlers",
                                "label": "Handlers",
                                "type": "repeat_group",
                                "questions": [
                                    {"key": "name", "label": "Name", "type": "short_text"},
                                    {"key": "diagnosis", "label": "Diagnosis", "type": "short_text", "sensitivity": "medical"},
                                ],
                            },
                        ],
                    }
                ]
            },
            status=FormTemplateStatus.PUBLISHED,
            published_by=self.admin,
            published_at=timezone.now(),
        )
        self.assignment = FormAssignment.objects.create(
            title="Privacy assignment",
            template=self.template,
            template_version=self.version,
            purpose=FormTemplatePurpose.EMPLOYER_COMPLIANCE,
            assigned_by=self.admin,
            assigned_to_type="organization",
            assigned_to_id=str(self.employer_org.id),
            context_type="employer",
            context_id=str(self.employer_org.id),
            status=AssignmentStatus.ACTIVE,
            allow_offline=True,
        )
        FormRecipient.objects.create(
            assignment=self.assignment,
            recipient_type="organization",
            recipient_id=str(self.employer_org.id),
            organization=self.employer_org,
        )
        self.form_response = FormResponse.objects.create(
            assignment=self.assignment,
            template=self.template,
            template_version=self.version,
            respondent_user=self.employer_user,
            respondent_organization=self.employer_org,
            context_type="employer",
            context_id=str(self.employer_org.id),
            response_json={
                "public_answer": "Visible",
                "medical_answer": "Hidden",
                "handlers": [{"name": "Ada", "diagnosis": "Private"}],
            },
            status=ResponseStatus.SUBMITTED,
        )

    def test_portal_and_generic_response_payloads_mask_sensitive_fields(self):
        self.client.force_authenticate(self.employer_user)

        detail = self.client.get(f"/api/employer/assigned-forms/{self.assignment.id}/")
        self.assertEqual(detail.status_code, 200)
        response_data = detail.data["response"]["response_json"]
        self.assertEqual(response_data["public_answer"], "Visible")
        self.assertNotIn("medical_answer", response_data)
        self.assertEqual(response_data["handlers"], [{"name": "Ada"}])
        medical_question = detail.data["template_schema"]["sections"][0]["questions"][1]
        self.assertEqual(medical_question["type"], "hidden")
        nested_questions = detail.data["template_schema"]["sections"][0]["questions"][2]["questions"]
        self.assertEqual(nested_questions[1]["type"], "hidden")

        generic = self.client.get(f"/api/forms/responses/{self.form_response.id}/")
        self.assertEqual(generic.status_code, 200)
        self.assertNotIn("medical_answer", generic.data["response_json"])

    def test_scope_prevents_cross_organization_form_access(self):
        self.client.force_authenticate(self.other_user)

        self.assertEqual(self.client.get("/api/employer/assigned-forms/").data, [])
        self.assertEqual(self.client.get(f"/api/forms/responses/{self.form_response.id}/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/forms/offline/assignments/{self.assignment.id}/package/").status_code, 404)

    def test_exports_are_controlled_masked_and_audited(self):
        self.client.force_authenticate(self.employer_user)
        denied = self.client.get(f"/api/forms/exports/responses/?assignment={self.assignment.id}&format=json")
        self.assertEqual(denied.status_code, 403)

        self.client.force_authenticate(self.admin)
        exported = self.client.get(f"/api/forms/exports/responses/?assignment={self.assignment.id}&format=json")
        self.assertEqual(exported.status_code, 200)
        body = exported.json()[0]
        self.assertEqual(body["public_answer"], "Visible")
        self.assertNotIn("medical_answer", body)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.admin,
                action=AuditAction.SECURITY_EVENT,
                metadata__event="form_export_created",
            ).exists()
        )

    def test_response_actions_write_platform_audit_logs(self):
        self.client.force_authenticate(self.employer_user)
        draft = self.client.post(
            f"/api/forms/responses/{self.form_response.id}/save_draft/",
            {"response_json": {"public_answer": "Updated"}},
            format="json",
        )
        self.assertEqual(draft.status_code, 200)
        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.employer_user,
                target_type="FormResponse",
                target_id=str(self.form_response.id),
                metadata__event="form_response_draft_saved",
            ).exists()
        )
