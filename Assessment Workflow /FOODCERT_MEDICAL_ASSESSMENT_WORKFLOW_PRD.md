# PRD: Medical Assessment Workflow Module — FoodCert NG

## 1. Module Name

**Medical Assessment Workflow Module**

## 2. Product Context

The Medical Assessment Workflow Module is the core certification workflow engine of **FoodCert NG**. It manages the end-to-end medical assessment process that determines whether a food handler is fit to handle food.

This module connects food handlers, employers, approved medical facilities, doctors, laboratory staff, vaccination records, payment confirmation, NIN verification, State Ministry certificate validation, certificate generation, and return-to-work management.

The module must enforce the national guideline requirements for food handler medical assessment, including health declaration, doctor validation, physical examination, laboratory investigations, vaccination review, medical fitness decision, re-examination triggers, illness handling, and documentation.

---

# 3. Product Goal

To provide a structured, auditable, privacy-safe, and rule-driven workflow for assessing the medical fitness of food handlers before they are issued State Ministry-approved fitness certificates.

---

# 4. Core Objectives

The Medical Assessment Workflow Module must:

1. Create and manage medical assessment records for food handlers.
2. Enforce prerequisite checks such as NIN verification, payment confirmation, facility approval, and appointment scheduling.
3. Digitize the food handler health declaration form.
4. Allow doctors to validate declarations.
5. Allow doctors to conduct physical examinations.
6. Allow doctors to request required and additional laboratory tests.
7. Allow laboratory staff to upload and submit results.
8. Allow doctors to review lab results.
9. Allow doctors to review and record vaccination status.
10. Allow doctors to make standardized fitness decisions.
11. Trigger return-to-work workflows where required.
12. Submit fit assessments to State Ministry validation queue.
13. Prevent certificate issuance if workflow requirements are incomplete.
14. Protect sensitive medical information from employers and public users.
15. Maintain a full audit trail for medical and regulatory actions.

---

# 5. Key Actors

## 5.1 Food Handler

The food handler is the subject of the assessment.

Can:

- Start or view an assessment.
- Complete health declaration.
- View assessment status.
- View required next steps.
- View appointment details.
- View limited lab status.
- View vaccination status.
- View final fitness outcome.
- Download certificate or report where permitted.
- Report illness or symptoms after certification.

Cannot:

- Edit declaration after doctor validation.
- View internal doctor notes unless policy allows.
- Edit lab results.
- Edit medical decision.
- Issue certificate.

## 5.2 Employer

The employer monitors the operational fitness status of linked food handlers.

Can:

- View assessment status category.
- View certificate status.
- View vaccination compliance status.
- Send renewal or assessment reminders.
- Report illness for a food handler.
- View return-to-work status.
- View operational fitness decision.

Cannot:

- View lab results.
- View doctor notes.
- View diagnosis.
- View declaration answers.
- View full NIN.
- Override medical decision.
- Mark a food handler fit.

## 5.3 Medical Facility Admin

Can:

- View facility assessment queue.
- Assign doctors.
- Monitor workflow status.
- View administrative assessment status.
- Submit completed assessment to State Ministry where permitted.
- Respond to State clarification requests.
- View facility-level assessment reports.

Cannot:

- Make doctor fitness decision unless also assigned as doctor.
- Issue State Ministry certificate directly.
- Override doctor decision.
- Change lab results.

## 5.4 Doctor

Can:

- Review assigned assessments.
- Validate health declaration.
- Conduct physical examination.
- Request lab tests.
- Review lab results.
- Review vaccination status.
- Prescribe vaccination where required.
- Make fitness decision.
- Set return-to-work requirements.
- Digitally sign assessment decision.
- Submit fit assessment for State validation.

Cannot:

- Approve State certificate issuance.
- Process payments.
- Change payment status.
- Edit lab result values after submission, except through correction workflow.
- View unrelated assessments outside facility/assignment scope.

## 5.5 Laboratory Staff

Can:

- View lab test requests.
- Mark sample collected.
- Enter lab result summary.
- Upload lab result document.
- Submit result to doctor.
- Mark repeat required or inconclusive, where permitted.

Cannot:

- Make final fitness decision.
- Validate certificate issuance.
- Issue certificate.
- View unrelated clinical notes unless authorized.

## 5.6 State Ministry Verification Officer

Can:

- View completed fit assessments submitted for validation.
- Verify assessment completion checklist.
- Approve or reject certificate issuance.
- Request clarification from facility.
- View assessment summary and required evidence.
- Trigger certificate generation after approval.

Cannot:

