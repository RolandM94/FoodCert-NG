# Food Handlers 2024 Policy Version Seed Configuration

## Purpose

This document provides the actual extracted policy configuration from the **National Guidelines for Food Handlers’ Medical Test 2024** for implementation in the existing Policy Version tool.

The Policy Version tool has already been built. Codex should **not redesign or rebuild** the policy module. Codex should use the existing policy creation APIs, models, seed files, forms, or admin screens to create the parent policy version and the attached policy standards/rule groups listed in this document.

## Important Implementation Rules

- Create one parent policy version: `FH-POL-2024-001`.
- Create the 16 attached standards/rule groups under the parent policy.
- Both assessment validity and certificate validity must be **6 months**.
- Typhoid vaccination validity must be **36 months**.
- Hepatitis A vaccination requires **two doses at 0 and 6 months**.
- Medical facility reaccreditation interval must be **12 months**.
- Certificates must support QR verification and central database validation.
- Food handler compliance must depend on valid certificate status within the 6-month validity period.
- Operational modules should read these rules from the active policy configuration, not from hardcoded values.

---

# 1. Parent Policy Version

```json
{
  "policy_code": "FH-POL-2024-001",
  "policy_name": "National Guidelines for Food Handlers’ Medical Test",
  "version_number": "1.0",
  "policy_year": 2024,
  "issuing_authority": "Federal Ministry of Health and Social Welfare",
  "status": "active",
  "effective_date": "2024-12-01",
  "source_document_name": "National Guidelines for Food Handlers’ Medical Test 2024",
  "description": "The national guideline establishing medical assessment, certification, vaccination, documentation, monitoring, and regulatory standards for food handlers in Nigeria.",
  "notes": "This policy version is extracted from the 2024 National Guidelines for Food Handlers’ Medical Test. It should be used as the active national standards baseline for the Food Handlers application."
}
```

---

# 2. Policy Standards / Rule Groups

## 2.1 Scope of Covered Food Handlers

```json
{
  "standard_code": "FH-SCOPE-2024-001",
  "standard_name": "Scope of Covered Food Handlers",
  "category": "scope",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines categories of food handlers required to undergo medical testing before handling food.",
  "applies_to": [
    "food_handler",
    "food_business_owner",
    "medical_facility",
    "state_ministry",
    "inspector",
    "federal_admin"
  ],
  "rule_parameters": {
    "medical_test_required_before_food_handling": true,
    "covered_food_handler_categories": [
      "Kitchen Staff",
      "Food Preparers",
      "Serving and Catering Staff",
      "Food Packers",
      "Bakery Workers",
      "Food Processing Operators",
      "Bartenders",
      "Dishwashers",
      "Food Delivery Personnel",
      "Food Stall and Street Food Vendors",
      "Food Storage Handlers",
      "Concession Stand Workers",
      "Airline Catering Vendors",
      "Train Catering Vendors",
      "Cruise Ship or Sea Vessel Catering Vendors",
      "Livestock Farmers",
      "Emergency Situation Workers"
    ]
  }
}
```

---

## 2.2 Covered Food Establishments

```json
{
  "standard_code": "FH-EST-2024-001",
  "standard_name": "Covered Food Establishments",
  "category": "establishment_coverage",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines the categories of food establishments subject to the Food Handlers Medical Test guideline.",
  "applies_to": [
    "food_business_owner",
    "food_establishment",
    "state_ministry",
    "lga",
    "inspector",
    "federal_admin"
  ],
  "rule_parameters": {
    "covered_establishment_categories": [
      "Restaurants and Cafes",
      "Bakeries and Pastry Shops",
      "Abattoirs, Slaughter Slabs, and Butcher Shops",
      "Grocery Stores and Supermarkets",
      "Food Trucks and Street Vendors",
      "Catering Services",
      "School Cafeterias",
      "Hospital Kitchens",
      "Bars and Pubs",
      "Food Processing Plants",
      "Hotels and Resorts",
      "Corporate Dining Facilities",
      "Food Markets and Stalls",
      "Airports and Train Stations",
      "Farms and Livestock Feed Processing Plants",
      "Daycare Centres"
    ]
  }
}
```

---

## 2.3 Medical Facility Prequalification and Accreditation Standard

