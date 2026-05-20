# PRD: Medical Facility Module — FoodCert NG

## 1. Module Name

**Medical Facility Module**

## 2. Product Context

The Medical Facility Module is a core operational module in **FoodCert NG**, the national platform for food handler medical fitness certification. It enables approved hospitals, clinics, diagnostic centres, primary healthcare centres, and mobile health units to participate in the food handler medical assessment process.

Medical facilities are responsible for conducting food handler assessments, managing doctors and lab staff, validating health declarations, conducting physical examinations, requesting and recording laboratory tests, reviewing vaccination status, generating medical reports, and submitting completed assessments to the State Ministry of Health for certificate validation and issuance.

The module must support both simple facilities and large multi-department facilities. A facility may have a Clinical Assessment Department, Laboratory Department, Medical Records Department, and Finance/Settlement Unit. This should be implemented using the `OrganizationUnit` model from the stakeholder management design.

---

# 3. Product Goal

To provide approved medical facilities with a secure, structured, and auditable workspace for managing food handler medical assessments from appointment to doctor decision, while ensuring that only accredited facilities can conduct assessments and receive settlements through the platform.

---

# 4. Core Objectives

The Medical Facility Module must allow facilities to:

1. Register as medical facilities.
2. Apply for State Ministry accreditation.
3. Create and manage facility departments.
4. Manage facility users, including doctors, lab staff, records staff, and finance staff.
5. Receive and manage food handler appointments.
6. Conduct health declaration review.
7. Conduct physical examinations.
8. Request and manage laboratory tests.
9. Record and review vaccination information.
10. Submit doctor fitness decisions.
11. Generate medical reports.
12. Submit completed assessments to the State Ministry for certificate validation.
13. Track assessment payments and facility settlements.
14. Manage annual re-accreditation.
15. Maintain facility performance reports and audit trails.

---

# 5. Medical Facility User Types

## 5.1 Medical Facility Admin

The facility administrator manages the facility account, accreditation, staff, departments, appointments, and facility-level reporting.

Can:

- Register facility profile.
- Submit accreditation application.
- Upload accreditation documents.
- Create facility departments.
- Invite doctors, lab staff, records staff, and finance users.
- View facility dashboard.
- View appointments.
- Assign doctors and lab staff.
- View assessment status.
- View facility performance.
- View settlements.
- Manage re-accreditation.

Cannot:

- Approve its own accreditation.
- Issue State Ministry certificate directly.
- Override State Ministry certificate validation.
- Edit issued certificates.

## 5.2 Doctor / Medical Practitioner

The doctor performs clinical assessment and makes the medical fitness decision.

Can:

- Review assigned food handler assessments.
- Validate health declarations.
- Conduct physical examination.
- Request lab tests.
- Review lab results.
- Review vaccination records.
- Prescribe vaccination where required.
- Make fitness decisions.
- Generate medical reports.
- Submit assessment for State validation.

Cannot:

- Approve facility accreditation.
- Process facility settlements.
- Change payment status.
- Issue certificates directly under State authority.
- Access unrelated facility assessments.

## 5.3 Laboratory Staff

Lab staff handle test requests and results.

Can:

- View lab test requests.
- Mark sample collection.
- Enter lab results.
- Upload lab result documents.
- Mark test status.
- Submit results to doctor.

Cannot:

- Make medical fitness decisions.
- Issue certificates.
- Approve assessment completion.
- View unrelated clinical notes unless authorized.

## 5.4 Medical Records Staff

Medical records staff manage documentation and completed records.

Can:

- View completed assessments.
- Confirm document completeness.
- Upload records where permitted.
- Manage patient/assessment file references.
- Support certificate/report generation workflow.
- Maintain assessment record archives.

Cannot:

- Change doctor decisions.
- Enter lab results.
- Approve certificates.
- Access finance settings unless permitted.

## 5.5 Facility Finance / Settlement User

Finance users monitor payments and settlements.

Can:

- View assessment payment summaries.
- View pending settlements.
- View settled payments.
- Download settlement reports.
- Raise settlement disputes.

Cannot:

- View detailed medical records.
- Change medical assessment data.
- Approve fitness decisions.

## 5.6 Facility Viewer

Read-only facility user.

Can:

- View assigned dashboards and reports.
- View non-sensitive facility operations.

Cannot:

- Edit assessments.
- Submit decisions.
- Upload results.
- Manage staff.
- Manage finance.

---

# 6. Module Scope

## 6.1 In Scope

The Medical Facility Module includes:

- Facility registration
- Facility profile management
- Accreditation application
- Accreditation status tracking
- Re-accreditation workflow
- Department/unit management
- Facility staff invitations
- Doctor onboarding
- Lab staff onboarding
- Appointment management
- Assessment queue management
- Health declaration review
- Physical examination workflow
- Lab test request and result workflow
- Vaccination review
- Doctor fitness decision
- Medical report generation
- Submission to State Ministry validation queue
- Facility dashboard
- Facility reports
- Facility settlements dashboard
- Audit logs