- Change doctor’s medical decision.
- Edit lab results.
- Edit declaration.
- Bypass required workflow checks unless explicit override permission exists.

## 5.7 Federal Ministry User

Can:

- View national aggregate assessment indicators.
- Monitor assessment trends.
- View state performance.
- View data quality alerts.
- View restricted records only where explicitly authorized.

Cannot by default:

- Edit state assessment workflows.
- Issue state certificates.
- Access individual medical details unless specifically authorized.

---

# 6. Assessment Lifecycle Overview

## 6.1 High-Level Flow

```txt
Food handler profile complete
→ NIN verified
→ Assessment payment confirmed
→ Appointment booked with approved facility
→ Health declaration submitted
→ Doctor validates declaration
→ Doctor conducts physical examination
→ Lab tests requested
→ Lab results submitted
→ Doctor reviews lab results
→ Vaccination status reviewed
→ Doctor makes fitness decision
→ If fit: submit to State Ministry validation
→ State approves certificate issuance
→ Certificate generated and QR verifiable
```

## 6.2 Alternative Outcomes

The assessment may also result in:

- Temporarily Not Fit
- Not Fit
- Requires Vaccination
- Requires Lab Test
- Requires Re-Examination
- Requires Treatment
- Requires Public Health Clearance
- Return-to-Work Clearance Pending

---

# 7. Assessment Prerequisites

Before assessment can be activated, the system should check:

1. Food handler profile is complete.
2. NIN verification is successful or official override is approved.
3. Selected medical facility is approved and active.
4. Facility accreditation is not expired or suspended.
5. Assessment payment is successful, unless policy permits otherwise.
6. Appointment is booked or facility has started walk-in assessment, where permitted.
7. Food handler has consented to medical assessment and data processing.
8. Employer linkage and branch assignment are captured where applicable.

## 7.1 Blocking Rules

The system must block assessment progression if:

- NIN is not verified and override is not approved.
- Facility is not approved.
- Facility accreditation is suspended or expired.
- Payment is not confirmed and policy requires payment before assessment.
- Food handler profile is incomplete.
- Doctor is not authorized for the facility.

---

# 8. Assessment Status Engine

## 8.1 Assessment Statuses

Recommended statuses:

- Draft
- Awaiting NIN Verification
- Awaiting Payment
- Payment Confirmed
- Appointment Booked
- Declaration Pending
- Declaration Submitted
- Declaration Validated
- Physical Exam Pending
- Physical Exam Completed
- Lab Tests Pending
- Lab Results Submitted
- Lab Results Reviewed
- Vaccination Review Pending
- Vaccination Reviewed
- Doctor Decision Pending
- Requires Vaccination
- Requires Lab Test
- Requires Re-Examination
- Temporarily Not Fit
- Not Fit
- Fit
- Ready for State Submission
- Submitted to State
- Clarification Requested
- Clarification Responded
- Approved by State
- Rejected by State
- Certificate Issued
- Closed

## 8.2 Status Transition Rules

| From | To | Trigger |
|---|---|---|
| Draft | Awaiting NIN Verification | Assessment created |
| Awaiting NIN Verification | Awaiting Payment | NIN verified |
| Awaiting Payment | Payment Confirmed | Payment successful |
| Payment Confirmed | Appointment Booked | Appointment confirmed |
| Appointment Booked | Declaration Pending | Appointment active |
| Declaration Pending | Declaration Submitted | Food handler submits declaration |
| Declaration Submitted | Declaration Validated | Doctor validates |
| Declaration Validated | Physical Exam Pending | Doctor starts assessment |
| Physical Exam Pending | Physical Exam Completed | Doctor completes exam |
| Physical Exam Completed | Lab Tests Pending | Doctor requests tests |
| Lab Tests Pending | Lab Results Submitted | Lab uploads results |
| Lab Results Submitted | Lab Results Reviewed | Doctor reviews results |
| Lab Results Reviewed | Vaccination Review Pending | Lab review complete |
| Vaccination Review Pending | Vaccination Reviewed | Doctor reviews vaccination |
| Vaccination Reviewed | Doctor Decision Pending | Required evidence complete |
| Doctor Decision Pending | Fit | Doctor marks fit |
| Doctor Decision Pending | Temporarily Not Fit | Doctor marks temporary restriction |
| Doctor Decision Pending | Not Fit | Doctor marks not fit |
| Fit | Ready for State Submission | Doctor signs decision |
| Ready for State Submission | Submitted to State | Facility submits |
| Submitted to State | Approved by State | State approves |
| Approved by State | Certificate Issued | Certificate generated |
| Any active stage | Closed | Assessment cancelled/closed according to policy |