```json
{
  "standard_code": "FH-FAC-2024-001",
  "standard_name": "Medical Facility Prequalification and Accreditation Standard",
  "category": "medical_facility_accreditation",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines eligibility, state mapping, monitoring, reaccreditation, and pricing rules for medical facilities approved to conduct food handler assessments.",
  "applies_to": [
    "medical_facility",
    "state_ministry",
    "federal_admin",
    "inspector"
  ],
  "rule_parameters": {
    "requires_prequalification": true,
    "prequalification_criteria_type": "uniform_national_criteria",
    "eligible_facility_ownership_types": [
      "public",
      "private"
    ],
    "requires_state_mapping": true,
    "assessment_reports_only_valid_from_prequalified_facilities": true,
    "food_handlers_must_use_approved_facilities_in_respective_state_or_fct": true,
    "prequalification_monitoring_authority": "State Ministries of Health",
    "reaccreditation_required": true,
    "reaccreditation_interval_months": 12,
    "assessment_price_standardized_per_state": true
  }
}
```

---

## 2.4 Food Handler Medical Assessment Workflow Standard

```json
{
  "standard_code": "FH-ASSMT-2024-001",
  "standard_name": "Food Handler Medical Assessment Workflow Standard",
  "category": "medical_assessment",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines the required medical assessment workflow for food handlers.",
  "applies_to": [
    "food_handler",
    "medical_facility",
    "doctor",
    "assessment_engine",
    "certificate_engine",
    "state_ministry"
  ],
  "rule_parameters": {
    "assessment_frequency_months": 6,
    "requires_health_declaration_form": true,
    "requires_food_handler_certification_of_declaration_form": true,
    "requires_medical_doctor_validation": true,
    "requires_physical_examination": true,
    "requires_laboratory_investigation": true,
    "requires_doctor_fitness_decision": true,
    "possible_assessment_outcomes": [
      "fit",
      "temporarily_unfit",
      "cleared_for_food_handling_duties"
    ],
    "physical_examination_indicators": [
      "Fever",
      "Jaundice",
      "Skin infections on hands, arms, or face",
      "Boils, styes, or sepsis on fingers",
      "Discharge from eyes, nose, ears, or mouth",
      "Diarrhea and/or vomiting",
      "Known history of being a typhoid carrier",
      "Sore throat",
      "Cough or flu"
    ],
    "reexamination_triggers": [
      "Jaundice",
      "Diarrhea",
      "Vomiting",
      "Fever",
      "Sore throat with fever",
      "Visibly infected skin lesions",
      "Discharges from ear, eye, or nose",
      "Cough or Flu"
    ]
  }
}
```

---

## 2.5 Mandatory Laboratory Test Standard

```json
{
  "standard_code": "FH-TEST-2024-001",
  "standard_name": "Mandatory Laboratory Test Standard",
  "category": "laboratory_test",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines the compulsory laboratory investigations required during food handler medical assessment.",
  "applies_to": [
    "food_handler",
    "medical_facility",
    "doctor",
    "laboratory",
    "assessment_engine",
    "certificate_engine"
  ],
  "rule_parameters": {
    "mandatory_tests": [
      {
        "test_name": "Stool microscopy, culture and sensitivity",
        "required": true
      },
      {
        "test_name": "Hepatitis A Antigen",
        "required": true
      }
    ],
    "allow_additional_tests_if_clinically_indicated": true,
    "additional_test_authority": "registered_medical_doctor",
    "additional_test_condition": "If clinically indicated or if foodborne disease is suspected"
  }
}
```

---

## 2.6 Vaccination Requirement Standard

```json
{
  "standard_code": "FH-VACC-2024-001",
  "standard_name": "Vaccination Requirement Standard",
  "category": "vaccination",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines food handler vaccination requirements for Typhoid and Hepatitis A.",
  "applies_to": [
    "food_handler",
    "medical_facility",
    "doctor",
    "food_business_owner",
    "certificate_engine"
  ],
  "rule_parameters": {
    "required_vaccinations": [
      {
        "vaccine_name": "Typhoid",
        "required": true,
        "certificate_required": true,
        "validity_months": 36,
        "dose_rule": "One dose every three years",
        "doctor_prescribes_if_absent_or_invalid": true
      },
      {
        "vaccine_name": "Hepatitis A",
        "required": true,
        "certificate_required": true,
        "dose_rule": "Two doses at 0 and 6 months intervals for full protection",
        "doctor_prescribes_if_absent_or_invalid": true
      }
    ],
    "accept_existing_valid_vaccination_certificate": true,
    "vaccination_certificate_must_be_certified_by_registered_medical_doctor": true
  }
}
```