## 6.2 Out of Scope for MVP

The following may be deferred:

- Full EMR replacement
- Direct integration with laboratory machines
- Complex hospital billing
- Insurance/HMO workflows
- Pharmacy inventory management
- Advanced clinical decision support
- Telemedicine consultation
- Offline facility workflow
- Multi-country facility management

---

# 7. Facility Registration Workflow

## 7.1 Workflow Summary

```txt
Facility creates account
→ Completes facility profile
→ Submits accreditation application
→ Uploads supporting documents
→ State Ministry reviews
→ State approves/rejects
→ Approved facility becomes available for food handler appointments
→ Facility creates departments and invites staff
```

## 7.2 Facility Account Creation

Required fields:

- Facility contact name
- Email
- Phone number
- Password
- Confirm password

Validation:

- Email must be unique.
- Phone number should be verified.
- Facility contact must accept terms.

## 7.3 Facility Profile Fields

Required fields:

- Facility name
- Facility type
- Ownership type: public/private
- Facility registration/license number
- Address
- State
- LGA
- Ward, optional
- Contact person
- Contact phone
- Contact email
- Facility operating hours
- Facility service capacity
- Bank/settlement details, if required at registration stage

Facility types:

- Hospital
- Clinic
- Diagnostic centre
- Primary healthcare centre
- Mobile health unit
- Other

## 7.4 Facility Statuses

- Draft
- Profile Submitted
- Accreditation Pending
- Under Review
- More Information Required
- Approved
- Rejected
- Suspended
- Expired
- Re-accreditation Due
- Inactive

---

# 8. Facility Accreditation Workflow

## 8.1 Purpose

Only pre-qualified and State-approved medical facilities should be allowed to conduct food handler medical assessments.

## 8.2 Accreditation Application Sections

The accreditation application should include:

1. Facility profile
2. Licensing and registration
3. Clinical staff capacity
4. Laboratory capacity
5. Medical records capacity
6. Internet and digital infrastructure
7. Documentation policy
8. QR/certificate handling readiness
9. Facility equipment and readiness
10. Supporting document upload
11. Declaration and submission

## 8.3 Accreditation Checklist

The facility should indicate and upload evidence for:

- Valid facility license
- Written reporting and documentation policy
- Computers in medical records unit
- Computer operators in medical records unit
- Standard health declaration forms
- Laboratory request forms
- Patient file system
- Internet access
- Trained clinical staff
- Trained lab staff
- Trained medical records staff
- Ability to manage QR-enabled certificate workflow
- Data protection and confidentiality procedures
- Basic infection prevention and control readiness
- Laboratory capacity for required food handler tests
- Valid doctor credentials
- Valid laboratory staff credentials

## 8.4 Accreditation Document Uploads

Possible documents:

- Facility license
- Corporate registration document, where applicable
- Medical director credential
- Doctor licenses
- Lab scientist/technician credentials
- Laboratory license/accreditation, where applicable
- Documentation policy
- Data protection/confidentiality policy
- Facility photos
- Equipment list
- Proof of internet/digital readiness
- Bank details for settlement
- Any State Ministry required forms

## 8.5 Accreditation Review Flow

```txt
Facility submits application
→ State Accreditation Unit reviews
→ Reviewer checks checklist and documents
→ Reviewer approves, rejects, or requests more information
→ Facility responds if more information is requested
→ Approved facility becomes active and bookable
```

## 8.6 Accreditation Statuses

- Draft
- Submitted
- Under Review
- More Information Required
- Approved
- Rejected
- Suspended
- Expired
- Re-accreditation Due

## 8.7 Accreditation Rules

- Facility cannot receive appointments until approved.
- Facility cannot conduct assessments if suspended or expired.
- Facility accreditation is state-specific.
- Re-accreditation should occur annually.
- Accreditation approval must be audit logged.
- Suspended facilities should not be selectable by food handlers.
- Expired facilities should be blocked from new assessments.

---

# 9. Re-Accreditation Workflow

## 9.1 Purpose

Approved medical facilities must be re-accredited periodically, with the default being yearly.

## 9.2 Re-Accreditation Alerts

The system should notify facility and State Ministry:

- 60 days before expiry
- 30 days before expiry
- 7 days before expiry
- On expiry date

## 9.3 Re-Accreditation Flow

```txt
Facility receives re-accreditation notice
→ Facility reviews existing profile
→ Facility updates documents and checklist
→ Facility submits renewal
→ State Ministry reviews
→ Accreditation renewed, rejected, or suspended
```

## 9.4 Re-Accreditation Rules

- Facility can continue operations during renewal review only if policy permits.
- If accreditation expires, new assessment booking is blocked.
- Existing assessments may be allowed to complete depending on state policy.
- Renewal decision must create audit log.

---

# 10. Facility Department Management

## 10.1 Purpose