## 8.3 Status Calculation

The backend should be the source of truth for assessment status. The frontend must not calculate final workflow status independently.

---

# 9. Health Declaration Workflow

## 9.1 Purpose

The health declaration captures the food handler’s self-reported health status and exposure history before doctor review.

## 9.2 Declaration Questions

The declaration form must include Yes/No questions:

1. Are you now, or have you over the last seven days, suffered from diarrhoea/vomiting?
2. Have you suffered from fever since more than one week ago?
3. Are you currently suffering from skin trouble affecting hands, arms, or face?
4. Do you have boils, styes, or sepsis on your fingers or hands?
5. Do you have discharge from eye, ear, nose, gums, or mouth?
6. Do you suffer from recurring skin or ear infection?
7. Do you suffer from recurring bowel disorder?
8. In the last five days, have you been in contact with anyone who may have been suffering from cholera?
9. In the last seven days, have you been in contact with anyone with diarrhoea or vomiting?
10. In the last 21 days, have you been in contact with anyone who may have been suffering from typhoid, paratyphoid, or jaundice?
11. Have you ever had, or are you now known to be a carrier of typhoid or paratyphoid?
12. Have you ever had, or are you now known to have typhoid fever?

## 9.3 Declaration Fields

- Assessment
- Food handler
- Declaration answers
- Risk flag
- Certified true checkbox
- Submitted at
- Validated by doctor
- Validated at
- Version number

## 9.4 Risk Flag Logic

Set `risk_flag = true` if any answer suggests potential food safety risk.

Risk flags should be triggered by:

- Diarrhoea/vomiting
- Fever
- Skin trouble
- Boils/styes/sepsis
- Discharge
- Cholera contact
- Diarrhoea/vomiting contact
- Typhoid/paratyphoid/jaundice contact
- Carrier history
- Current or previous typhoid

## 9.5 Declaration UX Rules

- Food handler can save draft before submission.
- Food handler must certify answers are true before submission.
- Once submitted, declaration is read-only to the food handler.
- After doctor validation, declaration is locked.
- Corrections require a new version or doctor-authorized reopening.
- Risk answers should show a non-punitive warning: “This does not automatically disqualify you. A doctor will review your response.”

## 9.6 Doctor Declaration Validation

Doctor can:

- Validate declaration.
- Request clarification.
- Mark additional examination required.
- Proceed to physical examination.

---

# 10. Physical Examination Workflow

## 10.1 Purpose

The doctor physically examines the food handler and records findings relevant to food safety.

## 10.2 Physical Examination Checklist

Doctor records Yes/No and notes for:

- Fever
- Jaundice
- Skin infection on hands, arms, or face
- Boils, styes, or sepsis on fingers
- Discharge from eye, ear, nose, gums, or mouth
- Diarrhoea
- Vomiting
- Sore throat with fever
- Cough or flu
- Known history of being a typhoid carrier
- Other clinical observations

## 10.3 Physical Examination Fields

- Assessment
- Doctor
- Examination date/time
- Checklist responses
- Doctor notes
- Risk flag
- Completed at
- Digital signature, where required

## 10.4 Physical Examination Actions

Doctor can:

- Save draft.
- Complete examination.
- Request lab tests.
- Request vaccination review.
- Mark temporarily not fit.
- Request re-examination.
- Proceed to decision when requirements are complete.

## 10.5 Physical Examination Rules

- Only assigned/authorized doctor can complete exam.
- Doctor notes are sensitive.
- Employer cannot view exam details.
- Public verifier cannot view exam details.
- Physical exam completion must be audit logged.

---

# 11. Laboratory Test Workflow

## 11.1 Purpose

The lab workflow manages required and additional laboratory investigations.

## 11.2 Required Tests

The module must support required tests:

- Stool microscopy
- Stool culture and sensitivity
- Hepatitis A antigen

## 11.3 Additional Tests

Doctor can request additional tests such as:

- Typhoid-specific test
- Cholera test
- Other clinically indicated test
- Other foodborne disease test

## 11.4 Lab Test Request Flow

```txt
Doctor requests lab test
→ Lab request appears in lab queue
→ Lab staff collects sample
→ Lab staff records result
→ Lab staff uploads result file
→ Result submitted to doctor
→ Doctor reviews result
```

## 11.5 Lab Test Statuses

- Requested
- Sample Collection Pending
- Sample Collected
- In Progress
- Result Uploaded
- Positive
- Negative
- Inconclusive
- Repeat Required
- Submitted to Doctor
- Reviewed by Doctor

