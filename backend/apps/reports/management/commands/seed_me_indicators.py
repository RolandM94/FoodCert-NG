from django.core.management.base import BaseCommand

from apps.reports.models import MEIndicator


INDICATORS = [
    ("registration_coverage", "registered_food_handlers", "Registered food handlers", "Count of registered food handler profiles.", "count(food_handlers)", ["food_handlers"], "monthly", ["state", "lga", "employer"], "kpi_card"),
    ("registration_coverage", "registered_employers", "Registered employers", "Count of registered food businesses.", "count(employers)", ["employers"], "monthly", ["state", "lga", "establishment_category"], "kpi_card"),
    ("registration_coverage", "registered_branches", "Registered branches", "Count of registered employer branches.", "count(organization_units where type=branch)", ["organizations"], "monthly", ["state", "lga", "employer"], "bar_chart"),
    ("registration_coverage", "registered_medical_facilities", "Registered medical facilities", "Count of registered medical facilities.", "count(facilities)", ["facilities"], "monthly", ["state", "lga", "facility_type"], "bar_chart"),
    ("registration_coverage", "approved_medical_facilities", "Approved medical facilities", "Facilities with active approval.", "count(approved facilities)", ["facilities"], "monthly", ["state", "lga", "facility_type"], "kpi_card"),
    ("certification", "certificates_issued", "Certificates issued", "Certificates issued in the period.", "count(certificates issued)", ["certificates"], "monthly", ["state", "lga", "facility"], "line_chart"),
    ("certification", "active_certificates", "Active certificates", "Certificates active at period end.", "count(active certificates)", ["certificates"], "monthly", ["state", "lga", "employer"], "kpi_card"),
    ("certification", "expired_certificates", "Expired certificates", "Certificates expired at period end.", "count(expired certificates)", ["certificates"], "monthly", ["state", "lga", "employer"], "kpi_card"),
    ("certification", "certification_coverage_rate", "Certification coverage rate", "Certified food handlers divided by registered food handlers.", "active_certified_handlers / registered_food_handlers * 100", ["certificates", "food_handlers"], "monthly", ["state", "lga", "employer"], "trend_card"),
    ("certification", "state_validation_time", "Average state validation time", "Average time from state submission to certificate decision.", "avg(certificate_request.reviewed_at - submitted_at)", ["certificates"], "monthly", ["state", "facility"], "line_chart"),
    ("medical_assessment", "assessments_initiated", "Assessments initiated", "Assessments created in the period.", "count(assessments)", ["assessments"], "monthly", ["state", "facility", "employer"], "bar_chart"),
    ("medical_assessment", "assessments_completed", "Assessments completed", "Assessments with final decision or sign-off.", "count(completed assessments)", ["assessments"], "monthly", ["state", "facility", "doctor"], "bar_chart"),
    ("medical_assessment", "fit_decisions", "Fit decisions", "Assessments resulting in fit decision.", "count(fit decisions)", ["assessments"], "monthly", ["state", "facility"], "kpi_card"),
    ("medical_assessment", "temporarily_not_fit_decisions", "Temporarily not-fit decisions", "Assessments resulting in temporary exclusion.", "count(temp not fit decisions)", ["assessments"], "monthly", ["state", "facility"], "kpi_card"),
    ("medical_assessment", "lab_completion_rate", "Lab test completion rate", "Reviewed lab tests divided by requested lab tests.", "reviewed_lab_tests / requested_lab_tests * 100", ["assessments", "lab_tests"], "monthly", ["state", "facility", "test_type"], "trend_card"),
    ("vaccination", "typhoid_vaccination_coverage", "Typhoid vaccination coverage", "Food handlers with valid typhoid vaccination divided by registered handlers.", "valid_typhoid / registered_food_handlers * 100", ["vaccinations", "food_handlers"], "monthly", ["state", "lga", "employer"], "trend_card"),
    ("vaccination", "hepatitis_a_dose_1_coverage", "Hepatitis A dose 1 coverage", "Handlers with Hepatitis A dose 1 recorded.", "hep_a_dose_1 / registered_food_handlers * 100", ["vaccinations", "food_handlers"], "monthly", ["state", "lga", "employer"], "bar_chart"),
    ("vaccination", "hepatitis_a_dose_2_completion", "Hepatitis A dose 2 completion", "Handlers completing second Hepatitis A dose.", "hep_a_dose_2 / hep_a_dose_1 * 100", ["vaccinations"], "monthly", ["state", "lga", "employer"], "trend_card"),
    ("facility", "facilities_due_reaccreditation", "Facilities due for re-accreditation", "Approved facilities expiring within policy window.", "count(facilities expiring soon)", ["facilities"], "monthly", ["state", "lga", "facility_type"], "table"),
    ("facility", "facility_assessment_volume", "Facility assessment volume", "Assessment count by facility.", "count(assessments by facility)", ["assessments", "facilities"], "monthly", ["state", "facility"], "bar_chart"),
    ("facility", "facility_average_turnaround", "Facility average turnaround time", "Average assessment completion hours by facility.", "avg(assessment signed_at - created_at)", ["assessments", "facilities"], "monthly", ["state", "facility"], "line_chart"),
    ("employer_compliance", "employer_compliance_rate", "Employer compliance rate", "Active certificates divided by linked food handlers.", "active_certificates / linked_handlers * 100", ["employers", "certificates"], "monthly", ["state", "lga", "employer"], "trend_card"),
    ("employer_compliance", "branch_compliance_rate", "Branch compliance rate", "Active certificates divided by linked handlers per branch.", "branch_active_certificates / branch_handlers * 100", ["employers", "organizations", "certificates"], "monthly", ["state", "lga", "branch"], "bar_chart"),
    ("employer_compliance", "open_inspection_notices", "Branches with open inspection notices", "Branches linked to unresolved notices.", "count(branches with open notices)", ["inspections", "employers"], "monthly", ["state", "lga", "employer"], "table"),
    ("inspection_enforcement", "inspections_conducted", "Inspections conducted", "Inspections submitted or closed in period.", "count(inspections)", ["inspections"], "monthly", ["state", "lga", "inspector"], "bar_chart"),
    ("inspection_enforcement", "inspection_coverage_rate", "Inspection coverage rate", "Inspected employers divided by registered employers.", "inspected_employers / registered_employers * 100", ["inspections", "employers"], "monthly", ["state", "lga"], "trend_card"),
    ("inspection_enforcement", "corrective_action_completion_rate", "Corrective action completion rate", "Completed corrective actions divided by issued actions.", "completed_corrective_actions / issued_corrective_actions * 100", ["inspections"], "monthly", ["state", "lga"], "trend_card"),
    ("illness_return_to_work", "illness_reports", "Illness reports", "Illness reports submitted in period.", "count(illness_reports)", ["illness"], "monthly", ["state", "lga", "employer"], "line_chart"),
    ("illness_return_to_work", "return_to_work_pending", "Return-to-work pending cases", "Temporary exclusions awaiting clearance.", "count(return_to_work pending)", ["illness", "food_handlers"], "weekly", ["state", "lga", "employer"], "kpi_card"),
    ("illness_return_to_work", "average_exclusion_duration", "Average exclusion duration", "Average days between exclusion and clearance.", "avg(clearance_date - exclusion_date)", ["illness"], "monthly", ["state", "lga", "employer"], "line_chart"),
    ("finance", "assessment_revenue", "Assessment revenue", "Assessment payment revenue in the period.", "sum(successful assessment payments)", ["payments"], "monthly", ["state", "facility"], "kpi_card"),
    ("finance", "facility_settlement_amount", "Facility settlement amount", "Facility settlement total in the period.", "sum(facility_amount)", ["settlements"], "monthly", ["state", "facility"], "bar_chart"),
    ("finance", "failed_payment_rate", "Failed payment rate", "Failed payments divided by total payments.", "failed_payments / total_payments * 100", ["payments"], "monthly", ["state", "provider"], "trend_card"),
    ("data_quality", "duplicate_nin_flags", "Duplicate NIN flags", "Detected duplicate NIN records.", "count(duplicate_nin_flags)", ["food_handlers", "data_quality"], "weekly", ["state"], "kpi_card"),
    ("data_quality", "missing_profile_data", "Missing profile data", "Food handler profiles missing required fields.", "count(incomplete profiles)", ["food_handlers"], "weekly", ["state", "lga"], "table"),
    ("data_quality", "failed_verification_attempts", "Failed verification attempts", "Certificate verification attempts that failed.", "count(failed verification attempts)", ["certificates"], "weekly", ["state"], "line_chart"),
]


