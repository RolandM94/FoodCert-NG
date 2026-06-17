# **Indicators Feature – Product Requirements Document**

## **1. Introduction**

### **1.1 Purpose**

The **Indicators Feature** in Stigdata will allow organizations to
define and track the metrics, whether **quantitative** or
**qualitative**, that measure progress toward project goals and
outcomes. By integrating with other modules, such as
**Logframes/Plans**, **Activities**, and **Documents/Reports**, this
feature will provide a centralized system for data-driven
decision-making, accountability, and real-time performance monitoring.

### **1.2 Scope**

- **What’s Included**:

  - Creation, configuration, and management of indicators (both
    **qualitative** and **quantitative**)

  - Automated and manual data entry

  - Integration with forms/documents for automated indicator calculation

  - Disaggregation (e.g., by gender, age group, region)

  - Linking indicators to specific objectives or outputs in Stigdata’s
    Plan module

## **2. Key Concepts**

1.  **Indicator**: A measurable variable—either **numeric
    (quantitative)** or **descriptive (qualitative)**—used to evaluate
    performance or track progress toward goals, outcomes, and outputs.

2.  **Calculation Method**: Defines how the indicator value from a data
    source is computed (e.g., sum, average, percentage) for
    **quantitative** indicators, or how **qualitative** data is captured
    and interpreted for that period.

3.  **Data Linking**: The process of connecting an indicator to a data
    source (form entries, Modules, documents, or external systems) for
    automated updates.

4.  **Disaggregation**: Splits an indicator’s value by specific
    categories (gender, region, etc.) for more granular analysis.

5.  **Unicity (Uniqueness) Field**: A designated field to ensure the
    same record is not counted multiple times in calculations for
    **quantitative** indicators.

## **3. Functional Requirements**

### **3.1 Indicator Creation and Configuration**

1.  **Indicator Types  
    **

    - **Requirement**: The system must allow the user to specify whether
      an indicator is **Quantitative** or **Qualitative** at the time of
      creation.

    - **Rationale**:

      - **Quantitative** indicators often require numeric values and
        calculation methods.

      - **Qualitative** indicators may need text fields, rating scales,
        or other descriptive inputs (e.g., “Narrative assessment of
        stakeholder satisfaction”).

2.  **Add New Indicator  
    **

    - **Requirement**: Users can create an indicator by providing a
      name, description, and unit of measurement (if applicable).

    - **Details**:

      - Option to include a short name or code for quick reference.

      - Allow associating the indicator with a Plan level (Goal,
        Outcome, Output) or activity.

      - Provide a dropdown or toggle for indicator type (Qualitative vs.
        Quantitative).

3.  **Baseline and Target Values** (Primarily for **Quantitative**
    Indicators)

    - **Requirement**: The system allows specifying a **baseline**
      (current or starting value) and one or more **target** values
      (desired value by a certain date).

    - **Details**:

      - Users can set multiple targets for different time periods (e.g.,
        annual targets).

4.  **Indicator Frequency or Reporting Period  
    **

    - **Requirement**: Users can define how often data for an indicator
      should be updated (monthly, quarterly, annually).

    - **Details**:

      - Integrate these settings with the reporting module so the
        indicator automatically appears for data entry when due.

5.  **<span class="mark">Record Input</span>**

    - <span class="mark">**Progress Only:** Only progress achieved
      within the current time period is entered</span>

    - <span class="mark">**Cumulative Only**: Only Cumulative Values
      Achieved within the current time period are entered (i.e, the User
      is entering the current total of his progress so far)</span>

    - <span class="mark">**Progress or Cumulative**: Either the progress
      or the cumulative for the current time period can be
      entered</span>