## 11.6 Lab Test Fields

- Assessment
- Test type
- Requested by doctor
- Assigned lab staff
- Sample collection date/time
- Result status
- Result summary
- Result file
- Result submitted by
- Submitted at
- Reviewed by doctor
- Reviewed at
- Doctor review notes

## 11.7 Lab Result Review Rules

- Positive results must be flagged for doctor review.
- Inconclusive results should allow repeat test request.
- Repeat test must create linked lab request.
- Lab staff cannot make fitness decision.
- Employer cannot view detailed lab results.
- Public verifier cannot view lab results.
- Lab result access must be logged.

---

# 12. Vaccination Review Workflow

## 12.1 Purpose

The module must review required food handler vaccination status.

## 12.2 Vaccines

Required vaccine records:

- Typhoid
- Hepatitis A

Other vaccines may be added through policy configuration.

## 12.3 Vaccination Rules

- Typhoid vaccination validity defaults to 3 years.
- Hepatitis A requires two doses at 0 and 6 months.
- If typhoid certificate is missing or expired, doctor should prescribe or administer typhoid vaccine.
- If Hepatitis A vaccination is missing or incomplete, doctor should prescribe or administer Hepatitis A vaccine.
- Vaccine requirements should be configurable by policy.

## 12.4 Vaccination Review Fields

- Assessment
- Food handler
- Vaccine type
- Dose number
- Date of vaccination
- Brand name
- Batch number
- Vaccinator name
- Facility name/address
- Certificate upload
- Expiry date
- Next dose date
- Review status
- Reviewed by doctor
- Reviewed at

## 12.5 Vaccination Review Statuses

- Not Submitted
- Pending Review
- Valid
- Missing
- Expired
- Incomplete
- Rejected
- Vaccination Prescribed
- Vaccination Administered

## 12.6 Vaccination Actions

Doctor can:

- Mark valid.
- Mark missing.
- Mark expired.
- Mark incomplete.
- Prescribe vaccine.
- Record vaccine administered.
- Set next dose date.
- Continue to decision.

## 12.7 Employer Visibility

Employers see only:

- Vaccination compliant
- Vaccination due
- Vaccination expired
- Second dose pending

Employers do not see clinical notes.

---

# 13. Fitness Decision Workflow

## 13.1 Purpose

The doctor issues a standardized medical fitness decision after all required assessment evidence is complete.

## 13.2 Decision Options

- Fit to Work
- Temporarily Not Fit
- Not Fit
- Requires Vaccination
- Requires Lab Test
- Requires Re-Examination
- Requires Treatment
- Requires Public Health Clearance
- Return to Work on Specific Date

## 13.3 Fit-to-Work Requirements

The backend should allow `Fit to Work` only if:

- Food handler profile complete
- NIN verified or override approved
- Payment confirmed
- Facility approved and active
- Doctor authorized
- Declaration validated
- Physical exam completed
- Required lab results submitted and reviewed
- Vaccination reviewed
- No unresolved blocking symptoms or illness report
- Doctor digital sign-off completed

## 13.4 Temporarily Not Fit

Doctor may mark temporarily not fit where risks are present but expected to resolve.

Examples:

- Diarrhoea
- Vomiting
- Fever
- Jaundice
- Cough/flu
- Infected skin lesions
- Positive/inconclusive lab findings pending review
- Missing required vaccination pending administration
- Clearance needed

Temporarily not fit should trigger:

- Employer operational status update
- Food handler notification
- Return-to-work requirements
- Medical review follow-up

## 13.5 Not Fit

Doctor may mark not fit if food handler is medically unfit for food handling according to clinical judgment or policy.

Not fit should generate:

- Medical report
- Operational status update
- No certificate submission
- Follow-up or appeal workflow, if policy allows

## 13.6 Requires Public Health Clearance

Use where disease-specific or regulatory clearance is needed.

Examples:

- Cholera
- Shigella
- Hepatitis A
- Amoebic dysentery
- Taenia solium
- Lassa fever
- Other reportable/high-risk conditions

## 13.7 Decision Finalization

Once doctor finalizes decision:

- Decision becomes immutable.
- Audit log is created.
- If fit, assessment becomes ready for State submission.
- If temporarily not fit, return-to-work workflow is created.
- If not fit, medical report is generated.
- Employer sees only operational category.

---

# 14. Return-to-Work Trigger

## 14.1 Purpose

The assessment workflow must trigger return-to-work handling when a food handler is temporarily excluded or becomes unfit due to illness.

