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
    FormTemplateVisibility,
    FormTemplateVersion,
    OfflineSyncQueue,
    ResponseStatus,
)
from apps.inspections.models import Inspection
from apps.locations.models import LGA, State
from apps.organizations.models import Organization, OrganizationType

User = get_user_model()


def payload(response):
    if isinstance(response.data, dict):
        return response.data.get("data", response.data)
    return response.data


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

    def test_draft_template_can_be_deleted(self):
        template = self.create_template()
        FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={"sections": []},
            status=FormTemplateStatus.DRAFT,
        )

        response = self.client.delete(f"/api/forms/templates/{template.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(FormTemplate.objects.filter(id=template.id).exists())
        self.assertTrue(AuditLog.objects.filter(action=AuditAction.DELETE, target_id=str(template.id)).exists())

    def test_published_template_must_be_archived_instead_of_deleted(self):
        template = self.create_template()
        template.status = FormTemplateStatus.PUBLISHED
        template.save(update_fields=["status", "updated_at"])

        response = self.client.delete(f"/api/forms/templates/{template.id}/")

        self.assertEqual(response.status_code, 400)
        self.assertTrue(FormTemplate.objects.filter(id=template.id).exists())

    def test_assigned_template_cannot_be_deleted(self):
        template = self.create_template()
        FormAssignment.objects.create(
            title="Monthly facility report",
            template=template,
            purpose=template.purpose,
            assigned_by=self.admin,
            assigned_to_type="organization",
            assigned_to_id=str(self.org.id),
        )

        response = self.client.delete(f"/api/forms/templates/{template.id}/")

        self.assertEqual(response.status_code, 400)
        self.assertTrue(FormTemplate.objects.filter(id=template.id).exists())

    def test_templates_are_organization_native_unless_explicitly_shared(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-forms-admin",
            email="federal-forms-admin@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        state_template = self.create_template()
        federal_template = FormTemplate.objects.create(
            title="Federal M&E Reporting",
            description="Federal owned reporting form.",
            purpose=FormTemplatePurpose.GENERAL_DATA_COLLECTION,
            owner_organization=federal_org,
            target_respondent_type="state_ministry",
            primary_module=FormPrimaryModule.REPORTS,
            created_by=federal_admin,
        )

        self.client.force_authenticate(federal_admin)
        response = self.client.get("/api/forms/templates/")

        self.assertEqual(response.status_code, 200)
        template_ids = {item["id"] for item in payload(response)}
        self.assertIn(str(federal_template.id), template_ids)
        self.assertNotIn(str(state_template.id), template_ids)

        state_template.settings_json = {"shared_with_organizations": [str(federal_org.id)]}
        state_template.save(update_fields=["settings_json", "updated_at"])
        shared_response = self.client.get("/api/forms/templates/")

        shared_ids = {item["id"] for item in payload(shared_response)}
        self.assertIn(str(state_template.id), shared_ids)

    def test_shared_template_is_visible_but_not_mutable_by_non_owner(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-forms-editor",
            email="federal-forms-editor@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        state_template = self.create_template()
        state_template.settings_json = {"shared_with_organizations": [str(federal_org.id)]}
        state_template.save(update_fields=["settings_json", "updated_at"])
        self.client.force_authenticate(federal_admin)

        update_response = self.client.patch(
            f"/api/forms/templates/{state_template.id}/",
            {"title": "Changed by Federal"},
            format="json",
        )
        draft_response = self.client.post(
            f"/api/forms/templates/{state_template.id}/save-draft/",
            {"schema_json": {"sections": []}},
            format="json",
        )

        self.assertEqual(update_response.status_code, 403)
        self.assertEqual(draft_response.status_code, 403)

    def test_federal_cannot_assign_unshared_state_template_by_id(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-forms-assigner",
            email="federal-forms-assigner@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        state_template = self.create_template()
        state_template.status = FormTemplateStatus.PUBLISHED
        state_template.save(update_fields=["status", "updated_at"])
        state_version = FormTemplateVersion.objects.create(
            template=state_template,
            version_number=1,
            schema_json={"sections": []},
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(federal_admin)

        response = self.client.post(
            "/api/forms/assignments/",
            {
                "title": "Improper Federal Assignment",
                "template": str(state_template.id),
                "template_version": str(state_version.id),
                "purpose": state_template.purpose,
                "assigned_to_type": "organization",
                "assigned_to_id": str(federal_org.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_federal_template_defaults_private_and_can_be_marked_standard(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-template-standard",
            email="federal-template-standard@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        self.client.force_authenticate(federal_admin)

        created = self.client.post(
            "/api/forms/templates/",
            {
                "title": "Federal M&E Data Collection",
                "purpose": FormTemplatePurpose.FEDERAL_ME_DATA_COLLECTION,
                "primary_module": FormPrimaryModule.REPORTS,
            },
            format="json",
        )

        self.assertEqual(created.status_code, 201)
        self.assertEqual(payload(created)["visibility"], FormTemplateVisibility.FEDERAL_PRIVATE)
        marked = self.client.post(f"/api/forms/templates/{payload(created)['id']}/mark-standard/", format="json")
        self.assertEqual(marked.status_code, 200)
        self.assertEqual(payload(marked)["visibility"], FormTemplateVisibility.FEDERAL_STANDARD)
        self.assertTrue(AuditLog.objects.filter(metadata__event="form_template_marked_standard").exists())

    def test_federal_can_share_template_with_selected_state(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-template-share",
            email="federal-template-share@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        state = State.objects.create(name="Oyo", code="OY")
        template = FormTemplate.objects.create(
            title="Guideline Survey",
            purpose=FormTemplatePurpose.GUIDELINE_IMPLEMENTATION_SURVEY,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_PRIVATE,
            created_by=federal_admin,
        )
        self.client.force_authenticate(federal_admin)

        response = self.client.post(
            f"/api/forms/templates/{template.id}/share-to-states/",
            {"state_ids": [str(state.id)]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        data = payload(response)
        self.assertEqual(data["visibility"], FormTemplateVisibility.FEDERAL_SHARED)
        self.assertEqual(data["shared_state_names"], ["Oyo"])
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_template_shared_with_states").exists())

    def test_state_can_list_standard_and_shared_federal_templates_only(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        oyo = State.objects.create(name="Oyo", code="OY")
        state_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        state_admin = User.objects.create_user(
            username="lagos-federal-template-viewer",
            email="lagos-federal-template-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=state_org,
        )
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        standard = FormTemplate.objects.create(
            title="National Standard Template",
            purpose=FormTemplatePurpose.STATE_REPORTING_FORM,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
        )
        shared = FormTemplate.objects.create(
            title="Lagos Shared Template",
            purpose=FormTemplatePurpose.CROSS_STATE_SURVEY,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_SHARED,
            status=FormTemplateStatus.PUBLISHED,
        )
        shared.shared_with_states.add(lagos)
        other_shared = FormTemplate.objects.create(
            title="Oyo Shared Template",
            purpose=FormTemplatePurpose.CROSS_STATE_SURVEY,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_SHARED,
            status=FormTemplateStatus.PUBLISHED,
        )
        other_shared.shared_with_states.add(oyo)
        private = FormTemplate.objects.create(
            title="Federal Private Template",
            purpose=FormTemplatePurpose.FEDERAL_ME_DATA_COLLECTION,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_PRIVATE,
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(state_admin)

        response = self.client.get("/api/state/forms/federal-templates/")

        self.assertEqual(response.status_code, 200)
        template_ids = {item["id"] for item in payload(response)}
        self.assertIn(str(standard.id), template_ids)
        self.assertIn(str(shared.id), template_ids)
        self.assertNotIn(str(other_shared.id), template_ids)
        self.assertNotIn(str(private.id), template_ids)

    def test_state_can_adopt_federal_template_as_read_only(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        state_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        state_admin = User.objects.create_user(
            username="lagos-template-adopter",
            email="lagos-template-adopter@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=state_org,
        )
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_template = FormTemplate.objects.create(
            title="Federal Standard Inspection Performance",
            purpose=FormTemplatePurpose.INSPECTION_PERFORMANCE_REPORTING_TEMPLATE,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
        )
        federal_version = FormTemplateVersion.objects.create(
            template=federal_template,
            version_number=1,
            schema_json={"sections": [{"key": "summary", "questions": [{"key": "count", "type": "number"}]}]},
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(state_admin)

        adopted_response = self.client.post(f"/api/state/forms/federal-templates/{federal_template.id}/adopt/", format="json")

        self.assertEqual(adopted_response.status_code, 201)
        adopted = FormTemplate.objects.get(id=payload(adopted_response)["id"])
        self.assertEqual(adopted.owner_organization, state_org)
        self.assertEqual(adopted.source_template, federal_template)
        self.assertEqual(adopted.source_version, federal_version)
        self.assertEqual(adopted.settings_json["federal_source"]["adoption_type"], "adopted")
        self.assertEqual(adopted.status, FormTemplateStatus.PUBLISHED)
        self.assertTrue(adopted.versions.filter(version_number=1).exists())
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_template_adopted").exists())

        update_response = self.client.patch(
            f"/api/forms/templates/{adopted.id}/",
            {"title": "Should not edit adopted template"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 403)

    def test_state_can_clone_federal_template_into_editable_draft(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        state_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        state_admin = User.objects.create_user(
            username="lagos-template-cloner",
            email="lagos-template-cloner@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=state_org,
        )
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_template = FormTemplate.objects.create(
            title="Federal Guideline Survey",
            purpose=FormTemplatePurpose.GUIDELINE_IMPLEMENTATION_SURVEY,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
        )
        FormTemplateVersion.objects.create(
            template=federal_template,
            version_number=1,
            schema_json={"sections": [{"key": "guidelines", "questions": [{"key": "implemented", "type": "yes_no"}]}]},
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(state_admin)

        clone_response = self.client.post(
            f"/api/state/forms/federal-templates/{federal_template.id}/clone/",
            {"title": "Lagos Guideline Survey"},
            format="json",
        )

        self.assertEqual(clone_response.status_code, 201)
        cloned = FormTemplate.objects.get(id=payload(clone_response)["id"])
        self.assertEqual(cloned.title, "Lagos Guideline Survey")
        self.assertEqual(cloned.owner_organization, state_org)
        self.assertEqual(cloned.source_template, federal_template)
        self.assertEqual(cloned.settings_json["federal_source"]["adoption_type"], "cloned")
        self.assertEqual(cloned.status, FormTemplateStatus.DRAFT)
        self.assertTrue(cloned.versions.filter(version_number=1, status=FormTemplateStatus.DRAFT).exists())
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_template_cloned").exists())

        update_response = self.client.patch(
            f"/api/forms/templates/{cloned.id}/",
            {"title": "Edited Lagos Guideline Survey"},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        cloned.refresh_from_db()
        self.assertEqual(cloned.title, "Edited Lagos Guideline Survey")

    def test_federal_assignment_to_all_states_creates_state_recipients(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        oyo = State.objects.create(name="Oyo", code="OY")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        oyo_org = Organization.objects.create(name="Oyo State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=oyo)
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-assignment-all",
            email="federal-assignment-all@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        template = FormTemplate.objects.create(
            title="Monthly State Reporting",
            purpose=FormTemplatePurpose.STATE_REPORTING_FORM,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []}, status=FormTemplateStatus.PUBLISHED)
        self.client.force_authenticate(federal_admin)

        response = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "June State Reporting", "template": str(template.id), "recipient_scope": "all_states"},
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        assignment = FormAssignment.objects.get(id=payload(response)["id"])
        self.assertEqual(assignment.assigned_to_type, "all_states")
        self.assertEqual(set(assignment.recipients.values_list("organization_id", flat=True)), {lagos_org.id, oyo_org.id})
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_form_assignment_created").exists())

    def test_federal_assignment_to_selected_states_only_targets_selected_state_orgs(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        oyo = State.objects.create(name="Oyo", code="OY")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        Organization.objects.create(name="Oyo State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=oyo)
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-assignment-selected",
            email="federal-assignment-selected@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        state_admin = User.objects.create_user(
            username="lagos-assignment-viewer",
            email="lagos-assignment-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=lagos_org,
        )
        template = FormTemplate.objects.create(
            title="Guideline Implementation",
            purpose=FormTemplatePurpose.GUIDELINE_IMPLEMENTATION_SURVEY,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []}, status=FormTemplateStatus.PUBLISHED)
        self.client.force_authenticate(federal_admin)

        created = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "Guideline Survey", "template": str(template.id), "recipient_scope": "selected_states", "state_ids": [str(lagos.id)]},
            format="json",
        )

        self.assertEqual(created.status_code, 201, created.data)
        assignment = FormAssignment.objects.get(id=payload(created)["id"])
        self.assertEqual(list(assignment.recipients.values_list("organization_id", flat=True)), [lagos_org.id])

        self.client.force_authenticate(state_admin)
        state_list = self.client.get("/api/state/forms/federal-assignments/")
        self.assertEqual(state_list.status_code, 200)
        self.assertEqual([item["id"] for item in payload(state_list)], [str(assignment.id)])

    def test_federal_operational_assignment_is_blocked_without_special_permission(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-assignment-blocked",
            email="federal-assignment-blocked@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        template = FormTemplate.objects.create(
            title="Operational Template",
            purpose=FormTemplatePurpose.FEDERAL_ME_DATA_COLLECTION,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_PRIVATE,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []}, status=FormTemplateStatus.PUBLISHED)
        self.client.force_authenticate(federal_admin)

        response = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "Blocked Operational Assignment", "template": str(template.id), "recipient_scope": "employer"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_state_can_submit_federal_assignment_and_federal_can_monitor_response(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-response-monitor",
            email="federal-response-monitor@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        state_admin = User.objects.create_user(
            username="lagos-federal-response-submitter",
            email="lagos-federal-response-submitter@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=lagos_org,
        )
        template = FormTemplate.objects.create(
            title="Monthly State Compliance Return",
            purpose=FormTemplatePurpose.STATE_REPORTING_FORM,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "summary",
                        "questions": [
                            {"key": "inspections_completed", "label": "Inspections completed", "type": "number", "required": True}
                        ],
                    }
                ]
            },
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(federal_admin)
        created = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "June Compliance Return", "template": str(template.id), "recipient_scope": "selected_states", "state_ids": [str(lagos.id)]},
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        assignment = FormAssignment.objects.get(id=payload(created)["id"])

        self.client.force_authenticate(state_admin)
        submitted = self.client.post(
            f"/api/state/forms/federal-assignments/{assignment.id}/response/",
            {"response_json": {"inspections_completed": 24}},
            format="json",
        )
        self.assertEqual(submitted.status_code, 200, submitted.data)
        form_response = FormResponse.objects.get(id=payload(submitted)["id"])
        self.assertEqual(form_response.status, ResponseStatus.SUBMITTED)
        self.assertEqual(form_response.recipient.status, FormRecipientStatus.SUBMITTED)

        self.client.force_authenticate(federal_admin)
        summary = self.client.get(f"/api/federal/forms/assignments/{assignment.id}/response-summary/")
        responses = self.client.get("/api/federal/forms/responses/", {"assignment": str(assignment.id)})

        self.assertEqual(summary.status_code, 200, summary.data)
        self.assertEqual(summary.data["total_assigned_states"], 1)
        self.assertEqual(summary.data["submitted_states"], 1)
        self.assertEqual(summary.data["pending_states"], 0)
        self.assertEqual(summary.data["response_rate"], 100)
        self.assertEqual(responses.status_code, 200, responses.data)
        self.assertEqual([item["id"] for item in payload(responses)], [str(form_response.id)])

    def test_federal_state_response_matrix_tracks_pending_and_submitted_states(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        oyo = State.objects.create(name="Oyo", code="OY")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        oyo_org = Organization.objects.create(name="Oyo State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=oyo)
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-matrix-monitor",
            email="federal-matrix-monitor@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        lagos_admin = User.objects.create_user(
            username="lagos-matrix-submitter",
            email="lagos-matrix-submitter@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=lagos_org,
        )
        template = FormTemplate.objects.create(
            title="Guideline Implementation Return",
            purpose=FormTemplatePurpose.GUIDELINE_IMPLEMENTATION_SURVEY,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={"sections": [{"key": "summary", "questions": [{"key": "implemented", "type": "yes_no", "required": True}]}]},
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(federal_admin)
        created = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "Guideline Return", "template": str(template.id), "recipient_scope": "all_states"},
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        assignment = FormAssignment.objects.get(id=payload(created)["id"])
        self.assertEqual(set(assignment.recipients.values_list("organization_id", flat=True)), {lagos_org.id, oyo_org.id})

        self.client.force_authenticate(lagos_admin)
        submitted = self.client.post(
            f"/api/state/forms/federal-assignments/{assignment.id}/response/",
            {"response_json": {"implemented": True}},
            format="json",
        )
        self.assertEqual(submitted.status_code, 200, submitted.data)

        self.client.force_authenticate(federal_admin)
        matrix = self.client.get(f"/api/federal/forms/assignments/{assignment.id}/state-response-matrix/")
        self.assertEqual(matrix.status_code, 200, matrix.data)
        rows_by_state = {row["state_name"]: row for row in payload(matrix)}
        self.assertEqual(rows_by_state["Lagos"]["submitted"], 1)
        self.assertEqual(rows_by_state["Lagos"]["pending"], 0)
        self.assertEqual(rows_by_state["Oyo"]["submitted"], 0)
        self.assertEqual(rows_by_state["Oyo"]["pending"], 1)

    def test_federal_response_detail_masks_sensitive_answers_without_permission(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-sensitive-viewer",
            email="federal-sensitive-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        state_admin = User.objects.create_user(
            username="lagos-sensitive-submitter",
            email="lagos-sensitive-submitter@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=lagos_org,
        )
        template = FormTemplate.objects.create(
            title="National Incident Return",
            purpose=FormTemplatePurpose.NATIONAL_INCIDENT_REPORTING,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "incident",
                        "questions": [
                            {"key": "incident_count", "label": "Incident count", "type": "number", "required": True, "sensitivity": "public"},
                            {"key": "patient_symptoms", "label": "Patient symptoms", "type": "long_text", "required": False, "sensitivity": "medical"},
                        ],
                    }
                ]
            },
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(federal_admin)
        created = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "Incident Return", "template": str(template.id), "recipient_scope": "selected_states", "state_ids": [str(lagos.id)]},
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        assignment = FormAssignment.objects.get(id=payload(created)["id"])

        self.client.force_authenticate(state_admin)
        submitted = self.client.post(
            f"/api/state/forms/federal-assignments/{assignment.id}/response/",
            {"response_json": {"incident_count": 2, "patient_symptoms": "Private medical detail"}},
            format="json",
        )
        self.assertEqual(submitted.status_code, 200, submitted.data)

        self.client.force_authenticate(federal_admin)
        detail = self.client.get(f"/api/federal/forms/responses/{payload(submitted)['id']}/")
        self.assertEqual(detail.status_code, 200, detail.data)
        self.assertEqual(payload(detail)["response_json"], {"incident_count": 2})
        masked_question = payload(detail)["template_schema"]["sections"][0]["questions"][1]
        self.assertTrue(masked_question["masked"])
        self.assertEqual(masked_question["key"], "patient_symptoms")

    def test_federal_reports_compare_states_and_overdue_submissions(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        oyo = State.objects.create(name="Oyo", code="OY")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        oyo_org = Organization.objects.create(name="Oyo State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=oyo)
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-report-viewer",
            email="federal-report-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        lagos_admin = User.objects.create_user(
            username="lagos-report-submitter",
            email="lagos-report-submitter@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=lagos_org,
        )
        template = FormTemplate.objects.create(
            title="State Reporting Template",
            purpose=FormTemplatePurpose.STATE_REPORTING_FORM,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={"sections": [{"key": "summary", "questions": [{"key": "completed", "type": "number", "required": True}]}]},
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(federal_admin)
        created = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "Monthly State Reporting", "template": str(template.id), "recipient_scope": "all_states"},
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        assignment = FormAssignment.objects.get(id=payload(created)["id"])

        self.client.force_authenticate(lagos_admin)
        submitted = self.client.post(
            f"/api/state/forms/federal-assignments/{assignment.id}/response/",
            {"response_json": {"completed": 12}},
            format="json",
        )
        self.assertEqual(submitted.status_code, 200, submitted.data)
        oyo_recipient = assignment.recipients.get(organization=oyo_org)
        oyo_recipient.status = FormRecipientStatus.OVERDUE
        oyo_recipient.save(update_fields=["status", "updated_at"])

        self.client.force_authenticate(federal_admin)
        report = self.client.get(f"/api/federal/forms/reports/state_by_state_response_comparison/?assignment={assignment.id}")
        self.assertEqual(report.status_code, 200, report.data)
        data = payload(report)
        self.assertEqual(data["summary"]["total_assigned_states"], 2)
        self.assertEqual(data["summary"]["submitted_states"], 1)
        self.assertEqual(data["summary"]["overdue_states"], 1)
        rows_by_state = {row["state_name"]: row for row in data["state_response_comparison"]}
        self.assertEqual(rows_by_state["Lagos"]["submitted"], 1)
        self.assertEqual(rows_by_state["Oyo"]["overdue"], 1)
        self.assertEqual(data["overdue_submissions"][0]["state_name"], "Oyo")

    def test_federal_template_adoption_report_lists_state_derivatives(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        state_admin = User.objects.create_user(
            username="lagos-adoption-report-user",
            email="lagos-adoption-report-user@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=lagos_org,
        )
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-adoption-report-viewer",
            email="federal-adoption-report-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        federal_template = FormTemplate.objects.create(
            title="Federal Standard Template Usage",
            purpose=FormTemplatePurpose.GUIDELINE_IMPLEMENTATION_SURVEY,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(
            template=federal_template,
            version_number=1,
            schema_json={"sections": []},
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(state_admin)
        adopted = self.client.post(f"/api/state/forms/federal-templates/{federal_template.id}/adopt/", format="json")
        self.assertEqual(adopted.status_code, 201, adopted.data)

        self.client.force_authenticate(federal_admin)
        report = self.client.get("/api/federal/forms/reports/template_adoption_by_state/")
        self.assertEqual(report.status_code, 200, report.data)
        adoption_rows = payload(report)["template_adoption_by_state"]
        self.assertEqual(adoption_rows[0]["state_name"], "Lagos")
        self.assertEqual(adoption_rows[0]["source_template_title"], "Federal Standard Template Usage")
        self.assertEqual(adoption_rows[0]["adoption_type"], "adopted")

    def test_federal_export_omits_sensitive_fields_and_logs_action(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-export-user",
            email="federal-export-user@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        state_admin = User.objects.create_user(
            username="lagos-export-submitter",
            email="lagos-export-submitter@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=lagos_org,
        )
        template = FormTemplate.objects.create(
            title="Federal Export Template",
            purpose=FormTemplatePurpose.NATIONAL_INCIDENT_REPORTING,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=federal_admin,
        )
        FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "incident",
                        "questions": [
                            {"key": "incident_count", "label": "Incident count", "type": "number", "required": True, "sensitivity": "public"},
                            {"key": "patient_detail", "label": "Patient detail", "type": "long_text", "sensitivity": "medical"},
                        ],
                    }
                ]
            },
            status=FormTemplateStatus.PUBLISHED,
        )
        self.client.force_authenticate(federal_admin)
        created = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "Incident Export Assignment", "template": str(template.id), "recipient_scope": "selected_states", "state_ids": [str(lagos.id)]},
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        assignment = FormAssignment.objects.get(id=payload(created)["id"])

        self.client.force_authenticate(state_admin)
        submitted = self.client.post(
            f"/api/state/forms/federal-assignments/{assignment.id}/response/",
            {"response_json": {"incident_count": 4, "patient_detail": "Private medical content"}},
            format="json",
        )
        self.assertEqual(submitted.status_code, 200, submitted.data)

        self.client.force_authenticate(federal_admin)
        export_created = self.client.post(
            "/api/federal/forms/exports/",
            {"format": "csv", "filters": {"assignment": str(assignment.id)}},
            format="json",
        )
        self.assertEqual(export_created.status_code, 201, export_created.data)
        export_id = payload(export_created)["id"]
        downloaded = self.client.get(f"/api/federal/forms/exports/{export_id}/download/")
        self.assertEqual(downloaded.status_code, 200)
        content = downloaded.content.decode()
        self.assertIn("incident_count", content)
        self.assertIn("4", content)
        self.assertNotIn("patient_detail", content)
        self.assertNotIn("Private medical content", content)
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_form_report_export_created").exists())
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_form_report_export_downloaded").exists())

    def test_federal_template_lifecycle_uses_federal_audit_events_and_unshare(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-template-audit-user",
            email="federal-template-audit-user@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        lagos = State.objects.create(name="Lagos", code="LA")
        self.client.force_authenticate(federal_admin)

        created = self.client.post(
            "/api/forms/templates/",
            {
                "title": "Federal Audit Template",
                "purpose": FormTemplatePurpose.STATE_REPORTING_FORM,
                "primary_module": FormPrimaryModule.REPORTS,
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        template_id = payload(created)["id"]
        published = self.client.post(
            f"/api/forms/templates/{template_id}/publish/",
            {"schema_json": {"sections": [{"key": "summary", "questions": []}]}},
            format="json",
        )
        shared = self.client.post(
            f"/api/forms/templates/{template_id}/share-to-states/",
            {"state_ids": [str(lagos.id)]},
            format="json",
        )
        unshared = self.client.post(f"/api/forms/templates/{template_id}/unshare-states/", format="json")

        self.assertEqual(published.status_code, 200, published.data)
        self.assertEqual(shared.status_code, 200, shared.data)
        self.assertEqual(unshared.status_code, 200, unshared.data)
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_template_created").exists())
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_template_published").exists())
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_template_shared_with_states").exists())
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_template_unshared").exists())

    def test_federal_template_alias_endpoints_reuse_form_template_engine(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        federal_admin = User.objects.create_user(
            username="federal-template-alias-user",
            email="federal-template-alias-user@example.com",
            password="StrongPass123!",
            role=UserRole.FEDERAL_ADMIN,
            organization=federal_org,
        )
        lagos = State.objects.create(name="Lagos", code="LA")
        self.client.force_authenticate(federal_admin)

        created = self.client.post(
            "/api/federal/forms/templates/",
            {
                "title": "Federal Alias Template",
                "purpose": FormTemplatePurpose.FEDERAL_ME_DATA_COLLECTION,
                "primary_module": FormPrimaryModule.REPORTS,
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.data)
        template_id = payload(created)["id"]
        self.assertEqual(payload(created)["visibility"], FormTemplateVisibility.FEDERAL_PRIVATE)

        published = self.client.post(
            f"/api/federal/forms/templates/{template_id}/publish/",
            {"schema_json": {"sections": [{"key": "summary", "questions": []}]}},
            format="json",
        )
        shared = self.client.post(
            f"/api/federal/forms/templates/{template_id}/share-to-states/",
            {"state_ids": [str(lagos.id)]},
            format="json",
        )
        marked = self.client.post(f"/api/federal/forms/templates/{template_id}/mark-standard/", format="json")
        listed = self.client.get("/api/federal/forms/templates/")

        self.assertEqual(published.status_code, 200, published.data)
        self.assertEqual(shared.status_code, 200, shared.data)
        self.assertEqual(marked.status_code, 200, marked.data)
        self.assertEqual(payload(marked)["visibility"], FormTemplateVisibility.FEDERAL_STANDARD)
        self.assertEqual(listed.status_code, 200, listed.data)
        self.assertIn(template_id, {item["id"] for item in payload(listed)})

    def test_federal_forms_permissions_block_wrong_account_types(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        state_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        employer_org = Organization.objects.create(name="No Access Foods", organization_type=OrganizationType.EMPLOYER, state=lagos)
        state_admin = User.objects.create_user(
            username="state-federal-permission-denied",
            email="state-federal-permission-denied@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=state_org,
        )
        employer_user = User.objects.create_user(
            username="employer-template-denied",
            email="employer-template-denied@example.com",
            password="StrongPass123!",
            role=UserRole.EMPLOYER,
            organization=employer_org,
        )

        self.client.force_authenticate(state_admin)
        federal_assignments = self.client.get("/api/federal/forms/assignments/")
        create_federal_assignment = self.client.post("/api/federal/forms/assignments/", {"template": "not-a-template"}, format="json")
        self.assertEqual(federal_assignments.status_code, 403)
        self.assertEqual(create_federal_assignment.status_code, 403)

        self.client.force_authenticate(employer_user)
        create_template = self.client.post(
            "/api/forms/templates/",
            {"title": "Employer Cannot Create Platform Template", "purpose": FormTemplatePurpose.GENERAL_DATA_COLLECTION},
            format="json",
        )
        self.assertEqual(create_template.status_code, 403)

    def test_sensitive_federal_response_view_is_audited_for_sensitive_detail_permission(self):
        lagos = State.objects.create(name="Lagos", code="LA")
        lagos_org = Organization.objects.create(name="Lagos State MOH", organization_type=OrganizationType.STATE_MINISTRY, state=lagos)
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        super_admin = User.objects.create_user(
            username="super-sensitive-viewer",
            email="super-sensitive-viewer@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
            organization=federal_org,
        )
        state_admin = User.objects.create_user(
            username="state-sensitive-response-owner",
            email="state-sensitive-response-owner@example.com",
            password="StrongPass123!",
            role=UserRole.STATE_ADMIN,
            state=lagos,
            organization=lagos_org,
        )
        template = FormTemplate.objects.create(
            title="Sensitive Federal Template",
            purpose=FormTemplatePurpose.NATIONAL_INCIDENT_REPORTING,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_STANDARD,
            status=FormTemplateStatus.PUBLISHED,
            created_by=super_admin,
        )
        version = FormTemplateVersion.objects.create(
            template=template,
            version_number=1,
            schema_json={
                "sections": [
                    {
                        "key": "incident",
                        "questions": [
                            {"key": "count", "type": "number", "sensitivity": "public"},
                            {"key": "patient_detail", "type": "long_text", "sensitivity": "medical"},
                        ],
                    }
                ]
            },
            status=FormTemplateStatus.PUBLISHED,
        )
        assignment = FormAssignment.objects.create(
            title="Sensitive Federal Assignment",
            template=template,
            template_version=version,
            purpose=template.purpose,
            assigned_by=super_admin,
            assigned_to_type="selected_states",
            context_type="federal_assignment",
            status=AssignmentStatus.ACTIVE,
        )
        recipient = FormRecipient.objects.create(
            assignment=assignment,
            recipient_type="state_ministry",
            recipient_id=str(lagos.id),
            organization=lagos_org,
            status=FormRecipientStatus.SUBMITTED,
        )
        form_response = FormResponse.objects.create(
            assignment=assignment,
            template=template,
            template_version=version,
            recipient=recipient,
            respondent_user=state_admin,
            respondent_organization=lagos_org,
            response_json={"count": 1, "patient_detail": "Visible only to sensitive-detail users"},
            status=ResponseStatus.SUBMITTED,
            submitted_at=timezone.now(),
        )
        self.client.force_authenticate(super_admin)

        detail = self.client.get(f"/api/federal/forms/responses/{form_response.id}/")

        self.assertEqual(detail.status_code, 200, detail.data)
        self.assertEqual(payload(detail)["response_json"]["patient_detail"], "Visible only to sensitive-detail users")
        self.assertTrue(AuditLog.objects.filter(metadata__event="federal_form_response_viewed").exists())
        self.assertTrue(AuditLog.objects.filter(metadata__event="sensitive_response_viewed").exists())

    def test_direct_national_operational_assignment_requires_special_permission_and_is_audited(self):
        federal_org = Organization.objects.create(name="Federal Ministry of Health", organization_type=OrganizationType.FEDERAL_MINISTRY)
        super_admin = User.objects.create_user(
            username="super-operational-assigner",
            email="super-operational-assigner@example.com",
            password="StrongPass123!",
            role=UserRole.SUPER_ADMIN,
            organization=federal_org,
        )
        template = FormTemplate.objects.create(
            title="Exceptional Operational Assignment",
            purpose=FormTemplatePurpose.FEDERAL_ME_DATA_COLLECTION,
            owner_organization=federal_org,
            visibility=FormTemplateVisibility.FEDERAL_PRIVATE,
            status=FormTemplateStatus.PUBLISHED,
            created_by=super_admin,
        )
        FormTemplateVersion.objects.create(template=template, version_number=1, schema_json={"sections": []}, status=FormTemplateStatus.PUBLISHED)
        self.client.force_authenticate(super_admin)

        response = self.client.post(
            "/api/federal/forms/assignments/",
            {"title": "Exceptional Employer Assignment", "template": str(template.id), "recipient_scope": "employer"},
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(AuditLog.objects.filter(metadata__event="direct_national_operational_assignment_created").exists())

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