Facilities may have internal departments responsible for different parts of the assessment process. These should be modeled as `OrganizationUnit` records.

## 10.2 Department Types

- Clinical Assessment Department
- Laboratory Department
- Medical Records Department
- Finance/Settlement Unit
- Administration Unit
- Other

## 10.3 Department Management Features

Facility admin can:

- Create department
- Edit department
- Deactivate department
- Assign staff to department
- View department workload
- View department performance
- Route tasks to department

## 10.4 Department-Specific Workflows

### Clinical Assessment Department

Handles:

- Declaration review
- Physical examination
- Lab request initiation
- Vaccination review
- Fitness decision

### Laboratory Department

Handles:

- Lab test requests
- Sample collection
- Result entry
- Result upload
- Repeat test handling

### Medical Records Department

Handles:

- Patient file references
- Assessment documentation
- Completed records
- Certificate/report documentation
- Record archiving

### Finance/Settlement Unit

Handles:

- Payment reports
- Pending settlements
- Paid settlements
- Failed settlement follow-up
- Settlement disputes

## 10.5 Department Scoping Rules

- Doctors assigned to clinical department see clinical assessment tasks.
- Lab staff assigned to lab department see lab requests and results.
- Records staff assigned to records department see completed record workflows.
- Finance users assigned to finance unit see settlements and payment reports.
- Facility admin can view all departments.

---

# 11. Facility Staff Management

## 11.1 Purpose

Facility admins must invite and manage users within the facility.

## 11.2 Staff Roles

- Facility Admin
- Doctor
- Lab Staff
- Medical Records Staff
- Finance/Settlement User
- Viewer

## 11.3 Invite Staff Flow

```txt
Facility admin opens staff page
→ Clicks invite user
→ Enters email/phone, role, department, message
→ System sends invite
→ Staff accepts invite
→ Staff is assigned to facility organization, role, and department
```

## 11.4 Invite Fields

- Email
- Phone, optional
- Role
- Department/unit
- Professional registration number, where applicable
- Message
- Expiry date, default 7 days

## 11.5 Staff List Columns

- Name
- Role
- Department
- Professional registration number
- Status
- Last login
- Actions

## 11.6 Staff Actions

- Invite staff
- Resend invite
- Revoke invite
- Assign department
- Suspend user
- Reactivate user
- Update role
- View activity log

## 11.7 Doctor Profile Requirements

Doctor profile should capture:

- Full name
- Phone
- Email
- Medical license/registration number
- Specialty, optional
- Facility assignment
- Department
- Digital signature profile
- Status

## 11.8 Lab Staff Profile Requirements

Lab staff profile should capture:

- Full name
- Phone
- Email
- Professional registration number, where applicable
- Department
- Status

---

# 12. Appointment Management

## 12.1 Purpose

Approved facilities should manage food handler assessment appointments.

## 12.2 Appointment Sources

Appointments may be created by:

- Food handler
- Employer on behalf of food handler
- Facility admin
- State-directed scheduling, future

## 12.3 Appointment List Columns

- Appointment date/time
- Food handler name
- Employer
- Branch
- Payment status
- Declaration status
- Assigned doctor
- Assessment status
- Appointment status
- Actions

## 12.4 Appointment Statuses

- Pending
- Confirmed
- Rescheduled
- Cancelled
- Completed
- No-show

## 12.5 Appointment Actions

Facility users can:

- Confirm appointment
- Reschedule appointment
- Cancel appointment
- Mark no-show
- Assign doctor
- Start assessment
- View payment confirmation
- View declaration status

## 12.6 Appointment Rules

- Appointment should only be confirmed after payment is successful, unless policy allows otherwise.
- Appointment should only be created for an approved facility.
- Suspended/expired facilities cannot accept new appointments.
- Food handler should complete declaration before assessment, where possible.
- Appointment changes should notify the food handler and employer, where linked.

---

# 13. Assessment Queue Management

## 13.1 Purpose

The facility needs a central queue showing all food handler assessments and their current status.

## 13.2 Assessment Queue Columns

- Assessment ID
- Food handler
- Employer
- Branch
- Appointment date
- Payment status
- Declaration status
- Physical exam status
- Lab status
- Vaccination status
- Doctor decision
- Submission status
- Assigned doctor
- Last updated
- Actions

## 13.3 Assessment Statuses

- Payment Confirmed
- Appointment Booked
- Declaration Submitted
- Declaration Validated
- Physical Exam Pending
- Physical Exam Completed
- Lab Tests Pending
- Lab Results Submitted
- Lab Results Reviewed
- Vaccination Review Pending
- Doctor Decision Pending
- Temporarily Not Fit
- Fit
- Not Fit
- Submitted for State Validation
- Certificate Issued
- Closed

## 13.4 Queue Filters

- Date range
- Doctor
- Lab status
- Decision status
- Employer
- Branch
- Payment status
- Certificate submission status
- Assessment status

---