## 14.2 Trigger Conditions

Return-to-work workflow may be triggered by:

- Doctor marks temporarily not fit.
- Employer reports illness.
- Food handler reports illness.
- Lab result indicates need for clearance.
- State/inspector flags handler during inspection.

## 14.3 Return-to-Work Data

Capture:

- Exclusion start date
- Symptom start date
- Symptom end date
- Required clearance tests
- Required clearance notes
- Earliest return date
- Doctor clearance decision
- Public health authority approval, where required

## 14.4 General Rule

For diarrhoea/vomiting:

- Exclude until 48 hours after symptoms stop.

## 14.5 Special Rules

| Condition | Rule |
|---|---|
| General diarrhoea/vomiting | Exclude until 48 hours after symptoms stop |
| Cholera | Require medical clearance and two negative stool samples at least 24 hours apart |
| Shigella | Require medical clearance and two negative stool samples at least 48 hours apart |
| Hepatitis A | Exclude for seven days after onset of jaundice or other symptoms |
| Infected skin lesion | Allow only if completely covered; otherwise exclude from food handling |
| Amoebic dysentery | Require one negative stool sample at least one week after treatment |
| Taenia solium | Require two negative stool tests at 1 and 2 weeks post-treatment |
| Lassa fever | Require medical documentation, clearance, and health authority approval |

---

# 15. Submission to State Ministry Validation

## 15.1 Purpose

Fit assessments must be submitted to the State Ministry for final validation before certificate issuance.

## 15.2 Submission Requirements

Before submission:

- Doctor decision is `Fit to Work`.
- Doctor signed final decision.
- Required evidence is complete.
- Facility is approved and active.
- Payment confirmed.
- NIN verified or override approved.
- Assessment has no unresolved clarification.
- Medical report/assessment summary is generated.

## 15.3 Submission Flow

```txt
Doctor marks Fit
→ Facility reviews administrative completeness
→ Assessment marked Ready for State Submission
→ Facility submits to State
→ State Verification Desk reviews
→ State approves/rejects/requests clarification
```

## 15.4 Clarification Flow

If State requests clarification:

- Assessment status becomes `Clarification Requested`.
- Facility admin and doctor receive notification.
- Facility responds.
- Assessment status becomes `Clarification Responded`.
- State continues validation.

---

# 16. Medical Assessment Reports

## 16.1 Report Types

The workflow should generate:

- Assessment Summary Report
- Medical Examination Report
- Temporarily Not Fit Report
- Return-to-Work Clearance Report
- Vaccination Review Report
- Lab Summary Report, restricted

## 16.2 Report Access

| User Type | Report Access |
|---|---|
| Doctor | Full medical report |
| Lab Staff | Lab-related section only |
| Facility Admin | Operational/administrative report, role-limited |
| Medical Records Staff | Completed documentation |
| State Ministry | Assessment summary and required evidence |
| Employer | Operational fitness status only |
| Food Handler | Their certificate/report where permitted |
| Public | No assessment report access |

---

# 17. Privacy and Data Protection

## 17.1 Sensitive Medical Data

Sensitive data includes:

- Declaration answers
- Doctor notes
- Lab results
- Diagnosis
- Treatment notes
- Public health clearance notes
- Full NIN
- Internal medical report

## 17.2 Privacy Rules

- Employers cannot view sensitive medical data.
- Public verifiers cannot view sensitive medical data.
- Finance users cannot view sensitive medical data.
- State/Federal access must be role-based.
- Full NIN should be masked unless authorized.
- All sensitive access must be audit logged.
- Reports must use role-safe serializers.
- API endpoints must separate public, employer-safe, medical, and regulatory serializers.

---

# 18. Audit Logging

Create audit logs for:

- Assessment created
- NIN prerequisite checked
- Payment prerequisite checked
- Appointment linked
- Declaration submitted
- Declaration validated
- Declaration reopened/versioned
- Physical exam started
- Physical exam completed
- Lab test requested
- Sample collected
- Lab result submitted
- Lab result reviewed
- Vaccination reviewed
- Vaccine prescribed/administered
- Doctor decision drafted
- Doctor decision finalized
- Assessment submitted to State
- State clarification requested
- Clarification response submitted
- Return-to-work workflow created
- Sensitive medical record viewed
- Assessment cancelled/closed

---

# 19. Data Model Requirements

## 19.1 MedicalAssessment