---

## 2.7 Certificate and Assessment Validity Standard

```json
{
  "standard_code": "FH-VALIDITY-2024-001",
  "standard_name": "Certificate and Assessment Validity Standard",
  "category": "validity",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines validity rules for food handler medical assessments and fitness certificates.",
  "applies_to": [
    "food_handler",
    "food_business_owner",
    "medical_facility",
    "certificate_engine",
    "assessment_engine",
    "kpi_engine",
    "state_ministry",
    "federal_admin"
  ],
  "rule_parameters": {
    "assessment_validity_months": 6,
    "certificate_validity_months": 6,
    "certificate_expiry_basis": "certificate_issue_date",
    "renewal_required_before_expiry": true,
    "renewal_reminder_days_before_expiry": [
      30,
      14,
      7
    ],
    "expired_certificate_status": "expired",
    "compliance_rule": "A food handler is compliant only if they have a valid fitness certificate issued within the last 6 months.",
    "policy_interpretation_note": "Although the document contains a one-year certificate reference, the application shall enforce 6 months for both assessment validity and certificate validity as confirmed by product/policy owner."
  }
}
```

---

## 2.8 Fitness Certificate Issuance and QR Verification Standard

```json
{
  "standard_code": "FH-CERT-2024-001",
  "standard_name": "Fitness Certificate Issuance and QR Verification Standard",
  "category": "certification",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines certificate issuance, report generation, QR code verification, and central database verification requirements.",
  "applies_to": [
    "food_handler",
    "medical_facility",
    "doctor",
    "certificate_engine",
    "state_ministry",
    "federal_admin",
    "inspector"
  ],
  "rule_parameters": {
    "issue_certificate_for_fit_subjects": true,
    "issue_report_for_temporarily_unfit_subjects": true,
    "issue_report_for_cleared_subjects": true,
    "requires_qr_code": true,
    "qr_code_verification_enabled": true,
    "requires_central_database_storage": true,
    "central_database_administered_by_regulatory_bodies": true,
    "certificate_must_be_digitally_verifiable": true,
    "certificate_must_have_unique_identifier": true,
    "required_certificate_identity_fields": [
      "Full Name",
      "Date of Birth",
      "Gender",
      "Passport Picture",
      "National Identity Number"
    ]
  }
}
```

---

## 2.9 Illness Reporting and Exclusion Standard

```json
{
  "standard_code": "FH-ILL-2024-001",
  "standard_name": "Illness Reporting and Exclusion Standard",
  "category": "illness_management",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines illness reporting, exclusion from food handling, and re-examination requirements.",
  "applies_to": [
    "food_handler",
    "food_business_owner",
    "medical_facility",
    "doctor",
    "inspector"
  ],
  "rule_parameters": {
    "food_handler_must_report_illness": true,
    "report_to": [
      "food_handler_organization_management",
      "food_handler_association_management"
    ],
    "management_must_exclude_affected_handler_from_food_handling": true,
    "requires_reexamination_by_registered_medical_doctor": true,
    "exclusion_conditions": [
      "Jaundice",
      "Diarrhea",
      "Vomiting",
      "Fever",
      "Sore throat with fever",
      "Visibly infected skin lesions",
      "Discharges from ear, eye, or nose",
      "Cough or Flu"
    ],
    "noninfective_exception_allowed": true,
    "noninfective_exception_requires_evidence": true
  }
}
```

---

## 2.10 Return-to-Work Clearance Standard

