# FoodCert NG Dynamic Assessment Forms Implementation Chunks

This roadmap breaks the Dynamic Assessment Forms & Verification Requirements Module into dependency-ordered implementation chunks. Each chunk should be implemented, tested, and committed before starting the next chunk.

## Chunk 1: Assessment Form Foundation

**Status:** Implemented and verified.

### Scope

- Add `AssessmentFormTemplate`.
- Add `AssessmentFormSection`.
- Add `AssessmentFormQuestion`.
- Support system, national, state, and facility ownership scopes.
- Add approved assessment field types.
- Add privacy classifications.
- Keep medical questionnaire fields separate from `FoodHandlerProfile`.

### Verification

- Run migrations.
- Add model tests.
- Add ownership-scope tests.
- Add permission tests for Federal, State, and facility users.

## Chunk 2: Builder and Template Lifecycle

**Status:** Implemented and verified.

### Scope

- Add template, section, and question APIs.
- Support draft, pending approval, approved, published, active, retired, rejected, and archived statuses.
- Add form preview.
- Add duplicate-as-new-version behavior.
- Prevent in-place edits to published templates.
- Preserve version history.

### Verification

- Add lifecycle transition tests.
- Add published-template immutability tests.
- Add duplicate-version tests.
- Verify builder API permissions.

## Chunk 3: Requirement Sets

**Status:** Implemented and verified.

### Scope

- Add `AssessmentRequirementSet`.
- Configure required forms, documents, lab tests, vaccinations, and approvals.
- Resolve requirements by assessment type, state, facility, food-handler category, employer category, illness status, and return-to-work status.
- Enforce precedence: national requirements override State requirements, and State requirements override facility supplements.
- Prevent lower scopes from weakening mandatory requirements.

### Verification

- Add requirement-resolution matrix tests.
- Add conflict-precedence tests.
- Add mandatory-requirement protection tests.

## Chunk 4: Response Engine

**Status:** Implemented and verified.

### Scope

- Add `AssessmentFormResponse`.
- Assign resolved forms when assessments are created.
- Support not started, draft, submitted, under review, clarification requested, reopened, resubmitted, validated, locked, superseded, and archived statuses.
- Store question snapshots and exact template versions.
- Lock submitted responses.
- Preserve previous response versions when forms are reopened.

### Verification

- Add draft and submission tests.
- Add locking tests.
- Add reopen and supersede tests.
- Add historical snapshot tests.

## Chunk 5: Validation, Logic, and Risk Flags

**Status:** Implemented and verified.

### Scope

- Expand backend validation for medical field types.
- Add conditional visibility rules.
- Add conditional-required rules.
- Validate conditional logic before publishing.
- Add risk flags such as medical review required, lab test required, vaccination required, temporary exclusion recommended, return-to-work required, public health clearance required, and State review required.
- Surface risk flags to doctors without automatically making clinical decisions.

### Verification

- Add field-validation tests.
- Add conditional-logic tests.
- Add invalid-publishing tests.
- Add risk-flag generation tests.

## Chunk 6: Facility Approval Workflow

**Status:** Implemented and verified.

### Scope

- Allow facilities to create supplementary intake forms.
- Add State approval, rejection, and change-request workflow.
- Prevent facility form publishing until approval where required.
- Ensure facility questions use approved field types and privacy classifications.
- Prevent facility forms from weakening national or State requirements.

### Verification

- Add approval workflow tests.
- Add rejection and resubmission tests.
- Add conflict and privacy-rule tests.

## Chunk 7: Workflow Screens

**Status:** Implemented and verified.

### Scope

- Add Federal national form library and requirement-set builder.
- Add State form management and facility approval queue.
- Add facility supplementary-form builder.
- Add food-handler assigned-questionnaire page.
- Add doctor response review and validation page.
- Add lab structured-result form page.
- Add assessment requirement-completion checklist.
- Reuse shared builder and renderer components.

### Verification

- Run frontend lint and type checks.
- Add role-based route smoke tests.
- Verify mobile and desktop layouts.
- Verify form previews and dynamic rendering.

## Chunk 8: Privacy, Audit, and Analytics

**Status:** Implemented and verified.

### Scope

- Hide medical responses from employers, inspectors, and public users.
- Expose only operational completion summaries to employers and inspectors.
- Audit sensitive-response access.
- Add form completion, overdue, risk-flag, usage, version, and clarification analytics.
- Add notifications for form assignment, reminders, submission, clarification, reopening, facility approval or rejection, and new-version publishing.

### Verification

- Add privacy regression tests.
- Add sensitive-access audit tests.
- Add aggregate-report tests.
- Verify notification triggers.

## Recommended Delivery Sequence

1. Implement one chunk.
2. Run focused backend tests.
3. Run migration consistency checks.
4. Run frontend lint and type checks when frontend code changes.
5. Smoke-test affected routes.
6. Commit the completed chunk.
7. Start the next chunk only after the previous chunk is stable.