```python
class MedicalAssessment(models.Model):
    id = models.UUIDField(primary_key=True)
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.CASCADE)
    employer = models.ForeignKey("employers.Employer", null=True, blank=True, on_delete=models.SET_NULL)
    business_branch = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.PROTECT)
    doctor = models.ForeignKey("accounts.User", null=True, blank=True, related_name="doctor_assessments", on_delete=models.SET_NULL)
    appointment = models.ForeignKey("appointments.Appointment", null=True, blank=True, on_delete=models.SET_NULL)
    payment_transaction = models.ForeignKey("payments.PaymentTransaction", null=True, blank=True, on_delete=models.SET_NULL)
    state = models.ForeignKey("geography.State", on_delete=models.PROTECT)
    status = models.CharField(max_length=80)
    declaration_status = models.CharField(max_length=50)
    physical_exam_status = models.CharField(max_length=50)
    lab_status = models.CharField(max_length=50)
    vaccination_status = models.CharField(max_length=50)
    final_decision = models.CharField(max_length=80, blank=True)
    return_to_work_date = models.DateField(null=True, blank=True)
    submitted_to_state_at = models.DateTimeField(null=True, blank=True)
    state_validation_status = models.CharField(max_length=50, blank=True)
    doctor_signed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 19.2 HealthDeclaration

```python
class HealthDeclaration(models.Model):
    id = models.UUIDField(primary_key=True)
    assessment = models.ForeignKey("assessments.MedicalAssessment", on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=1)
    diarrhoea_vomiting_last_7_days = models.BooleanField(default=False)
    fever_more_than_one_week = models.BooleanField(default=False)
    skin_trouble = models.BooleanField(default=False)
    boils_styes_sepsis = models.BooleanField(default=False)
    discharge_eye_ear_nose_mouth = models.BooleanField(default=False)
    recurring_skin_or_ear_infection = models.BooleanField(default=False)
    recurring_bowel_disorder = models.BooleanField(default=False)
    cholera_contact_last_5_days = models.BooleanField(default=False)
    diarrhoea_vomiting_contact_last_7_days = models.BooleanField(default=False)
    typhoid_paratyphoid_jaundice_contact_last_21_days = models.BooleanField(default=False)
    typhoid_or_paratyphoid_carrier = models.BooleanField(default=False)
    previous_or_current_typhoid = models.BooleanField(default=False)
    certified_true = models.BooleanField(default=False)
    risk_flag = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    validated_by_doctor = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    validated_at = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 19.3 PhysicalExamination