# 14. Health Declaration Review

## 14.1 Purpose

The doctor must validate the food handler's health declaration before or during assessment.

## 14.2 Declaration Review Screen

Doctor should see:

- Food handler profile summary
- Declaration answers
- Risk flags
- Submission timestamp
- Linked employer and branch
- Prior assessment history, where authorized

## 14.3 Declaration Actions

Doctor can:

- Validate declaration
- Request clarification
- Mark risk flag
- Continue to physical examination

## 14.4 Declaration Rules

- Declaration should be locked after doctor validation.
- If changes are required, create a new declaration version.
- Risky answers should not automatically disqualify a food handler but should require doctor attention.
- Declaration validation must be audit logged.

---

# 15. Physical Examination Workflow

## 15.1 Purpose

Doctors conduct and document physical examinations for food handlers.

## 15.2 Physical Exam Checklist

Doctor records Yes/No or relevant notes for:

- Fever
- Jaundice
- Skin infection on hands, arms, or face
- Boils, styes, or sepsis on finger
- Discharge from eye, ear, nose, gums, or mouth
- Diarrhoea
- Vomiting
- Sore throat with fever
- Cough or flu
- Known history of typhoid carrier
- Other relevant clinical observations

## 15.3 Physical Exam Actions

Doctor can:

- Save draft
- Complete exam
- Request lab tests
- Recommend vaccination
- Mark temporary exclusion
- Proceed to decision when all requirements are complete

## 15.4 Physical Exam Rules

- Only authorized doctors can complete the physical exam.
- Doctor notes are sensitive and should not be visible to employers/public.
- Physical exam completion must be audit logged.
- Positive symptoms may trigger additional lab tests, temporary exclusion, or return-to-work workflow.

---

# 16. Laboratory Test Workflow

## 16.1 Purpose

The facility must manage required and additional lab tests for food handler assessment.

## 16.2 Required Tests

System should support:

- Stool microscopy
- Stool culture and sensitivity
- Hepatitis A antigen

## 16.3 Optional Tests

Doctor may request:

- Typhoid-specific test
- Cholera test
- Other foodborne disease test
- Other clinically indicated test

## 16.4 Lab Request Flow

```txt
Doctor requests lab test
→ Lab department receives request
→ Lab staff marks sample collected
→ Lab staff enters result
→ Lab staff uploads result document
→ Doctor reviews result
→ Assessment status updates
```

## 16.5 Lab Test Statuses

- Requested
- Sample Collected
- In Progress
- Result Uploaded
- Positive
- Negative
- Inconclusive
- Repeat Required
- Submitted to Doctor
- Reviewed by Doctor

## 16.6 Lab Result Fields

- Test type
- Sample collected date/time
- Result status
- Result summary
- Result document upload
- Lab staff notes
- Submitted by
- Reviewed by doctor
- Review date

## 16.7 Lab Workflow Rules

- Lab staff cannot issue fitness decision.
- Positive results must be flagged for doctor review.
- Inconclusive results should allow repeat test request.
- Lab result submission must be audit logged.
- Employers should not see detailed lab results.

---

# 17. Vaccination Review Workflow

## 17.1 Purpose

Facilities must review and record food handler vaccination status for required vaccines.

## 17.2 Vaccines

- Typhoid
- Hepatitis A
- Other vaccines as required by policy

## 17.3 Vaccination Review Screen

Doctor or authorized facility user should see:

- Existing vaccination records
- Uploaded certificates
- Date of vaccination
- Brand name
- Batch number
- Vaccinator
- Facility where vaccine was administered
- Expiry date
- Next visit date
- Verification status

## 17.4 Vaccination Actions

Doctor can:

- Mark record valid
- Mark record missing
- Mark record expired
- Prescribe vaccination
- Record administered vaccination
- Set next dose date
- Continue assessment

## 17.5 Vaccination Rules

- Typhoid vaccine validity defaults to 3 years.
- Hepatitis A requires two doses at 0 and 6 months.
- If required vaccine is missing or expired, doctor should prescribe or administer vaccine.
- Vaccination record changes must be audit logged.
- Employers see only vaccination compliance status, not clinical notes.

---

# 18. Doctor Fitness Decision Workflow

## 18.1 Purpose

The doctor makes the clinical/medical fitness decision after reviewing declaration, physical exam, lab results, and vaccination status.

## 18.2 Decision Options

- Fit to Work
- Temporarily Not Fit
- Not Fit
- Requires Vaccination
- Requires Lab Test
- Requires Re-Examination
- Requires Treatment
- Requires Public Health Clearance
- Return to Work on Specific Date

## 18.3 Decision Requirements

Before a `Fit to Work` decision, the system should check:

- Payment confirmed
- NIN verified or override approved
- Facility approved
- Doctor authorized
- Declaration validated
- Physical exam completed
- Required lab results reviewed
- Vaccination status reviewed
- No unresolved exclusion or illness issue
- Doctor digital sign-off completed