6.  **<span class="mark">Relationship between Progress and
    Cumulative</span>**

    - <span class="mark">**Dependent:** The cumulative value depends on
      the Progress Values, i.e, Cumulative = Sum of all progress values
      to date and Vice Versa (i.e if the Cumulative is Entered the
      Progressive is calculated from the difference, between the current
      input value and last previous value</span>

      - <span class="mark">Use case: When tracking ongoing progress that
        builds over time (e.g, Kilometers of road constructed, farmers
        trained, etc.)</span>

    - <span class="mark">**Same:** The progress value is already total
      or up to date, not just for a specific period. The cumulative
      value does not add anything new; it's identical, i.e, Progress =
      Cumulative and Vice versa (Note, there is no Summation, as the
      most recent Cumulative/Progress is already a sum, or the current
      cumulative value)</span>

      - <span class="mark">**Use case**: For indicators that are
        naturally cumulative in definition (e.g, %project completion,
        current GDP Growth rate….)</span>

    - <span class="mark">**Independent**: Each data point stands on its
      own, not derived from one another, for e.g</span>

      - <span class="mark">Each Progress entry represents only that
        period (No calculation is done here at all, i.e, the Progress
        isn't calculated towards the Target</span>

      - <span class="mark">Each Cumulative entry represents only that
        period ( Cumulative is calculated against the target, to show
        the progression towards the target)</span>

      - <span class="mark">Indicator values for one location or period
        don’t affect others</span>

      - <span class="mark">If the user selects Enter either Progressive
        or Cumulative, then Independent relationship should be an
        invalid option.</span>

      - <span class="mark">**Use case:** For periodic tracking like
        monthly attendance, satisfaction rate, or test results.</span>

### **3.2 Calculation Methods for Quantitative Indicators**

1.  **Manual Entry  
    **

    - **Requirement**: Users can input numeric values directly for
      indicators that are not derived from other data sources.

2.  **<span class="mark">Automatic Aggregation</span>**

    - <span class="mark">**Sum**: Adds up a numeric field from multiple
      records.  
      </span>

    - <span class="mark">**Count**: Counts all or unique records.  
      </span>

    - <span class="mark">**Average**: Computes the mean of a numeric
      field.  
      </span>

    - <span class="mark">**Percentage**: Requires numerator/denominator
      definitions (100 × Numerator ÷ Denominator).  
      </span>

3.  **<span class="mark">Formulas and Conditional Logic</span>**

    - <span class="mark">**Requirement**: Allow for conditional filters
      (e.g., “Count only records with ‘Yes’ in a certain field”).  
      </span>

    - <span class="mark">**Details**:  
      </span>

      - <span class="mark">Provide a user-friendly interface to define
        such conditions or advanced filters.  
        </span>

### **3.3 Input Methods for Qualitative Indicators**

1.  **Structured Text Fields or Scales  
    **

    - **Requirement**: Qualitative indicators may utilize text fields,
      Likert scales (e.g., 1–5), or categorical dropdowns to capture
      narrative or descriptive data.

    - **Rationale**:

      - Facilitates capturing non-numeric evidence of progress (e.g.,
        stakeholder satisfaction described in words).

2.  **Optional Rating System** (Enhancement)

    - **Requirement**: The system could allow rating scales or custom
      rubrics to standardize how qualitative inputs are measured (e.g.,
      “High, Medium, Low” or a 5-point scale).

    - **Details**:

      - May combine rating scales with free-text fields for additional
        context, our forms tool may also be of use here.

### **3.4 Linking to Data Sources**

1.  **<span class="mark">Link to Forms  
    </span>**

    - <span class="mark">**Requirement**: If an indicator is based on
      data collected in a custom form (e.g., “Beneficiary,” “Training
      Attendance,” or “Qualitative Feedback”), the system must
      automatically calculate or update indicator values whenever new or
      changed form entries are added or updated.  
      </span>

    - <span class="mark">**Details**:  
      </span>

      - <span class="mark">**Unicity Field**: If counting unique
        participants for a quantitative indicator, specify a
        “Participant ID.”  
        </span>

      - <span class="mark">For qualitative data, link text or
        scale-based input fields to the indicator.</span>

      - <span class="mark">For Qunatitative data;</span>

        - <span class="mark">**Sum**: Adds up a **numeric field** from
          multiple responses. Unicity field is not compulsory, but it
          helps</span>

        - <span class="mark">**Average**: Computes the mean of a numeric
          field. Unicity field is not mandatory, but it helps</span>

        - <span class="mark">**Count:** Number of responses, usually
          based on a unicity field, should one wish to apply, for cases
          of double counting</span>

        - <span class="mark">**Percentage:** for the Numerator and
          Denominator, the following fields shall apply</span>

          - <span class="mark">Calculation Method\*: Sum or
            Average</span>

          - <span class="mark">Value Field\*: Linked question within the
            form</span>

          - <span class="mark">Filter/Unicity Field: Other questions
            from which the user can filter the responses for the value
            field.</span>

2.  **<span class="mark">Link to Indicators</span>**

    - <span class="mark">One or a group of indicator’s valuers triggers
      or influences another, this can be done across levels, or Projects
      (i.e, indicators found in other projects)</span>

      - <span class="mark">The Calculation/aggregation options for this
        shall be between **Sum** or **Average**</span>

      - <span class="mark">The user can use all the data or apply
        filters by period. The Sum and Average can be set to be
        calculated for certain periods, in accordance with the indicator
        reporting period.  
        </span>

3.  **<span class="mark">Link to Documents (Reporting Module)  
    </span>**

    - <span class="mark">**Requirement**:</span>

      - <span class="mark">Storage and linking of Evidence to the
        Indicator</span>

    - <span class="mark">**Details**:  
      </span>

      - <span class="mark">A “Draft → Approved” workflow ensures only
        validated data is reflected in the official indicator record.  
        </span>

      - <span class="mark">Qualitative indicators might allow for
        narrative entries directly in the document.  
        </span>

### **<span class="mark">3.5 Disaggregation (Primarily for Quantitative Indicators)</span>**

1.  **<span class="mark">Category-Based Breakdowns  
    </span>**

    - <span class="mark">**Requirement**: Allow users to specify
      disaggregation fields (e.g., “Gender,” “Age Group”). The system
      then automatically calculates and displays sub-values for each
      category based on the selected calculation Method.</span>

    - **<span class="mark">The Calculation Method selected will
      determine how the total for that period is achieved.</span>**

      - <span class="mark">**Sum**: Adds up a numeric field from
        multiple records.</span>

      - <span class="mark">**Average**: Computes the mean of a numeric
        field.  
        </span>

2.  **Multi-Level Disaggregation** (Optional Enhancement)

    - **Requirement**: If needed, more than one dimension can be applied
      simultaneously (e.g., gender × region).

    - **Details**:

      - The system generates a table or chart that shows data for each
        combination of categories.

### **3.6 Data Entry and Management**

1.  **Manual Updates  
    **

    - **Requirement**: Users can manually override or input indicator
      values—both numeric and qualitative—in case of offline data or
      exceptions.

2.  **Bulk Imports** (Primarily for Quantitative Data)

    - **Requirement**: CSV/Excel uploads for historical or large-volume
      data entry.

    - **Details**:

      - Ensure a template is provided so columns map correctly to the
        indicator’s fields.

### **3.7 Progress Tracking and History**

1.  **Versioning/History/Change Log  
    **

    - **Requirement**: The system logs changes to indicator values
      (numeric or descriptive) over time, including who updated them and
      when.

2.  **Timeline or Trend View** (Quantitative Indicators)

    - **Requirement**: A visual or tabular display that shows how an
      indicator’s numeric value has evolved across different reporting
      periods.

3.  **Qualitative Trend Summaries** (Optional Enhancement)

    - **Requirement**: A way to view historical entries for qualitative
      indicators (e.g., a series of narrative updates or average rating
      changes over time).

## **4. Integration with Other Stigdata Modules**

1.  **Plans**

    - **Requirement**: Indicators (qualitative or quantitative) must be
      easily tied to specific goals, outcomes, or outputs in the Plans

2.  **Activities**

    - **Requirement**: References to the Activities module where tasks
      may influence indicator performance (e.g., number of training
      sessions, or feedback collected during focus groups).

3.  **Dashboard and Reporting**

    - **Requirement**: Indicator values (numeric or textual) should be
      visible in dashboards (summary cards, charts) and integrated into
      standard or custom reports.

## **5. Permissions and Access Control**

1.  **Role-Based Permissions**

    - **Requirement**: Only authorized roles can create, edit, or delete
      indicators, while others may only view or comment.

2.  **Sensitive Indicators**

    - **Requirement**: Certain indicators (e.g., financial or
      politically sensitive data) may have restricted access.

    - **Details**: Admins can configure indicator-level access rules
      (view-only vs. edit).

## **6. UI/UX Considerations**

1.  **Indicator Creation Wizard  
    **

    - **Requirement**: A step-by-step interface for defining **type**
      (qualitative vs. quantitative), calculation methods, linking to
      forms, and setting disaggregation.

2.  **Clear Visualization  
    **

    - **Requirement**: For quantitative indicators, provide simple
      charts or tables to show progress over time, current vs. target
      values, and disaggregated data.

    - **Requirement**: For qualitative indicators, display aggregated
      text/ratings in a user-friendly, searchable format.

3.  **Mobile Compatibility** (Optional Enhancement)

    - **Requirement**: The interface should be responsive for users
      entering data or viewing indicator dashboards on mobile devices.

## **7. Reporting and Dashboards**

1.  **Real-Time Dashboards  
    **

    - **Requirement**: Automatic refresh of indicator values (numeric or
      textual) upon new data submissions.

2.  **Export Options  
    **

    - **Requirement**: Ability to export indicator data and charts (PDF,
      Excel) for offline sharing or presentations. For qualitative
      indicators, text exports might be needed.

3.  **Indicator Trend Analysis** (Primarily for Quantitative Data)

    - **Requirement**: Graphical representation (e.g., line chart) to
      illustrate changes across reporting periods.

## **8. Suggestions for Future Enhancements**

1.  **Deep Analytics or Advanced Data Visualization  
    **

    - Although core charts and summary tables will be provided, more
      sophisticated analytics (e.g., interactive dashboards, complex
      data slicing) could be developed as a separate module or premium
      feature.

2.  **Complex Machine Learning or Predictive Analytics  
    **

    - Using historical or real-time indicator data to predict future
      trends, resource needs, or potential bottlenecks.

    - May require specialized data pipelines and ML frameworks that go
      beyond basic indicator tracking.

3.  **Qualitative Natural Language Processing (NLP)  
    **

    - If large volumes of qualitative data accumulate (e.g., open-ended
      survey responses), an NLP feature could analyze sentiment, detect
      themes, or produce summaries.

## **10. Acceptance Criteria**

1.  **Accuracy**: Indicator calculations (sum, average, percentage,
    count) yield correct results for quantitative data; qualitative
    inputs are preserved exactly as entered.

2.  **Ease of Use**: Users can set up both qualitative and quantitative
    indicators within minutes, without extensive training.

3.  **Performance**: Indicator updates should reflect in dashboards or
    reports within an acceptable load time (e.g., under 5 seconds for
    typical queries).

4.  **Security**: Access controls prevent unauthorized editing,
    especially for sensitive indicators.

5.  **Scalability**: Must handle hundreds or thousands of indicators
    (across multiple projects) without significant performance
    degradation.

---

# 11. Implementation Plan for Codex

## 11.1 Implementation Assumptions

This implementation plan assumes Stigdata already has the following modules or foundations in place:

- Authentication and organization/team membership.
- Role-based access control.
- Plans/Logframes module with plan levels such as Goal, Outcome, Output, and Activity.
- Forms module with form schemas, questions/fields, and submitted responses.
- Documents/Reports module with evidence uploads and approval workflows.
- Dashboard/reporting layer for cards, charts, tables, and exports.

Where these modules are not fully available, Codex should implement adapter interfaces and mock service boundaries so that the Indicators feature can be integrated later without rewriting core indicator logic.

## 11.2 Recommended Delivery Sequence

Build the feature in the order below. Each chunk should be implemented as a separate pull request or commit group where possible.

1. Data model and migrations.
2. Indicator service layer and validation logic.
3. Manual indicator creation and editing.
4. Baseline, targets, reporting periods, and input-mode rules.
5. Manual data entry and value history.
6. Quantitative calculation engine.
7. Forms data-source linking.
8. Indicator-to-indicator linking.
9. Qualitative indicator capture.
10. Disaggregation engine.
11. Evidence/document linking and approval workflow.
12. Dashboard, trend views, and reporting exports.
13. Permissions, sensitive indicator access, audit logs.
14. Tests, seed data, and performance hardening.

---

# 12. Implementation Chunks

## Chunk 1 — Indicator Domain Model and Database Migrations

### Objective
Create the core database tables, enums, and relationships required to store quantitative and qualitative indicators.

### Backend Tasks

- Create an `indicators` table/model with the following fields:
  - `id`
  - `organization_id`
  - `project_id` or equivalent parent scope
  - `plan_node_id` nullable; links to Goal, Outcome, Output, or Activity
  - `name`
  - `short_name`
  - `code`
  - `description`
  - `indicator_type`: `quantitative` or `qualitative`
  - `unit_of_measurement`
  - `reporting_frequency`: `monthly`, `quarterly`, `biannual`, `annual`, `custom`
  - `record_input_mode`: `progress_only`, `cumulative_only`, `progress_or_cumulative`
  - `progress_cumulative_relationship`: `dependent`, `same`, `independent`
  - `is_sensitive`
  - `status`: `draft`, `active`, `archived`
  - `created_by`
  - `updated_by`
  - `created_at`
  - `updated_at`
  - `deleted_at` if soft deletes are used

- Create an `indicator_baselines` table:
  - `id`
  - `indicator_id`
  - `baseline_value_numeric` nullable
  - `baseline_value_text` nullable
  - `baseline_date`
  - `notes`
  - `created_by`
  - timestamps

- Create an `indicator_targets` table:
  - `id`
  - `indicator_id`
  - `target_value_numeric` nullable
  - `target_value_text` nullable
  - `target_period_start`
  - `target_period_end`
  - `target_date`
  - `notes`
  - `created_by`
  - timestamps

- Create an `indicator_values` table:
  - `id`
  - `indicator_id`
  - `period_start`
  - `period_end`
  - `progress_value_numeric` nullable
  - `cumulative_value_numeric` nullable
  - `qualitative_value_text` nullable
  - `qualitative_rating` nullable
  - `value_source`: `manual`, `form`, `indicator`, `document`, `import`
  - `source_reference_id` nullable
  - `approval_status`: `draft`, `submitted`, `approved`, `rejected`
  - `calculation_snapshot_json`
  - `notes`
  - `created_by`
  - `approved_by`
  - `approved_at`
  - timestamps

- Create an `indicator_value_history` table:
  - `id`
  - `indicator_value_id`
  - `indicator_id`
  - `old_value_json`
  - `new_value_json`
  - `change_reason`
  - `changed_by`
  - `changed_at`

### Validation Rules

- `indicator_type` is required.
- Quantitative indicators must support numeric baseline/target/value fields.
- Qualitative indicators must support text, rating, or categorical values.
- `progress_cumulative_relationship = independent` is invalid when `record_input_mode = progress_or_cumulative`.
- `unit_of_measurement` should be required for quantitative indicators unless the indicator is a percentage or index.
- `code` should be unique within an organization/project scope.

### API Endpoints

Implement or update:

- `GET /api/indicators`
- `POST /api/indicators`
- `GET /api/indicators/:id`
- `PATCH /api/indicators/:id`
- `DELETE /api/indicators/:id`
- `GET /api/indicators/:id/history`

### Acceptance Criteria

- The system can create, update, retrieve, archive, and soft-delete indicators.
- Indicators can be classified as quantitative or qualitative.
- Validation prevents invalid progress/cumulative combinations.
- Indicator records are scoped to organization and project.
- History/audit tables are ready for later value tracking.

---

## Chunk 2 — Indicator Creation Wizard UI

### Objective
Build a step-by-step UI for creating and configuring indicators.

### UI Flow

#### Step 1: Basic Details
Fields:

- Indicator name
- Short name
- Code
- Description
- Indicator type: Quantitative or Qualitative
- Unit of measurement
- Sensitive indicator toggle

#### Step 2: Link to Plan
Fields:

- Project selector
- Plan level selector: Goal, Outcome, Output, Activity
- Plan node selector

Behavior:

- If a plan node is selected, show breadcrumb: `Project > Goal > Outcome > Output > Activity`.
- Allow the user to continue without linking to a plan node only if business rules allow standalone indicators.

#### Step 3: Reporting Configuration
Fields:

- Reporting frequency
- Reporting period start date
- Reporting period end date or custom schedule
- Record input mode:
  - Progress only
  - Cumulative only
  - Progress or cumulative
- Relationship between progress and cumulative:
  - Dependent
  - Same
  - Independent

Behavior:

- If record input mode is `progress_or_cumulative`, disable `independent` relationship.
- Show helper text explaining the selected relationship.

#### Step 4: Baseline and Targets
Fields:

- Baseline value
- Baseline date
- Target rows:
  - Target value
  - Target date or target period
  - Notes

Behavior:

- Allow multiple targets.
- Validate that target dates align with reporting periods where applicable.

#### Step 5: Data Source
Options:

- Manual entry
- Link to form
- Link to another indicator
- Link to document/report evidence

Behavior:

- Only show calculation setup when the user selects an automated source.
- Qualitative indicators should show text, scale, or categorical configuration.

#### Step 6: Review and Publish
Display:

- Summary of all selected configurations.
- Warnings for missing optional items.
- `Save as Draft` and `Publish Indicator` actions.

### Frontend Components

- `IndicatorWizard`
- `IndicatorBasicDetailsStep`
- `IndicatorPlanLinkStep`
- `IndicatorReportingConfigStep`
- `IndicatorBaselineTargetsStep`
- `IndicatorDataSourceStep`
- `IndicatorReviewStep`
- `IndicatorTypeBadge`
- `ProgressCumulativeHelperCard`

### Acceptance Criteria

- Users can complete indicator setup in a guided wizard.
- Invalid combinations are blocked before submission.
- The wizard supports draft save and final publish.
- The UI clearly distinguishes quantitative and qualitative configurations.

---

## Chunk 3 — Reporting Period and Input-Mode Engine

### Objective
Implement the business logic that determines how progress and cumulative values are stored and calculated for each reporting period.

### Backend Tasks

- Create a service: `IndicatorPeriodService`.
- Create helper methods:
  - `generatePeriods(indicator, startDate, endDate)`
  - `getCurrentPeriod(indicator, date)`
  - `getPreviousApprovedValue(indicatorId, periodStart)`
  - `validateInputMode(indicator, submittedValue)`

### Calculation Rules

#### Progress Only

- User enters only `progress_value_numeric`.
- If relationship is `dependent`, cumulative is calculated as sum of all approved progress values to date.
- If relationship is `same`, cumulative equals progress.
- If relationship is `independent`, cumulative remains empty unless separately generated by reporting logic.

#### Cumulative Only

- User enters only `cumulative_value_numeric`.
- If relationship is `dependent`, progress is calculated as current cumulative minus previous cumulative.
- If relationship is `same`, progress equals cumulative.
- If relationship is `independent`, progress remains empty.

#### Progress or Cumulative

- User may enter either progress or cumulative.
- If progress is entered and relationship is `dependent`, cumulative is calculated as previous cumulative plus progress.
- If cumulative is entered and relationship is `dependent`, progress is calculated as current cumulative minus previous cumulative.
- If relationship is `same`, entered value is copied to both progress and cumulative.
- `independent` is not allowed.

### Edge Cases

- First period has no previous cumulative value.
- Negative progress should only be allowed if the indicator configuration permits reversals/corrections.
- Rejected values should not affect approved cumulative values.
- Draft values should not appear in official dashboards.

### Acceptance Criteria

- Progress and cumulative values are calculated correctly for all valid configurations.
- Invalid input/relationship combinations are rejected.
- Draft/rejected values are excluded from official totals.
- Approved values form the basis for cumulative calculations.

---

## Chunk 4 — Manual Data Entry and Approval Workflow

### Objective
Allow authorized users to manually enter, submit, approve, reject, and revise indicator values.

### Backend Tasks

- Implement endpoints:
  - `POST /api/indicators/:id/values`
  - `GET /api/indicators/:id/values`
  - `PATCH /api/indicator-values/:valueId`
  - `POST /api/indicator-values/:valueId/submit`
  - `POST /api/indicator-values/:valueId/approve`
  - `POST /api/indicator-values/:valueId/reject`

- Enforce value state transitions:
  - Draft → Submitted
  - Submitted → Approved
  - Submitted → Rejected
  - Rejected → Draft after revision
  - Approved → Revised version, only through controlled update

### UI Flow

- User opens indicator detail page.
- User clicks `Enter Data`.
- Modal/page shows the current reporting period.
- User enters progress, cumulative, or qualitative value depending on configuration.
- User can attach notes and evidence.
- User saves draft or submits for approval.
- Approver sees pending submissions in approval queue.
- Approver approves or rejects with comments.

### Acceptance Criteria

- Users can manually submit indicator values for a period.
- Approvals determine whether values appear in dashboards.
- Rejections require a reason/comment.
- Every change is logged in value history.

---

## Chunk 5 — Quantitative Calculation Engine

### Objective
Implement calculation methods for quantitative indicators.

### Supported Methods

- Manual entry
- Sum
- Count
- Unique count
- Average
- Percentage

### Backend Tasks

- Create table/model `indicator_data_sources`:
  - `id`
  - `indicator_id`
  - `source_type`: `manual`, `form`, `indicator`, `document`, `external`
  - `source_id`
  - `calculation_method`: `sum`, `count`, `unique_count`, `average`, `percentage`
  - `value_field_id`
  - `numerator_config_json`
  - `denominator_config_json`
  - `filter_config_json`
  - `unicity_field_id`
  - `period_filter_mode`: `all_time`, `current_period`, `custom_period`
  - timestamps

- Create service: `IndicatorCalculationService`.
- Implement methods:
  - `calculateSum(sourceConfig, period)`
  - `calculateCount(sourceConfig, period)`
  - `calculateUniqueCount(sourceConfig, period)`
  - `calculateAverage(sourceConfig, period)`
  - `calculatePercentage(sourceConfig, period)`
  - `applyFilters(records, filterConfig)`
  - `applyUnicity(records, unicityField)`

### Percentage Rule

Percentage calculation should follow:

```text
100 × numerator ÷ denominator
```

For numerator and denominator, support:

- Calculation method: Sum or Average.
- Value field: linked question/field within the form.
- Filter/unicity field: additional form questions used to filter or deduplicate responses.

### Acceptance Criteria

- Sum, count, unique count, average, and percentage return correct values.
- Filters can be applied before calculation.
- Unicity fields prevent double counting where configured.
- Calculation snapshots are stored with generated indicator values.

---

## Chunk 6 — Link Indicators to Forms

### Objective
Allow indicators to automatically calculate values from form responses.

### Backend Tasks

- Add a form-source configuration API:
  - `POST /api/indicators/:id/data-sources/forms`
  - `PATCH /api/indicator-data-sources/:id`
  - `DELETE /api/indicator-data-sources/:id`
  - `POST /api/indicators/:id/recalculate`

- Add background recalculation trigger when:
  - A linked form response is created.
  - A linked form response is updated.
  - A linked form response is deleted or invalidated.
  - A linked form field configuration changes.

### UI Flow

- User selects `Link to Form` in indicator wizard.
- User chooses form.
- User chooses calculation method.
- User chooses value field.
- User optionally chooses unicity field.
- User adds filters, for example:
  - `Gender = Female`
  - `Training Completed = Yes`
  - `State = Lagos`
- User previews calculation using existing records.
- User saves configuration.

### Preview Panel

Show:

- Number of matching records.
- Number of unique records if unicity is applied.
- Calculated value for selected period.
- Warning if selected value field is not numeric for Sum/Average.

### Acceptance Criteria

- Indicators can be linked to form fields.
- Calculations refresh when relevant form responses change.
- Users can preview formula results before saving.
- The system blocks invalid field selections.

---

## Chunk 7 — Link Indicators to Other Indicators

### Objective
Allow one indicator to derive its value from one or more other indicators.

### Backend Tasks

- Extend `indicator_data_sources` to support `source_type = indicator`.
- Create table/model `indicator_source_indicators`:
  - `id`
  - `indicator_data_source_id`
  - `source_indicator_id`
  - `weight` nullable
  - timestamps

- Support aggregation options:
  - Sum
  - Average

- Add cycle detection:
  - Prevent Indicator A from depending on Indicator B if B already depends on A directly or indirectly.

### UI Flow

- User selects `Link to Indicators`.
- User searches/selects one or more source indicators.
- User selects aggregation method: Sum or Average.
- User selects period mode:
  - Use all available approved data.
  - Use matching reporting period.
  - Use custom date range.
- User previews output.

### Acceptance Criteria

- An indicator can derive values from one or more indicators.
- Sum and average calculations work across selected indicators.
- Circular dependencies are blocked.
- Only approved source values are used in official calculations.

---

## Chunk 8 — Qualitative Indicator Configuration and Entry

### Objective
Support narrative, categorical, and rating-scale qualitative indicators.

### Backend Tasks

- Add table/model `qualitative_indicator_configs`:
  - `id`
  - `indicator_id`
  - `input_type`: `text`, `likert_scale`, `category`, `rubric`
  - `scale_min`
  - `scale_max`
  - `scale_labels_json`
  - `category_options_json`
  - `requires_narrative`
  - timestamps

- Add support for qualitative values in `indicator_values`:
  - `qualitative_value_text`
  - `qualitative_rating`
  - `qualitative_category`

### UI Flow

- For qualitative indicators, user selects input format:
  - Narrative text
  - Rating scale
  - Dropdown category
  - Rubric
- User decides whether narrative evidence is required.
- During data entry, show the configured qualitative fields.
- Trend view shows previous narratives and rating changes over time.

### Acceptance Criteria

- Qualitative indicators can capture text, categories, ratings, or rubrics.
- Qualitative inputs are preserved exactly as entered.
- Optional ratings can be summarized over time.
- Qualitative entries can be searched and exported.

---

## Chunk 9 — Disaggregation Engine

### Objective
Allow users to break down quantitative indicator values by categories such as gender, age group, region, or other form fields.

### Backend Tasks

- Create table/model `indicator_disaggregations`:
  - `id`
  - `indicator_id`
  - `source_type`: `form`, `indicator`, `manual`
  - `field_id`
  - `field_label`
  - `level`: numeric order for multi-level disaggregation
  - timestamps

- Create table/model `indicator_disaggregated_values`:
  - `id`
  - `indicator_value_id`
  - `indicator_id`
  - `period_start`
  - `period_end`
  - `dimension_values_json`
  - `value_numeric`
  - timestamps

- Implement:
  - Single-level breakdown.
  - Multi-level breakdown, for example `gender × region`.
  - Disaggregated sum and average.

### UI Flow

- User opens indicator configuration.
- User selects `Disaggregation`.
- User adds one or more dimensions.
- User previews table output.
- Dashboard shows disaggregated chart/table.

### Acceptance Criteria

- Users can configure one or more disaggregation fields.
- The system calculates sub-values based on the selected calculation method.
- Multi-level disaggregation produces a matrix/table.
- Disaggregation updates when source data changes.

---

## Chunk 10 — Evidence and Document Linking

### Objective
Allow users to link documents, reports, and evidence files to indicator values.

### Backend Tasks

- Create table/model `indicator_evidence`:
  - `id`
  - `indicator_id`
  - `indicator_value_id` nullable
  - `document_id` nullable
  - `file_id` nullable
  - `title`
  - `description`
  - `evidence_type`
  - `approval_status`
  - `uploaded_by`
  - `approved_by`
  - `approved_at`
  - timestamps

- Integrate with Documents/Reports module.
- Ensure only approved evidence is shown as official evidence where required.

### UI Flow

- On indicator value entry, user can attach evidence.
- Evidence appears in an `Evidence` tab on the indicator detail page.
- Approvers can approve or reject evidence.
- Approved evidence is visible in reports and exports.

### Acceptance Criteria

- Indicator values can have one or more evidence files/documents.
- Draft evidence does not become official until approved.
- Users can view evidence history.
- Reports can include evidence links or attachment references.

---

## Chunk 11 — Indicator Detail Page

### Objective
Create a complete page for viewing indicator configuration, current performance, history, evidence, and linked sources.

### UI Sections

1. Header
   - Indicator name
   - Type badge
   - Status
   - Sensitive badge if applicable
   - Linked project/plan level
   - Actions: Edit, Enter Data, Recalculate, Export

2. Summary Cards
   - Baseline
   - Latest approved progress
   - Latest approved cumulative
   - Current target
   - Percent achievement
   - Last updated

3. Trend View
   - Line chart for quantitative indicators.
   - Timeline/narrative feed for qualitative indicators.

4. Values Table
   - Period
   - Progress
   - Cumulative
   - Target
   - Status
   - Source
   - Updated by
   - Updated at

5. Disaggregation Tab
   - Table and chart for configured dimensions.

6. Evidence Tab
   - Evidence list, status, uploader, approval state.

7. History Tab
   - Change log of values and configuration changes.

### Acceptance Criteria

- Users can understand indicator status from a single page.
- Quantitative and qualitative indicators have appropriate views.
- Sensitive indicators respect access restrictions.
- All major actions are available from the detail page.

---

## Chunk 12 — Indicator List and Filters

### Objective
Create a searchable, filterable list of indicators.

### UI Requirements

Columns:

- Indicator name
- Code
- Type
- Linked plan level
- Reporting frequency
- Latest value
- Target
- Achievement
- Status
- Last updated

Filters:

- Project
- Plan level
- Indicator type
- Status
- Reporting frequency
- Sensitive indicator
- Due for reporting
- Created by

Actions:

- Create indicator
- Bulk import
- Export list
- Archive selected indicators

### Acceptance Criteria

- Users can search and filter indicators quickly.
- List supports pagination.
- Sensitive indicators are hidden or restricted based on permissions.
- Due indicators can be identified easily.

---

## Chunk 13 — Bulk Import for Historical Data

### Objective
Allow users to import historical indicator values from CSV/Excel.

### Backend Tasks

- Add endpoints:
  - `GET /api/indicators/:id/import-template`
  - `POST /api/indicators/:id/import-preview`
  - `POST /api/indicators/:id/import-confirm`

- Import template columns:
  - Indicator code
  - Period start
  - Period end
  - Progress value
  - Cumulative value
  - Qualitative value
  - Rating/category
  - Notes
  - Evidence reference

### UI Flow

- User downloads template.
- User uploads completed file.
- System validates rows.
- Preview shows valid rows and errors.
- User confirms import.
- Imported values are saved as draft or submitted depending on permission.

### Acceptance Criteria

- Users can import historical values.
- Invalid rows are clearly reported.
- Import does not overwrite approved values unless explicitly allowed.
- Imported records are logged with `value_source = import`.

---

## Chunk 14 — Dashboard and Reporting

### Objective
Expose indicator data in dashboards and reports.

### Dashboard Widgets

- Indicator performance summary cards.
- Current value vs target.
- Trend line by reporting period.
- Disaggregation bar/table.
- Due reporting indicators.
- Indicators awaiting approval.
- Qualitative narrative summary panel.

### Reporting Exports

Support exports to:

- Excel
- PDF
- CSV

Export should include:

- Indicator metadata.
- Baseline and targets.
- Periodic values.
- Disaggregation values.
- Evidence references.
- Approval status.

### Acceptance Criteria

- Dashboards refresh when approved data changes.
- Draft and rejected values do not appear in official dashboards.
- Users can export indicator data.
- Qualitative indicators export text without truncation.

---

## Chunk 15 — Permissions, Sensitive Indicators, and Audit Logs

### Objective
Secure indicator creation, editing, data entry, approvals, and sensitive indicator access.

### Suggested Permissions

- `indicators.view`
- `indicators.view_sensitive`
- `indicators.create`
- `indicators.edit`
- `indicators.delete`
- `indicators.archive`
- `indicators.enter_data`
- `indicators.submit_data`
- `indicators.approve_data`
- `indicators.reject_data`
- `indicators.configure_sources`
- `indicators.configure_disaggregation`
- `indicators.export`
- `indicators.import`

### Role Rules

- View-only users can view non-sensitive indicators.
- Data entry users can submit values but cannot approve their own submissions unless explicitly allowed.
- Approvers can approve/reject submitted values.
- Admins can configure sensitive access.
- Sensitive indicators require explicit permission.

### Audit Events

Log:

- Indicator created.
- Indicator updated.
- Indicator archived/deleted.
- Data source linked/updated/removed.
- Value drafted/submitted/approved/rejected/revised.
- Evidence uploaded/approved/rejected.
- Export generated.
- Sensitive indicator viewed.

### Acceptance Criteria

- Unauthorized users cannot create/edit/delete indicators.
- Sensitive indicators are protected.
- All major actions are auditable.
- Approval duties can be separated from data entry duties.

---

## Chunk 16 — Tests and Quality Assurance

### Objective
Ensure indicator calculations, workflows, and permissions are reliable.

### Unit Tests

Test:

- Indicator validation rules.
- Progress/cumulative calculation rules.
- Sum/count/unique count/average/percentage calculations.
- Filters and unicity logic.
- Period generation.
- Indicator-to-indicator cycle detection.
- Disaggregation calculation.

### Integration Tests

Test:

- Indicator creation wizard API submission.
- Manual data entry approval workflow.
- Form response triggers recalculation.
- Indicator-to-indicator recalculation.
- Evidence approval flow.
- Bulk import preview and confirm.
- Dashboard official-value filtering.

### Permission Tests

Test:

- Sensitive indicator access.
- Data entry without approval permission.
- Approver restrictions.
- Export permission.
- Configuration permission.

### Acceptance Criteria

- All critical calculation paths are covered.
- Approval workflow is tested end-to-end.
- Unauthorized access is blocked in API and UI.
- Dashboard values match approved source records.

---

# 13. Suggested Folder and File Structure

Codex should adapt names to the existing codebase, but the recommended structure is:

```text
src/
  modules/
    indicators/
      api/
        indicator.routes.ts
        indicator-value.routes.ts
        indicator-source.routes.ts
        indicator-import.routes.ts
      components/
        IndicatorWizard.tsx
        IndicatorList.tsx
        IndicatorDetail.tsx
        IndicatorSummaryCards.tsx
        IndicatorTrendChart.tsx
        IndicatorValuesTable.tsx
        IndicatorEvidenceTab.tsx
        IndicatorDisaggregationTab.tsx
        IndicatorHistoryTab.tsx
      services/
        indicator.service.ts
        indicator-calculation.service.ts
        indicator-period.service.ts
        indicator-disaggregation.service.ts
        indicator-permission.service.ts
        indicator-import.service.ts
      models/
        indicator.model.ts
        indicator-value.model.ts
        indicator-target.model.ts
        indicator-data-source.model.ts
        indicator-disaggregation.model.ts
        indicator-evidence.model.ts
      validators/
        indicator.schema.ts
        indicator-value.schema.ts
        indicator-source.schema.ts
      tests/
        indicator-calculation.test.ts
        indicator-workflow.test.ts
        indicator-permissions.test.ts
```

---

# 14. Data Model Summary for Codex

## Core Tables

| Table | Purpose |
|---|---|
| `indicators` | Stores indicator metadata and configuration. |
| `indicator_baselines` | Stores baseline values. |
| `indicator_targets` | Stores one or more target values by date/period. |
| `indicator_values` | Stores period-by-period progress, cumulative, or qualitative values. |
| `indicator_value_history` | Stores change history for values. |
| `indicator_data_sources` | Stores manual/form/indicator/document source configuration. |
| `indicator_source_indicators` | Stores indicator-to-indicator relationships. |
| `qualitative_indicator_configs` | Stores text, scale, category, and rubric configuration. |
| `indicator_disaggregations` | Stores configured disaggregation dimensions. |
| `indicator_disaggregated_values` | Stores calculated disaggregated outputs. |
| `indicator_evidence` | Links evidence documents/files to indicators and values. |

---

# 15. UI/UX Flow Summary for Codex

## Primary User Flow: Create Indicator

```text
Indicators List
  → Create Indicator
  → Basic Details
  → Link to Plan
  → Reporting Configuration
  → Baseline and Targets
  → Data Source Setup
  → Disaggregation Setup
  → Review
  → Save Draft / Publish
```

## Primary User Flow: Enter Manual Value

```text
Indicator Detail
  → Enter Data
  → Select/confirm reporting period
  → Enter progress/cumulative/qualitative value
  → Attach evidence
  → Save Draft / Submit
  → Approval Queue
  → Approve / Reject
  → Dashboard updates if approved
```

## Primary User Flow: Link to Form

```text
Indicator Detail or Wizard
  → Data Source
  → Select Form
  → Select Calculation Method
  → Select Value Field
  → Select Unicity Field where needed
  → Add Filters
  → Preview Calculation
  → Save
  → Recalculate
```

## Primary User Flow: Dashboard Review

```text
Dashboard
  → Indicator Summary Cards
  → Trend Chart
  → Current vs Target
  → Disaggregation View
  → Evidence Links
  → Export
```

---

# 16. Codex Implementation Prompts

Use these prompts sequentially.

## Prompt 1 — Data Model

Implement the Indicators feature database models and migrations based on the data model summary in this Markdown file. Include indicators, baselines, targets, values, value history, data sources, source indicators, qualitative configs, disaggregations, disaggregated values, and evidence. Add enum validation and organization/project scoping. Do not implement UI yet.

## Prompt 2 — Core Services

Implement the Indicator service layer, period service, validation rules, and progress/cumulative calculation rules. Include support for progress-only, cumulative-only, and progress-or-cumulative input modes. Enforce the invalid combination where independent relationship cannot be used with progress-or-cumulative input.

## Prompt 3 — CRUD API

Implement REST API endpoints for creating, reading, updating, archiving, deleting, and listing indicators. Include filters for project, plan level, indicator type, status, reporting frequency, sensitive indicator, and due-for-reporting. Enforce permissions at the API level.

## Prompt 4 — Creation Wizard UI

Build the Indicator Creation Wizard with steps for basic details, plan link, reporting configuration, baseline/targets, data source setup, disaggregation, and review. Include inline validation and helper text for progress/cumulative relationships.

## Prompt 5 — Manual Values and Approval

Implement manual indicator value entry, draft/submitted/approved/rejected workflow, approval queue, rejection comments, and value history logging. Ensure only approved values appear in official calculations and dashboards.

## Prompt 6 — Calculation Engine

Implement quantitative calculations for sum, count, unique count, average, and percentage. Add filtering and unicity support. Store calculation snapshots for generated indicator values.

## Prompt 7 — Form Linking

Implement linking indicators to form responses. Allow users to select form, value field, calculation method, unicity field, and filters. Add preview calculation and automatic recalculation when linked form responses change.

## Prompt 8 — Indicator-to-Indicator Linking

Implement indicator-to-indicator data sources using sum or average aggregation. Add cycle detection and period filtering. Use only approved source indicator values.

## Prompt 9 — Qualitative Indicators

Implement qualitative indicator configuration and data entry for narrative text, rating scales, categories, and rubrics. Add qualitative trend/history display and export support.

## Prompt 10 — Disaggregation

Implement disaggregation configuration and calculation. Support single-level and multi-level breakdowns such as gender by region. Display results in tables and charts on the indicator detail page.

## Prompt 11 — Evidence Linking

Implement evidence linking to indicators and indicator values. Integrate with the documents/reports module where available. Add evidence approval status and include approved evidence in exports.

## Prompt 12 — Dashboard and Exports

Implement dashboard widgets for indicator summaries, current vs target, trend analysis, disaggregation, due reporting, pending approvals, and qualitative summaries. Add Excel, CSV, and PDF exports.

## Prompt 13 — Permissions and Audit Logs

Implement indicator permissions, sensitive indicator access rules, and audit logs for all major actions including sensitive views, exports, approvals, value changes, data-source changes, and evidence changes.

## Prompt 14 — Tests

Add unit, integration, and permission tests for the Indicators feature. Cover all calculation methods, progress/cumulative logic, approval workflow, form recalculation, disaggregation, imports, exports, and sensitive access restrictions.

---

# 17. Definition of Done

The Indicators feature is complete when:

- Users can create quantitative and qualitative indicators.
- Indicators can be linked to plan levels or activities.
- Baselines, multiple targets, reporting frequencies, and data entry modes work correctly.
- Manual and automated values are supported.
- Form-linked indicators calculate correctly.
- Indicator-to-indicator linking works without circular dependencies.
- Disaggregation works for configured dimensions.
- Qualitative indicators support narrative/rating/category inputs.
- Evidence can be attached and approved.
- Only approved values appear in official dashboards and reports.
- Sensitive indicators are protected by permissions.
- Exports are available for indicator data.
- Audit history is available for configuration and value changes.
- Automated tests cover the critical paths.