```python
class PhysicalExamination(models.Model):
    id = models.UUIDField(primary_key=True)
    assessment = models.ForeignKey("assessments.MedicalAssessment", on_delete=models.CASCADE)
    doctor = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    fever = models.BooleanField(default=False)
    jaundice = models.BooleanField(default=False)
    skin_infection_hands_arms_face = models.BooleanField(default=False)
    boils_styes_sepsis_finger = models.BooleanField(default=False)
    discharge_eye_ear_nose_mouth = models.BooleanField(default=False)
    diarrhoea = models.BooleanField(default=False)
    vomiting = models.BooleanField(default=False)
    sore_throat_with_fever = models.BooleanField(default=False)
    cough_or_flu = models.BooleanField(default=False)
    typhoid_carrier_history = models.BooleanField(default=False)
    other_observations = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    risk_flag = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 19.4 LabTest

```python
class LabTest(models.Model):
    id = models.UUIDField(primary_key=True)
    assessment = models.ForeignKey("assessments.MedicalAssessment", on_delete=models.CASCADE)
    requested_by_doctor = models.ForeignKey("accounts.User", related_name="requested_lab_tests", on_delete=models.PROTECT)
    performed_by_lab_user = models.ForeignKey("accounts.User", null=True, blank=True, related_name="performed_lab_tests", on_delete=models.SET_NULL)
    test_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    sample_collected_at = models.DateTimeField(null=True, blank=True)
    result_status = models.CharField(max_length=50, blank=True)
    result_summary = models.TextField(blank=True)
    result_file_url = models.URLField(blank=True)
    reviewed_by_doctor = models.ForeignKey("accounts.User", null=True, blank=True, related_name="reviewed_lab_tests", on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    parent_lab_test = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 19.5 VaccinationReview

```python
class VaccinationReview(models.Model):
    id = models.UUIDField(primary_key=True)
    assessment = models.ForeignKey("assessments.MedicalAssessment", on_delete=models.CASCADE)
    food_handler = models.ForeignKey("food_handlers.FoodHandlerProfile", on_delete=models.CASCADE)
    vaccine_type = models.CharField(max_length=100)
    dose_number = models.PositiveIntegerField(null=True, blank=True)
    date_of_vaccination = models.DateField(null=True, blank=True)
    brand_name = models.CharField(max_length=255, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    vaccinator_name = models.CharField(max_length=255, blank=True)
    facility_name = models.CharField(max_length=255, blank=True)
    certificate_file_url = models.URLField(blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    next_dose_date = models.DateField(null=True, blank=True)
    review_status = models.CharField(max_length=50)
    reviewed_by_doctor = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 19.6 FitnessDecision

```python
class FitnessDecision(models.Model):
    id = models.UUIDField(primary_key=True)
    assessment = models.OneToOneField("assessments.MedicalAssessment", on_delete=models.CASCADE)
    doctor = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    decision = models.CharField(max_length=80)
    reason = models.TextField(blank=True)
    return_to_work_date = models.DateField(null=True, blank=True)
    public_health_clearance_required = models.BooleanField(default=False)
    medical_report_url = models.URLField(blank=True)
    digitally_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

# 20. API Requirements

## 20.1 Assessment Lifecycle

```txt
POST   /api/assessments
GET    /api/assessments
GET    /api/assessments/:id
PATCH  /api/assessments/:id
POST   /api/assessments/:id/cancel
POST   /api/assessments/:id/close
GET    /api/assessments/:id/status
```

## 20.2 Food Handler Declaration

```txt
GET    /api/assessments/:id/declaration
POST   /api/assessments/:id/declaration
PATCH  /api/assessments/:id/declaration
POST   /api/assessments/:id/declaration/submit
POST   /api/assessments/:id/declaration/validate
POST   /api/assessments/:id/declaration/reopen
```

## 20.3 Physical Examination

```txt
GET    /api/assessments/:id/physical-exam
POST   /api/assessments/:id/physical-exam
PATCH  /api/assessments/:id/physical-exam
POST   /api/assessments/:id/physical-exam/complete
```

## 20.4 Lab Tests

```txt
GET    /api/assessments/:id/lab-tests
POST   /api/assessments/:id/lab-tests
GET    /api/lab-tests/:id
PATCH  /api/lab-tests/:id/sample-collected
PATCH  /api/lab-tests/:id/result
POST   /api/lab-tests/:id/upload-result
POST   /api/lab-tests/:id/submit-to-doctor
POST   /api/lab-tests/:id/review
POST   /api/lab-tests/:id/request-repeat
```

## 20.5 Vaccination Review

```txt
GET    /api/assessments/:id/vaccination-reviews
POST   /api/assessments/:id/vaccination-reviews
PATCH  /api/vaccination-reviews/:id
POST   /api/vaccination-reviews/:id/mark-valid
POST   /api/vaccination-reviews/:id/mark-missing
POST   /api/vaccination-reviews/:id/prescribe
POST   /api/vaccination-reviews/:id/administer
```

## 20.6 Fitness Decision

```txt
GET    /api/assessments/:id/fitness-decision
POST   /api/assessments/:id/fitness-decision
PATCH  /api/assessments/:id/fitness-decision
POST   /api/assessments/:id/fitness-decision/finalize
POST   /api/assessments/:id/submit-to-state
```

## 20.7 Assessment Reports

```txt
GET /api/assessments/:id/reports
GET /api/assessments/:id/reports/summary
GET /api/assessments/:id/reports/medical
GET /api/assessments/:id/reports/return-to-work
```

---

# 21. Frontend Routes

## 21.1 Food Handler Routes

```txt
/app/food-handler/assessment
/app/food-handler/assessment/:id
/app/food-handler/assessment/:id/declaration
/app/food-handler/assessment/:id/status
/app/food-handler/assessment/:id/vaccinations
/app/food-handler/assessment/:id/reports
```

## 21.2 Doctor Routes

```txt
/app/doctor/assessments
/app/doctor/assessments/:id
/app/doctor/assessments/:id/declaration
/app/doctor/assessments/:id/physical-exam
/app/doctor/assessments/:id/lab-results
/app/doctor/assessments/:id/vaccination-review
/app/doctor/assessments/:id/decision
```

## 21.3 Lab Staff Routes

```txt
/app/lab/requests
/app/lab/requests/:id
/app/lab/results
```

## 21.4 Facility Routes

```txt
/app/facility/assessments
/app/facility/assessments/:id
/app/facility/assessments/:id/submit-to-state
```

## 21.5 State Routes

```txt
/app/state/certificate-validation
/app/state/certificate-validation/:assessment_id
```

---

# 22. Core Frontend Components

- AssessmentStepper
- AssessmentStatusBadge
- AssessmentPrerequisiteChecklist
- HealthDeclarationForm
- DeclarationRiskFlag
- DoctorDeclarationReviewPanel
- PhysicalExamForm
- LabTestRequestForm
- LabTestStatusTable
- LabResultEntryForm
- LabResultReviewPanel
- VaccinationReviewPanel
- FitnessDecisionForm
- ReturnToWorkTriggerPanel
- SubmitToStatePanel
- AssessmentAuditTimeline
- MedicalPrivacyNotice
- EmployerSafeFitnessStatusBadge
- FoodHandlerAssessmentStatusCard

---

# 23. Permissions and Access Control

## 23.1 Food Handler

Can access only own assessments.

## 23.2 Employer

Can access only employer-safe operational statuses for linked food handlers.

## 23.3 Facility Admin

Can view facility assessment queue and administrative status.

## 23.4 Doctor

Can edit clinical workflow only for assigned/authorized assessments.

## 23.5 Lab Staff

Can edit only lab test workflow for facility/department.

## 23.6 State Ministry

Can view submitted assessment summaries for certificate validation.

## 23.7 Federal Ministry

Can view aggregate assessment analytics unless granted explicit individual-record access.

---

# 24. Acceptance Criteria

## 24.1 Assessment Creation

- Assessment can be created for a food handler.
- Assessment links to food handler, facility, state, payment, appointment, employer, and branch where applicable.
- Assessment cannot proceed if required prerequisites fail.

## 24.2 Declaration

- Food handler can complete declaration.
- Risk flags are generated.
- Doctor can validate declaration.
- Declaration locks after validation.
- Declaration changes require versioning.

## 24.3 Physical Examination

- Doctor can complete physical exam.
- Risk findings are flagged.
- Employer cannot see physical exam details.
- Physical exam completion is audit logged.

## 24.4 Lab Workflow

- Doctor can request lab tests.
- Lab staff can submit results.
- Doctor can review results.
- Positive/inconclusive results are flagged.
- Lab details are hidden from employers/public.

## 24.5 Vaccination Review

- Doctor can review typhoid and Hepatitis A status.
- System calculates due/expired status.
- Missing/expired vaccination can trigger required vaccination.
- Employer sees only compliance status.

## 24.6 Fitness Decision

- Doctor can submit decision only after required evidence is complete.
- Fit decision requires all backend checks.
- Temporarily not fit triggers operational restriction.
- Not fit blocks certificate submission.
- Fit decision can be submitted to State validation.

## 24.7 State Submission

- Assessment can be submitted to State only if fit and complete.
- State can request clarification.
- Facility can respond to clarification.
- State approval leads to certificate issuance by certificate module.

## 24.8 Privacy

- Employers cannot see lab results, doctor notes, diagnosis, declaration answers, or full NIN.
- Public users cannot see any medical assessment data.
- Sensitive access is audit logged.

---

# 25. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Medical Assessment Workflow Module for FoodCert NG.

The module must support assessment creation, prerequisite checks, health declaration, doctor declaration validation, physical examination, lab test request and result workflow, vaccination review, doctor fitness decision, return-to-work trigger, submission to State Ministry validation, assessment status engine, role-based privacy, audit logging, backend service-layer validation, and frontend workflow pages.

Important rules:
- Backend is the source of truth for assessment status.
- Assessment cannot proceed if NIN, payment, facility approval, or doctor authorization checks fail.
- Employers must only see operational fitness status, not medical details.
- Public users must not see assessment records.
- Doctor decisions require completed declaration, physical exam, lab review, and vaccination review.
- Fit assessments are submitted to State Ministry for certificate issuance.
- Facilities do not issue certificates directly.
- Temporarily not-fit decisions trigger return-to-work workflow.
- All sensitive medical access and workflow transitions must be audit logged.

Build backend models, serializers, permissions, services, endpoints, tests, and frontend pages for the module.
```

---

# 26. MVP Build Order

1. MedicalAssessment model and status engine
2. Assessment creation and prerequisite checks
3. Health declaration form and API
4. Declaration validation
5. Physical examination form and API
6. Lab test request workflow
7. Lab result submission workflow
8. Doctor lab result review
9. Vaccination review workflow
10. Fitness decision workflow
11. Return-to-work trigger
12. Submit to State validation
13. Role-safe serializers
14. Assessment audit logs
15. Frontend assessment stepper
16. Food handler assessment status page
17. Doctor assessment workflow pages
18. Lab staff workflow pages
19. Facility assessment queue
20. Permission and privacy tests