## 18.4 Decision Actions

Doctor can:

- Save decision draft
- Submit final decision
- Generate medical report
- Submit assessment to State validation
- Set return-to-work date, if applicable
- Request further review

## 18.5 Decision Rules

- Decision must be digitally signed by doctor.
- Decision must be immutable after submission except through formal correction workflow.
- Employers see only operational fitness category.
- Fit decisions go to State Ministry validation queue.
- Not-fit decisions generate medical report, not certificate.
- Temporarily not-fit decisions may trigger return-to-work workflow.

---

# 19. Medical Report Generation

## 19.1 Report Types

The facility should generate:

- Medical Examination Report
- Temporarily Not Fit Report
- Return-to-Work Report
- Vaccination Record
- Lab Summary Report, restricted
- Assessment Completion Summary

## 19.2 Medical Report Fields

- Food handler name
- Food handler ID
- Facility
- Doctor
- Assessment date
- Declaration validation status
- Physical examination summary
- Lab summary, restricted
- Vaccination review summary
- Doctor decision
- Return-to-work date, where applicable
- Doctor signature
- Facility stamp/digital authorization

## 19.3 Report Access

- Doctor: full report
- Facility Admin: operational and administrative report
- Medical Records Staff: documentation report
- State Ministry: assessment summary and required evidence
- Employer: operational status only
- Food Handler: certificate/report appropriate to their status
- Public: no medical report access

---

# 20. Submission to State Ministry

## 20.1 Purpose

Completed fit assessments must be submitted to the State Ministry for validation and certificate issuance.

## 20.2 Submission Requirements

Before submission:

- Doctor decision is final.
- Required assessment sections are complete.
- Lab results reviewed.
- Vaccination review complete.
- Payment confirmed.
- Facility accreditation active.
- Doctor authorized.
- Medical report generated.

## 20.3 Submission Flow

```txt
Doctor submits final decision
→ Facility assessment marked complete
→ Facility submits to State validation queue
→ State Verification Desk reviews
→ State approves/rejects/requests clarification
→ Certificate issued if approved
```

## 20.4 Clarification Workflow

If State Ministry requests clarification:

- Facility receives notification.
- Facility sees clarification request.
- Doctor or facility admin responds.
- Facility resubmits assessment.
- State continues review.

## 20.5 Submission Statuses

- Not Submitted
- Ready for Submission
- Submitted to State
- Clarification Requested
- Clarification Responded
- Approved by State
- Rejected by State
- Certificate Issued

---

# 21. Facility Settlement and Finance Workflow

## 21.1 Purpose

Facilities should receive payment settlements through the platform after completing valid assessments.

## 21.2 Settlement Eligibility

Facility settlement should become eligible after:

- Food handler payment is confirmed.
- Assessment is completed.
- Doctor decision submitted.
- State validation completed.
- Certificate issued or report finalized, depending on settlement policy.

## 21.3 Settlement Dashboard

Show:

- Total paid assessments
- Completed assessments
- Pending settlements
- Processing settlements
- Paid settlements
- Failed settlements
- Gross amount
- Facility amount
- State amount
- Platform amount
- Refunds
- Settlement disputes

## 21.4 Settlement Table Columns

- Settlement reference
- Assessment ID
- Food handler
- Payment date
- Assessment completion date
- Gross amount
- Facility amount
- Status
- Settlement date
- Actions

## 21.5 Settlement Actions

Facility finance user can:

- View settlement details
- Download settlement report
- Raise dispute
- View payment receipt
- Export reconciliation report

## 21.6 Finance Privacy

Finance users should not see:

- Lab results
- Diagnosis
- Doctor notes
- Declaration answers

---

# 22. Facility Dashboard

## 22.1 Dashboard Cards

Show:

- Accreditation status
- Re-accreditation due date
- Appointments today
- Pending appointments
- Assessments in progress
- Lab requests pending
- Lab results pending doctor review
- Vaccination reviews pending
- Doctor decisions pending
- Submitted to State
- Certificates issued
- Not-fit reports
- Pending settlements
- Settled amount

## 22.2 Dashboard Charts

Suggested charts:

- Assessment volume over time
- Assessment status distribution
- Lab turnaround time
- Doctor decision distribution
- Certificate approval rate
- State clarification requests
- Settlement trend
- Department workload

## 22.3 Dashboard Filters

- Date range
- Department
- Doctor
- Lab status
- Assessment status
- Payment status
- Employer
- Food handler category

---

# 23. Facility Reports

## 23.1 Report Types

Facilities should generate:

- Assessment volume report
- Appointment report
- Lab test report
- Doctor decision report
- Certificate submission report
- State clarification report
- Settlement report
- Department workload report
- Re-accreditation readiness report

## 23.2 Export Formats

- PDF
- Excel
- CSV

## 23.3 Report Privacy

Reports must respect user role:

- Finance reports exclude medical details.
- Lab reports restricted to lab/doctor/admin users.
- Clinical reports restricted to doctors and authorized facility users.
- Employer-safe reports should not contain medical details.

---

# 24. Notifications

## 24.1 Facility Notifications

Notify facility when:

- Accreditation application is submitted
- Accreditation approved/rejected
- More information is requested
- Re-accreditation is due
- New appointment booked
- Appointment cancelled/rescheduled
- Declaration submitted
- Lab test requested
- Lab result submitted
- Doctor decision pending
- State requests clarification
- Certificate issued
- Settlement processed
- Settlement failed

## 24.2 Doctor Notifications

Notify doctor when:

- New assessment assigned
- Declaration pending review
- Lab result ready
- Vaccination review pending
- State requests clarification
- Return-to-work review assigned

## 24.3 Lab Staff Notifications

Notify lab staff when:

- New lab request assigned
- Sample collection overdue
- Result upload pending
- Repeat test requested

## 24.4 Finance Notifications

Notify finance users when:

- Settlement eligible
- Settlement paid
- Settlement failed
- Refund processed
- Dispute response available

---

# 25. Data Model Requirements

## 25.1 MedicalFacility

```python
class MedicalFacility(models.Model):
    id = models.UUIDField(primary_key=True)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    facility_name = models.CharField(max_length=255)
    facility_type = models.CharField(max_length=100)
    ownership_type = models.CharField(max_length=50)
    license_number = models.CharField(max_length=100)
    address = models.TextField()
    state = models.ForeignKey("geography.State", on_delete=models.SET_NULL, null=True)
    lga = models.ForeignKey("geography.LGA", on_delete=models.SET_NULL, null=True)
    ward = models.CharField(max_length=100, blank=True)
    contact_person_name = models.CharField(max_length=255)
    contact_person_phone = models.CharField(max_length=50)
    contact_person_email = models.EmailField(blank=True)
    accreditation_status = models.CharField(max_length=50)
    accreditation_start_date = models.DateField(null=True, blank=True)
    accreditation_expiry_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    standard_assessment_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 25.2 FacilityAccreditationApplication

```python
class FacilityAccreditationApplication(models.Model):
    id = models.UUIDField(primary_key=True)
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    has_reporting_policy = models.BooleanField(default=False)
    has_medical_records_computers = models.BooleanField(default=False)
    has_computer_operators = models.BooleanField(default=False)
    has_standard_forms = models.BooleanField(default=False)
    has_patient_files = models.BooleanField(default=False)
    has_qr_certificate_capability = models.BooleanField(default=False)
    has_internet_access = models.BooleanField(default=False)
    has_trained_records_staff = models.BooleanField(default=False)
    has_trained_clinical_staff = models.BooleanField(default=False)
    has_trained_lab_staff = models.BooleanField(default=False)
    reviewer = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    review_comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 25.3 FacilityDocument