```json
{
  "standard_code": "FH-RTW-2024-001",
  "standard_name": "Return-to-Work Clearance Standard",
  "category": "return_to_work",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines return-to-work rules for food handlers after illness or infection.",
  "applies_to": [
    "food_handler",
    "food_business_owner",
    "medical_facility",
    "doctor",
    "inspector"
  ],
  "rule_parameters": {
    "standard_exclusion_period_hours_after_symptoms_stop": 48,
    "symptom_resolution_basis": [
      "time_symptoms_naturally_cease",
      "end_of_symptom_treatment",
      "first_normal_stool_if_uncertain"
    ],
    "specific_infection_rules": [
      {
        "condition": "Vibrio cholerae",
        "return_to_work_requirement": "Medical clearance required with two consecutive negative stool samples taken at intervals of at least 24 hours."
      },
      {
        "condition": "Shigella dysenteriae, flexneri, and boydii",
        "return_to_work_requirement": "Medical clearance required with two consecutive negative stool samples taken at intervals of at least 48 hours."
      },
      {
        "condition": "Hepatitis A",
        "return_to_work_requirement": "Exclude for seven days after onset of jaundice or other symptoms. Medical advice required before return."
      },
      {
        "condition": "Infected or injured skin",
        "return_to_work_requirement": "May work only if infected area is completely covered with suitable waterproof dressing. Exclude if lesion cannot be effectively covered."
      },
      {
        "condition": "Entamoeba histolytica",
        "return_to_work_requirement": "Medical clearance required with a single negative stool sample taken at least one week after treatment ends."
      },
      {
        "condition": "Taenia solium",
        "return_to_work_requirement": "Exclude from direct handling and serving of open ready-to-eat foods until two negative stool tests at 1 and 2 weeks post-treatment."
      },
      {
        "condition": "Lassa Fever",
        "return_to_work_requirement": "Requires documentation of illness, medical clearance, and approval from health authorities."
      }
    ],
    "extra_hygiene_required_on_return": true
  }
}
```

---

## 2.11 Medical Records and Documentation Standard

```json
{
  "standard_code": "FH-DOC-2024-001",
  "standard_name": "Medical Records and Documentation Standard",
  "category": "documentation",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines documentation and record-keeping requirements for medical facilities conducting food handler assessments.",
  "applies_to": [
    "medical_facility",
    "doctor",
    "state_ministry",
    "federal_admin",
    "inspector"
  ],
  "rule_parameters": {
    "requires_written_reporting_and_documentation_policy": true,
    "requires_medical_records_unit_computers": true,
    "requires_computer_operators": true,
    "requires_predefined_health_declaration_form": true,
    "requires_laboratory_investigation_request_forms": true,
    "requires_radiology_investigation_request_forms": true,
    "requires_patient_files": true,
    "requires_qr_coded_certificate_format": true,
    "requires_internet_access": true,
    "requires_trained_medical_records_staff": true,
    "requires_trained_clinical_team": true,
    "requires_trained_non_clinical_team": true,
    "requires_confidentiality": true,
    "requires_safe_storage": true,
    "requires_record_retention_policy": true,
    "supports_hard_copy_records": true,
    "supports_electronic_medical_records": true
  }
}
```

---

## 2.12 Food Handler Identity and Unique Identifier Standard

```json
{
  "standard_code": "FH-ID-2024-001",
  "standard_name": "Food Handler Identity and Unique Identifier Standard",
  "category": "identity",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines the identity fields required for food handler records, certificate issuance, and verification.",
  "applies_to": [
    "food_handler",
    "medical_facility",
    "certificate_engine",
    "assessment_engine",
    "state_ministry",
    "federal_admin"
  ],
  "rule_parameters": {
    "required_certificate_identity_fields": [
      "Full Name",
      "Date of Birth",
      "Gender",
      "Passport Picture",
      "National Identity Number"
    ],
    "required_medical_record_identity_fields": [
      "Patient Name",
      "Medical Record Number",
      "Date of Birth",
      "Case Number",
      "National Identity Number",
      "Gender",
      "Passport Photograph"
    ],
    "requires_unique_certificate_identifier": true,
    "requires_unique_visit_case_number": true,
    "requires_unique_patient_medical_record_number": true,
    "nin_required": true,
    "passport_photograph_required": true
  }
}
```

---

## 2.13 Food Business Owner Responsibility Standard