ADDITIONAL_INDICATORS = [
    ("certification", "certificates_revoked", "Certificates revoked", "Certificates revoked during the reporting period.", "count(revoked certificates)", ["certificates"], "monthly", ["state", "lga", "employer"], "kpi_card"),
    ("certification", "certificates_suspended", "Certificates suspended", "Certificates suspended during the reporting period.", "count(suspended certificates)", ["certificates"], "monthly", ["state", "lga", "employer"], "kpi_card"),
    ("certification", "certificate_expiry_30d", "Certificates expiring within 30 days", "Active certificates due to expire within 30 days.", "count(active certificates expiring within 30 days)", ["certificates"], "weekly", ["state", "lga", "employer"], "table"),
    ("medical_assessment", "declaration_review_completion_rate", "Declaration review completion rate", "Validated declarations divided by submitted declarations.", "validated_declarations / submitted_declarations * 100", ["assessments"], "monthly", ["state", "facility", "doctor"], "trend_card"),
    ("medical_assessment", "doctor_decision_turnaround", "Doctor decision turnaround", "Average hours from completed assessment inputs to doctor decision.", "avg(decision_signed_at - inputs_completed_at)", ["assessments"], "monthly", ["state", "facility", "doctor"], "line_chart"),
    ("vaccination", "vaccination_missing_records", "Missing vaccination records", "Handlers without required vaccination records.", "count(handlers missing vaccination records)", ["vaccinations", "food_handlers"], "weekly", ["state", "lga", "employer"], "table"),
    ("vaccination", "vaccination_due_30d", "Vaccinations due within 30 days", "Vaccination records due or expiring within 30 days.", "count(vaccinations due within 30 days)", ["vaccinations"], "weekly", ["state", "lga", "employer"], "kpi_card"),
    ("facility", "facility_accreditation_applications", "Facility accreditation applications", "Facility accreditation applications submitted in the period.", "count(accreditation applications)", ["facilities"], "monthly", ["state", "lga", "facility_type"], "bar_chart"),
    ("facility", "facility_approval_rate", "Facility approval rate", "Approved facility applications divided by reviewed applications.", "approved_facility_applications / reviewed_facility_applications * 100", ["facilities"], "monthly", ["state", "lga", "facility_type"], "trend_card"),
    ("facility", "facility_suspensions", "Facility suspensions", "Facilities suspended during the reporting period.", "count(suspended facilities)", ["facilities"], "monthly", ["state", "lga", "facility_type"], "kpi_card"),
    ("employer_compliance", "employers_without_certified_handlers", "Employers without certified handlers", "Employers with linked handlers but no active certificates.", "count(employers with zero certified handlers)", ["employers", "certificates"], "monthly", ["state", "lga", "establishment_category"], "table"),
    ("employer_compliance", "employers_with_expiring_certificates", "Employers with expiring certificates", "Employers with at least one certificate expiring within 30 days.", "count(employers with expiring certificates)", ["employers", "certificates"], "weekly", ["state", "lga", "establishment_category"], "kpi_card"),
    ("employer_compliance", "employer_vaccination_compliance_rate", "Employer vaccination compliance rate", "Handlers with valid required vaccination divided by linked handlers.", "valid_vaccinated_handlers / linked_handlers * 100", ["employers", "vaccinations"], "monthly", ["state", "lga", "employer"], "trend_card"),
    ("inspection_enforcement", "inspection_overdue_count", "Overdue inspections", "Assigned or scheduled inspections past their due date.", "count(overdue inspections)", ["inspections"], "weekly", ["state", "lga", "inspector"], "kpi_card"),
    ("inspection_enforcement", "enforcement_notices_issued", "Enforcement notices issued", "Inspections with enforcement action other than none.", "count(enforcement notices issued)", ["inspections"], "monthly", ["state", "lga", "enforcement_action"], "bar_chart"),
    ("inspection_enforcement", "high_priority_inspections", "High priority inspections", "High and critical priority inspections.", "count(high priority inspections)", ["inspections"], "weekly", ["state", "lga", "inspector"], "kpi_card"),
    ("inspection_enforcement", "inspection_average_compliance_score", "Average inspection compliance score", "Average compliance score across submitted inspections.", "avg(compliance_score)", ["inspections"], "monthly", ["state", "lga", "establishment_category"], "trend_card"),
    ("illness_return_to_work", "active_exclusions", "Active food handler exclusions", "Food handlers currently excluded due to illness or fitness decision.", "count(active exclusions)", ["illness", "food_handlers"], "weekly", ["state", "lga", "employer"], "kpi_card"),
    ("illness_return_to_work", "return_to_work_clearance_rate", "Return-to-work clearance rate", "Cleared return-to-work cases divided by reviewed cases.", "cleared_return_to_work / reviewed_return_to_work * 100", ["illness"], "monthly", ["state", "lga", "employer"], "trend_card"),
    ("illness_return_to_work", "illness_condition_distribution", "Illness condition distribution", "Illness reports grouped by suspected condition.", "count(illness reports by condition)", ["illness"], "monthly", ["state", "lga", "suspected_condition"], "pie_chart"),
    ("finance", "state_revenue_share", "State revenue share", "State revenue collected from successful transactions.", "sum(state revenue share)", ["payments", "settlements"], "monthly", ["state"], "line_chart"),
    ("finance", "platform_revenue", "Platform revenue", "Platform revenue collected from successful transactions.", "sum(platform revenue)", ["payments", "settlements"], "monthly", ["state"], "line_chart"),
    ("finance", "settlement_failure_rate", "Settlement failure rate", "Failed settlements divided by total settlement attempts.", "failed_settlements / total_settlements * 100", ["settlements"], "monthly", ["state", "facility"], "trend_card"),
    ("data_quality", "missing_lga_data", "Missing LGA data", "Records missing LGA assignment across core entities.", "count(records missing lga)", ["food_handlers", "employers", "facilities"], "weekly", ["state"], "table"),
    ("data_quality", "overdue_state_reports", "Overdue state reports", "State reports not submitted within policy window.", "count(overdue state reports)", ["reports"], "monthly", ["state"], "kpi_card"),
]


ALL_INDICATORS = INDICATORS + ADDITIONAL_INDICATORS


class Command(BaseCommand):
    help = "Seed default FoodCert NG M&E indicator definitions."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for category, code, name, description, formula, sources, frequency, disaggregation, visualization in ALL_INDICATORS:
            _indicator, was_created = MEIndicator.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "category": category,
                    "numerator_definition": description,
                    "denominator_definition": "Defined by formula denominator where applicable.",
                    "formula": formula,
                    "data_sources": sources,
                    "reporting_frequency": frequency,
                    "disaggregation_fields": disaggregation,
                    "target_value": None,
                    "warning_threshold": None,
                    "critical_threshold": None,
                    "visualization_type": visualization,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded M&E indicators: {created} created, {updated} updated."))