```python
class FacilityDocument(models.Model):
    id = models.UUIDField(primary_key=True)
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.CASCADE)
    accreditation_application = models.ForeignKey("facilities.FacilityAccreditationApplication", null=True, blank=True, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=100)
    file_url = models.URLField()
    uploaded_by = models.ForeignKey("accounts.User", null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 25.4 FacilityStaffProfile

```python
class FacilityStaffProfile(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.CASCADE)
    department = models.ForeignKey("organizations.OrganizationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    staff_type = models.CharField(max_length=50)
    professional_registration_number = models.CharField(max_length=100, blank=True)
    digital_signature_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 25.5 FacilityClarificationRequest

```python
class FacilityClarificationRequest(models.Model):
    id = models.UUIDField(primary_key=True)
    facility = models.ForeignKey("facilities.MedicalFacility", on_delete=models.CASCADE)
    assessment = models.ForeignKey("assessments.MedicalAssessment", null=True, blank=True, on_delete=models.CASCADE)
    accreditation_application = models.ForeignKey("facilities.FacilityAccreditationApplication", null=True, blank=True, on_delete=models.CASCADE)
    requested_by = models.ForeignKey("accounts.User", related_name="facility_clarifications_requested", on_delete=models.SET_NULL, null=True)
    responded_by = models.ForeignKey("accounts.User", related_name="facility_clarifications_responded", on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    response = models.TextField(blank=True)
    status = models.CharField(max_length=50)
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
```

---

# 26. API Requirements

## 26.1 Facility Profile

```txt
POST   /api/facilities
GET    /api/facilities/me
GET    /api/facilities/:id
PATCH  /api/facilities/:id
```

## 26.2 Accreditation

```txt
POST   /api/facilities/:id/accreditation
GET    /api/facilities/:id/accreditation
PATCH  /api/facilities/:id/accreditation
POST   /api/facilities/:id/accreditation/submit
POST   /api/facilities/:id/accreditation/documents
GET    /api/facilities/:id/accreditation/documents
POST   /api/facilities/:id/re-accreditation
```

## 26.3 Departments

```txt
GET    /api/facilities/:id/departments
POST   /api/facilities/:id/departments
GET    /api/facilities/:id/departments/:department_id
PATCH  /api/facilities/:id/departments/:department_id
DELETE /api/facilities/:id/departments/:department_id
```

## 26.4 Staff

```txt
GET    /api/facilities/:id/staff
POST   /api/facilities/:id/invites
GET    /api/facilities/:id/invites
DELETE /api/facilities/:id/invites/:invite_id
PATCH  /api/facilities/:id/staff/:user_id/department
PATCH  /api/facilities/:id/staff/:user_id/suspend
PATCH  /api/facilities/:id/staff/:user_id/reactivate
```

## 26.5 Appointments

```txt
GET    /api/facilities/:id/appointments
PATCH  /api/facilities/:id/appointments/:appointment_id/confirm
PATCH  /api/facilities/:id/appointments/:appointment_id/reschedule
PATCH  /api/facilities/:id/appointments/:appointment_id/cancel
PATCH  /api/facilities/:id/appointments/:appointment_id/no-show
PATCH  /api/facilities/:id/appointments/:appointment_id/assign-doctor
```

## 26.6 Assessments

```txt
GET    /api/facilities/:id/assessments
GET    /api/facilities/:id/assessments/:assessment_id
PATCH  /api/facilities/:id/assessments/:assessment_id/assign-doctor
POST   /api/facilities/:id/assessments/:assessment_id/submit-to-state
```

## 26.7 Doctor Workflow

```txt
GET    /api/doctor/assessments
GET    /api/doctor/assessments/:assessment_id
PATCH  /api/doctor/assessments/:assessment_id/declaration/validate
POST   /api/doctor/assessments/:assessment_id/physical-exam
POST   /api/doctor/assessments/:assessment_id/lab-tests
PATCH  /api/doctor/assessments/:assessment_id/vaccination-review
PATCH  /api/doctor/assessments/:assessment_id/decision
```

## 26.8 Lab Workflow

```txt
GET    /api/lab/requests
GET    /api/lab/requests/:lab_test_id
PATCH  /api/lab/requests/:lab_test_id/sample-collected
PATCH  /api/lab/requests/:lab_test_id/result
POST   /api/lab/requests/:lab_test_id/upload-result
```

## 26.9 Settlements

```txt
GET /api/facilities/:id/settlements
GET /api/facilities/:id/settlements/:settlement_id
GET /api/facilities/:id/reports/settlements
POST /api/facilities/:id/settlements/:settlement_id/dispute
```

## 26.10 Facility Reports

```txt
GET /api/facilities/:id/dashboard
GET /api/facilities/:id/reports/assessments
GET /api/facilities/:id/reports/lab-tests
GET /api/facilities/:id/reports/doctor-decisions
GET /api/facilities/:id/reports/submissions
GET /api/facilities/:id/reports/departments
```

---

# 27. Frontend Routes

```txt
/app/facility/dashboard
/app/facility/profile
/app/facility/accreditation
/app/facility/re-accreditation
/app/facility/departments
/app/facility/departments/[id]
/app/facility/staff
/app/facility/invites
/app/facility/appointments
/app/facility/appointments/[id]
/app/facility/assessments
/app/facility/assessments/[id]
/app/facility/lab-requests
/app/facility/lab-requests/[id]
/app/facility/settlements
/app/facility/settlements/[id]
/app/facility/reports
/app/facility/settings

/app/doctor/dashboard
/app/doctor/assessments
/app/doctor/assessments/[id]
/app/doctor/return-to-work

/app/lab/dashboard
/app/lab/requests
/app/lab/requests/[id]
/app/lab/results
```

---

# 28. Core Frontend Components

- FacilityDashboardCards
- AccreditationStatusBadge
- AccreditationChecklistForm
- FacilityDocumentUpload
- DepartmentManagementTable
- DepartmentWorkloadCard
- FacilityStaffTable
- InviteFacilityStaffModal
- AppointmentCalendar
- AppointmentTable
- AssessmentQueueTable
- AssessmentStepper
- DeclarationReviewPanel
- PhysicalExamForm
- LabRequestForm
- LabResultEntryForm
- VaccinationReviewPanel
- FitnessDecisionPanel
- MedicalReportPreview
- StateSubmissionPanel
- SettlementDashboardCards
- SettlementTable
- FacilityReportBuilder

---

# 29. Permissions and Access Control

## 29.1 Facility Admin

Can:

- Manage facility profile
- Submit accreditation
- Manage departments
- Invite staff
- View all facility assessments
- Assign doctors
- View facility reports
- View settlements

## 29.2 Doctor

Can:

- View assigned assessments
- Validate declarations
- Conduct physical exams
- Request lab tests
- Review lab results
- Review vaccinations
- Submit fitness decisions

## 29.3 Lab Staff

Can:

- View lab requests assigned to facility/department
- Mark sample collection
- Enter results
- Upload lab documents
- Submit results to doctor

## 29.4 Records Staff

Can:

- View completed assessment records
- Manage assessment documentation
- Support medical report archiving

## 29.5 Finance User

Can:

- View facility payment and settlement reports
- Download reconciliation reports
- Raise settlement disputes

## 29.6 Facility Viewer

Can:

- View permitted dashboards/reports
- Cannot edit workflow records

---

# 30. Privacy Requirements

The module handles sensitive medical information.

Rules:

- Employers must not see lab results, doctor notes, diagnosis, or declaration answers.
- Public verifiers must not see any medical record.
- Finance users must not see medical details.
- Lab staff should only see lab-related information.
- Medical records access must be logged.
- Doctor notes must be restricted.
- Full NIN must be masked unless the user is authorized.
- All report exports must respect role-based privacy.

---

# 31. Audit Logs

Create audit logs for:

- Facility registration
- Accreditation application submission
- Document upload
- Accreditation approval/rejection by State
- Facility suspension/reinstatement
- Re-accreditation submission
- Department creation/update/deactivation
- Staff invite sent/accepted/revoked
- Appointment confirmation/reschedule/cancellation
- Doctor assignment
- Declaration validation
- Physical exam completion
- Lab test request
- Lab result submission
- Vaccination review
- Doctor fitness decision
- Assessment submission to State
- State clarification response
- Settlement dispute
- Sensitive medical record access

---

# 32. Acceptance Criteria

## Facility Registration and Accreditation

- Facility can register and create a profile.
- Facility can submit accreditation application.
- Facility can upload required documents.
- State Ministry can approve/reject/request clarification.
- Only approved facilities can receive appointments.
- Suspended/expired facilities cannot conduct new assessments.
- Facility can apply for re-accreditation.

## Department and Staff Management

- Facility can create departments.
- Facility can assign staff to departments.
- Facility can invite doctors, lab staff, records staff, and finance users.
- Department-scoped users see relevant workflows.
- Facility admin can view all departments.

## Appointment Management

- Facility can view appointments.
- Facility can confirm/reschedule/cancel appointments.
- Facility can assign doctors.
- Appointment cannot proceed if payment is not confirmed, unless policy allows.
- Facility cannot accept appointments if accreditation is inactive.

## Medical Workflow

- Doctor can validate declaration.
- Doctor can complete physical exam.
- Doctor can request lab tests.
- Lab staff can enter/upload results.
- Doctor can review lab results.
- Doctor can review vaccination status.
- Doctor can submit final decision.
- Fit decision can be submitted to State validation.

## Certificate Submission

- Facility can submit completed fit assessment to State Ministry.
- State can request clarification.
- Facility can respond to clarification.
- Certificate is issued by State, not directly by facility.

## Settlement

- Facility can view pending and paid settlements.
- Facility settlement is linked to completed and validated assessments.
- Facility can download settlement reports.
- Facility can raise settlement dispute.

## Privacy

- Employers cannot see facility clinical details.
- Public users cannot see medical records.
- Finance users cannot see diagnosis/lab details.
- Medical access is audit logged.

---

# 33. Codex Implementation Instructions

Use this prompt for Codex:

```txt
Implement the Medical Facility Module for FoodCert NG.

The module must support facility registration, facility profile management, State Ministry accreditation application, document upload, annual re-accreditation, department management using OrganizationUnit, staff invites, doctor onboarding, lab staff onboarding, appointment management, assessment queue management, declaration review, physical examination, lab test workflow, vaccination review, doctor fitness decision, medical report generation, submission to State Ministry for certificate validation, facility settlement dashboard, reports, permissions, privacy controls, and audit logs.

Important rules:
- Only State-approved facilities can conduct food handler assessments.
- Suspended or expired facilities cannot accept new appointments.
- Facilities do not issue certificates directly; certificates are issued by the State Ministry after validation.
- Doctors make medical fitness decisions but State Ministry validates certificate issuance.
- Lab staff cannot make fitness decisions.
- Employers and public verifiers must not see detailed medical records.
- Department scoping should use OrganizationUnit.
- Facility settlements should only become eligible after payment confirmation, completed assessment, and State validation according to settlement policy.
- All sensitive medical record access and workflow actions must be audit logged.

Build backend models, serializers, permissions, services, endpoints, tests, and frontend pages for the module.
```

---

# 34. MVP Build Order

1. MedicalFacility model and profile API
2. Facility registration page
3. Accreditation application workflow
4. Facility document upload
5. State accreditation status integration
6. Department management using OrganizationUnit
7. Facility staff invite workflow
8. Appointment management
9. Assessment queue
10. Doctor declaration review
11. Doctor physical exam form
12. Lab request and result workflow
13. Vaccination review
14. Fitness decision workflow
15. Submit to State validation
16. Facility dashboard
17. Settlement dashboard
18. Facility reports
19. Facility privacy tests
20. Facility permission tests