```json
{
  "standard_code": "FH-FBO-2024-001",
  "standard_name": "Food Business Owner Responsibility Standard",
  "category": "fbo_responsibility",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines the obligations of Food Business Owners under the Food Handlers Medical Test guideline.",
  "applies_to": [
    "food_business_owner",
    "food_handler",
    "inspector",
    "state_ministry"
  ],
  "rule_parameters": {
    "must_inform_food_handlers_of_health_and_hygiene_obligations": true,
    "must_take_reasonable_measures_to_prevent_food_contamination": true,
    "must_prevent_unnecessary_contact_with_ready_to_eat_food": true,
    "must_prevent_spitting_smoking_or_tobacco_use_near_exposed_food": true,
    "health_information_use_limited_to_risk_mitigation": true,
    "must_maintain_up_to_date_vaccination_evidence": true,
    "must_preserve_health_status_confidentiality": true,
    "health_status_disclosure_requires_authorized_officer_or_consent": true,
    "must_reeducate_recovered_handlers_on_hand_hygiene": true,
    "must_report_foodborne_illness_as_required_by_law": true
  }
}
```

---

## 2.14 Food Handler Hygiene Practice Standard

```json
{
  "standard_code": "FH-HYGIENE-2024-001",
  "standard_name": "Food Handler Hygiene Practice Standard",
  "category": "food_handler_hygiene",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines required and prohibited hygiene practices for food handlers.",
  "applies_to": [
    "food_handler",
    "food_business_owner",
    "inspector",
    "state_ministry"
  ],
  "rule_parameters": {
    "requires_handwashing_before_work": true,
    "requires_handwashing_before_handling_food": true,
    "requires_handwashing_before_donning_gloves": true,
    "requires_use_of_provided_handwashing_facilities": true,
    "requires_reporting_infections_or_discharge_to_supervisor": true,
    "requires_covering_infected_sores": true,
    "requires_minimising_contact_with_ready_to_eat_foods": true,
    "requires_personal_grooming": true,
    "requires_vaccination_compliance": true,
    "requires_ppe": true,
    "required_ppe_examples": [
      "Face masks",
      "Hair nets"
    ],
    "prohibited_behaviours": [
      "Sneezing over unprotected food",
      "Coughing over unprotected food",
      "Blowing over unprotected food",
      "Consuming food over unprotected surfaces",
      "Using tobacco products in food handling areas",
      "Handling food without washing hands after contact with contaminants",
      "Wearing jewellery on hands or wrists while handling food",
      "Relieving oneself anywhere other than designated toilet facilities"
    ]
  }
}
```

---

## 2.15 Government Responsibility and Regulatory Oversight Standard

```json
{
  "standard_code": "FH-GOV-2024-001",
  "standard_name": "Government Responsibility and Regulatory Oversight Standard",
  "category": "government_oversight",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines responsibilities of Federal, State, FCT, and relevant MDAs for implementation, certification, awareness, policy use, and enforcement.",
  "applies_to": [
    "federal_admin",
    "state_ministry",
    "fct",
    "lga",
    "inspector",
    "medical_facility"
  ],
  "rule_parameters": {
    "state_ministries_must_establish_regular_testing_protocols": true,
    "testing_protocols_apply_to_36_states_and_fct": true,
    "state_government_certified_centres_must_implement_vaccination_programmes": true,
    "state_ministries_must_designate_reference_medical_facilities": true,
    "reference_facilities_must_provide_health_checks_vaccinations_and_certifications": true,
    "certification_responsibility": "State Ministries of Health and FCT",
    "official_certificates_must_be_digitally_verifiable": true,
    "certificates_generated_through_central_portal": true,
    "central_portal_domiciled_and_archived_within_federal_ministry": true,
    "government_mdas_must_promote_public_awareness": true,
    "federal_and_state_ministries_should_use_collected_data_for_policy_decisions": true,
    "states_and_respective_mdas_should_enforce_compliance": true,
    "punitive_measures_allowed_for_non_compliance": true
  }
}
```

---

## 2.16 Monitoring, Evaluation, Reporting and Feedback Standard

```json
{
  "standard_code": "FH-ME-2024-001",
  "standard_name": "Monitoring, Evaluation, Reporting and Feedback Standard",
  "category": "monitoring_and_evaluation",
  "enforcement_level": "mandatory",
  "status": "active",
  "description": "Defines M&E objectives, periodic reporting, stakeholder feedback, data analysis, and digital certification monitoring.",
  "applies_to": [
    "federal_admin",
    "state_ministry",
    "fct",
    "kpi_engine",
    "inspector"
  ],
  "rule_parameters": {
    "m_and_e_objectives": [
      "Ensure food handlers comply with medical testing and vaccination requirements",
      "Assess the impact of the guidelines on reducing foodborne diseases",
      "Provide data-driven insights for policy formulation and decision-making",
      "Foster accountability and transparency in the implementation process"
    ],
    "requires_periodic_state_reports_to_federal_ministry": true,
    "reporting_from": "State Ministries of Health",
    "reporting_to": "Federal Ministry of Health and Social Welfare",
    "requires_compliance_reports": true,
    "requires_impact_reports": true,
    "requires_feedback_loop": true,
    "requires_stakeholder_feedback_channels": true,
    "requires_data_analysis": true,
    "requires_digital_certification_monitoring": true
  }
}
```

---

# 3. Codex Implementation Prompt

```text
The Policy Version tool already exists. Do not rebuild or redesign it.

Create or seed the Food Handlers 2024 policy version and its standards using the existing policy version system.

Create one parent policy version:
FH-POL-2024-001 — National Guidelines for Food Handlers’ Medical Test, Version 1.0, Year 2024, issued by the Federal Ministry of Health and Social Welfare.

Under this parent policy, create the following 16 active standards/rule groups:

1. FH-SCOPE-2024-001 — Scope of Covered Food Handlers
2. FH-EST-2024-001 — Covered Food Establishments
3. FH-FAC-2024-001 — Medical Facility Prequalification and Accreditation Standard
4. FH-ASSMT-2024-001 — Food Handler Medical Assessment Workflow Standard
5. FH-TEST-2024-001 — Mandatory Laboratory Test Standard
6. FH-VACC-2024-001 — Vaccination Requirement Standard
7. FH-VALIDITY-2024-001 — Certificate and Assessment Validity Standard
8. FH-CERT-2024-001 — Fitness Certificate Issuance and QR Verification Standard
9. FH-ILL-2024-001 — Illness Reporting and Exclusion Standard
10. FH-RTW-2024-001 — Return-to-Work Clearance Standard
11. FH-DOC-2024-001 — Medical Records and Documentation Standard
12. FH-ID-2024-001 — Food Handler Identity and Unique Identifier Standard
13. FH-FBO-2024-001 — Food Business Owner Responsibility Standard
14. FH-HYGIENE-2024-001 — Food Handler Hygiene Practice Standard
15. FH-GOV-2024-001 — Government Responsibility and Regulatory Oversight Standard
16. FH-ME-2024-001 — Monitoring, Evaluation, Reporting and Feedback Standard

Use the JSON payloads provided in this markdown file as the seed data.

Important:
- Both assessment validity and certificate validity must be 6 months.
- Typhoid vaccination validity must be 36 months.
- Hepatitis A vaccination requires two doses at 0 and 6 months.
- Medical facility reaccreditation interval is 12 months.
- Certificates must support QR verification and central database validation.
- Food handler compliance must depend on valid certificate status within the 6-month validity period.
- Do not hardcode these rules elsewhere; operational modules should read from this active policy configuration.
```

---

# 4. Suggested Acceptance Criteria for Codex

```text
1. Parent policy version FH-POL-2024-001 is created successfully.
2. All 16 standards are created under FH-POL-2024-001.
3. Each standard uses the standard_code, category, applies_to, description, and rule_parameters provided in this file.
4. FH-VALIDITY-2024-001 has assessment_validity_months = 6.
5. FH-VALIDITY-2024-001 has certificate_validity_months = 6.
6. FH-VACC-2024-001 has Typhoid validity_months = 36.
7. FH-FAC-2024-001 has reaccreditation_interval_months = 12.
8. Seed operation is idempotent and does not create duplicate policy versions or standards if re-run.
9. If an existing record with the same code exists, Codex should update it or skip it based on the existing system’s seeding convention.
10. The created policy version is visible in the Policy Version tool.
11. The standards are visible under the parent policy version.
12. Operational modules can retrieve the active standards from the existing policy rules service.
```
