"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Calendar, ChevronLeft, ChevronRight, Plus, X } from "lucide-react";

import {
  createMEIndicator,
  createMEIndicatorDataSource,
  createMEIndicatorDisaggregation,
  updateMEIndicator,
} from "@/lib/api/standards";
import { getApiErrorMessage } from "@/lib/api/client";
import {
  generateIndicatorPeriods,
  validateIndicatorInputMode,
  type IndicatorPeriod,
} from "@/lib/indicators/period-engine";
import { Stepper } from "@/components/ui/stepper";
import type { DataSource, MEIndicator, QualitativeInputType, ReportingFrequency, VisualizationType } from "@/types/standards";

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  mode: "create" | "edit";
  policyVersionId: string;
  initial?: Partial<MEIndicator> | null;
}

type IndicatorType = "quantitative" | "qualitative";
type InputMode = "automatic" | "manual" | "imported" | "hybrid";
type RecordInputMode = "progress_only" | "cumulative_only" | "progress_or_cumulative";
type ProgressRelationship = "dependent" | "same" | "independent";
type TargetDirection = "higher_better" | "lower_better" | "exact" | "range";
type CalculationMethod = "manual" | "sum" | "count" | "unique_count" | "average" | "percentage" | "ratio" | "formula";
type BuilderDataSource = DataSource;
type EnginePreset = {
  calculation_source: string;
  policy_standard_code: string;
  rule_parameter_key: string;
  helper: string;
};

type TargetRow = {
  id: string;
  label: string;
  value: string;
  date: string;
};

type DisaggregationRow = {
  id: string;
  field_id: string;
  field_label: string;
};

const STEPS = [
  "Basic Details",
  "Input Mode",
  "Data Source & Calculation",
  "Disaggregation",
  "Targets & Thresholds",
  "Review & Activate",
];

const DATA_SOURCES: DataSource[] = [
  "manual",
  "food_handler_registry",
  "medical_test_records",
  "test_results",
  "certificate_records",
  "facility_records",
  "facility_handler_mapping",
  "test_centers_labs",
  "inspections",
  "training_orientation",
  "payments",
];
const FREQUENCIES: ReportingFrequency[] = ["daily", "weekly", "monthly", "quarterly", "biannual", "annual", "ad_hoc", "custom"];
const VISUALIZATIONS: VisualizationType[] = ["card", "line", "bar", "map", "table", "pie"];
const UNITS = ["Number", "Percentage", "Rate", "Score", "Text", "Yes/No"];
const today = "2026-06-15";
const ENGINE_PRESETS: Record<Exclude<BuilderDataSource, "manual">, EnginePreset> = {
  food_handler_registry: {
    calculation_source: "system_required_fields",
    policy_standard_code: "",
    rule_parameter_key: "",
    helper: "Use this for completeness and registration-quality KPIs derived from food handler profiles.",
  },
  medical_test_records: {
    calculation_source: "return_to_work_clearances",
    policy_standard_code: "FH-RTW-2024-001",
    rule_parameter_key: "standard_exclusion_period_hours_after_symptoms_stop",
    helper: "Best fit for return-to-work and illness clearance KPIs tied to medical workflows.",
  },
  test_results: {
    calculation_source: "",
    policy_standard_code: "",
    rule_parameter_key: "",
    helper: "Use for custom test-result KPIs when a policy-linked preset is not available yet.",
  },
  certificate_records: {
    calculation_source: "certificates",
    policy_standard_code: "FH-VALIDITY-2024-001",
    rule_parameter_key: "certificate_validity_months",
    helper: "Use for certification coverage, expiry, and certificate lifecycle KPIs.",
  },
  facility_records: {
    calculation_source: "medical_facilities",
    policy_standard_code: "FH-FAC-2024-001",
    rule_parameter_key: "reaccreditation_interval_months",
    helper: "Use for facility compliance and accreditation performance KPIs.",
  },
  facility_handler_mapping: {
    calculation_source: "",
    policy_standard_code: "",
    rule_parameter_key: "",
    helper: "Use for operational mapping KPIs where handlers are linked to specific facilities.",
  },
  test_centers_labs: {
    calculation_source: "",
    policy_standard_code: "",
    rule_parameter_key: "",
    helper: "Use for custom lab throughput or center performance KPIs.",
  },
  inspections: {
    calculation_source: "qr_verification_logs",
    policy_standard_code: "FH-CERT-2024-001",
    rule_parameter_key: "requires_qr_code",
    helper: "Use for QR verification and inspection-linked compliance indicators.",
  },
  training_orientation: {
    calculation_source: "",
    policy_standard_code: "",
    rule_parameter_key: "",
    helper: "Use for training uptake and orientation completion KPIs.",
  },
  payments: {
    calculation_source: "",
    policy_standard_code: "",
    rule_parameter_key: "",
    helper: "Use for revenue, payment completion, and settlement-oriented KPIs.",
  },
};

function calculationTypeFromMethod(method: CalculationMethod): MEIndicator["calculation_type"] {
  if (method === "manual") return "";
  if (method === "percentage") return "percentage";
  if (method === "count") return "count";
  if (method === "unique_count") return "unique_count";
  if (method === "average") return "average";
  if (method === "ratio") return "ratio";
  if (method === "sum") return "sum";
  if (method === "formula") return "formula";
  return "";
}

function valueFromConfig(config: Record<string, unknown> | undefined, key: string, fallback = "") {
  const value = config?.[key];
  return value == null ? fallback : String(value);
}

function boolFromConfig(config: Record<string, unknown> | undefined, key: string, fallback = false) {
  const value = config?.[key];
  return typeof value === "boolean" ? value : fallback;
}

function targetsFromConfig(config: Record<string, unknown> | undefined): TargetRow[] {
  const rows = Array.isArray(config?.targets) ? config.targets : [];
  const parsed = rows
    .filter((row): row is Record<string, unknown> => Boolean(row) && typeof row === "object")
    .map((row, index) => ({
      id: String(row.id ?? `target-${index + 1}`),
      label: String(row.label ?? `Target ${index + 1}`),
      value: String(row.value ?? ""),
      date: String(row.date ?? ""),
    }));
  return parsed.length ? parsed : [{ id: "target-1", label: "Target 1", value: "", date: "2026-12-31" }];
}

function nice(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatStatus(status: string) {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}

export function MEIndicatorFormDrawer({ open, onClose, onSuccess, mode, policyVersionId, initial }: Props) {
  const queryClient = useQueryClient();
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [targets, setTargets] = useState<TargetRow[]>([{ id: "target-1", label: "Target 1", value: "", date: "2026-12-31" }]);
  const [disaggregationRows, setDisaggregationRows] = useState<DisaggregationRow[]>([{ id: "dimension-1", field_id: "", field_label: "" }]);
  const [operationalSource, setOperationalSource] = useState({
    value_field_id: "",
    unicity_field_id: "",
    date_field_id: "date",
    scope_field_id: "",
    filter_field: "",
    filter_value: "",
  });
  const [form, setForm] = useState({
    indicator_name: "",
    indicator_code: "",
    short_name: "",
    description: "",
    indicator_type: "quantitative" as IndicatorType,
    unit_of_measurement: "Number",
    input_mode: "manual" as InputMode,
    reporting_frequency: "quarterly" as ReportingFrequency,
    record_input_mode: "progress_only" as RecordInputMode,
    progress_relationship: "dependent" as ProgressRelationship,
    target_direction: "higher_better" as TargetDirection,
    visibility_scope: "federal_and_state",
    calculation_method: "manual" as CalculationMethod,
    calculation_source: "",
    data_source: "manual" as BuilderDataSource,
    policy_standard_code: "",
    rule_parameter_key: "",
    formula_expression: "",
    numerator: "",
    denominator: "",
    baseline_value: "0",
    baseline_date: today,
    target_value: "",
    target_date: "2026-12-31",
    threshold_green: "80",
    threshold_amber: "60",
    visualization_type: "line" as VisualizationType,
    qualitative_input_type: "text" as QualitativeInputType,
    qualitative_scale_min: "1",
    qualitative_scale_max: "5",
    qualitative_scale_labels: "",
    qualitative_category_options: "",
    qualitative_requires_narrative: false,
    link_data_source: false,
    disaggregation: false,
    allow_negative_progress: false,
    override_requires_reason: true,
    federal_dashboard_visible: true,
    state_dashboard_visible: true,
    mandatory: true,
  });

  useEffect(() => {
    if (!open) return;
    setError("");
    setStep(0);
    const formula = initial?.formula_config ?? {};
    const thresholds = initial?.threshold_config ?? {};
    setForm({
      indicator_name: initial?.indicator_name ?? "",
      indicator_code: initial?.indicator_code ?? "",
      short_name: valueFromConfig(formula, "short_name"),
      description: initial?.description ?? "",
      indicator_type: (initial?.kpi_type ?? valueFromConfig(formula, "indicator_type", "quantitative")) as IndicatorType,
      unit_of_measurement: initial?.unit_of_measurement ?? valueFromConfig(formula, "unit_of_measurement", "Number"),
      input_mode: ((initial?.input_mode ?? valueFromConfig(formula, "input_mode", "manual")) === "automated"
        ? "automatic"
        : (initial?.input_mode ?? valueFromConfig(formula, "input_mode", "manual"))) as InputMode,
      reporting_frequency: initial?.reporting_frequency ?? "quarterly",
      record_input_mode: (initial?.record_input_type ?? valueFromConfig(formula, "record_input_mode", "progress_only")) as RecordInputMode,
      progress_relationship: (initial?.progress_cumulative_relationship ?? valueFromConfig(formula, "progress_relationship", "dependent")) as ProgressRelationship,
      target_direction: (initial?.target_direction ?? valueFromConfig(formula, "target_direction", "higher_better")) as TargetDirection,
      visibility_scope: valueFromConfig(initial?.visibility_scope as Record<string, unknown> | undefined, "scope_type", valueFromConfig(formula, "visibility_scope", "federal_and_state")),
      calculation_method: valueFromConfig(formula, "calculation_method", "manual") as CalculationMethod,
      calculation_source: initial?.calculation_source ?? valueFromConfig(formula, "calculation_source"),
      data_source: valueFromConfig(formula, "builder_data_source", initial?.data_source ?? "manual") as BuilderDataSource,
      policy_standard_code: initial?.policy_standard_code ?? valueFromConfig(formula, "policy_standard_code"),
      rule_parameter_key: initial?.rule_parameter_key ?? valueFromConfig(formula, "rule_parameter_key"),
      formula_expression: valueFromConfig(formula, "expression"),
      numerator: valueFromConfig(formula, "numerator"),
      denominator: valueFromConfig(formula, "denominator"),
      baseline_value: valueFromConfig(formula, "baseline_value", "0"),
      baseline_date: valueFromConfig(formula, "baseline_date", today),
      target_value: initial?.target_value != null ? String(initial.target_value) : valueFromConfig(formula, "target_value"),
      target_date: valueFromConfig(formula, "target_date", "2026-12-31"),
      threshold_green: String(thresholds.green_min ?? 80),
      threshold_amber: String(thresholds.amber_min ?? 60),
      visualization_type: initial?.visualization_type ?? "line",
      qualitative_input_type: initial?.qualitative_config?.input_type ?? "text",
      qualitative_scale_min: initial?.qualitative_config?.scale_min == null ? "1" : String(initial.qualitative_config.scale_min),
      qualitative_scale_max: initial?.qualitative_config?.scale_max == null ? "5" : String(initial.qualitative_config.scale_max),
      qualitative_scale_labels: Object.entries(initial?.qualitative_config?.scale_labels_json ?? {}).map(([key, value]) => `${key}:${value}`).join(", "),
      qualitative_category_options: (initial?.qualitative_config?.category_options_json ?? []).join(", "),
      qualitative_requires_narrative: initial?.qualitative_config?.requires_narrative ?? false,
      link_data_source: boolFromConfig(formula, "link_data_source"),
      disaggregation: boolFromConfig(formula, "disaggregation"),
      allow_negative_progress: boolFromConfig(formula, "allow_negative_progress"),
      override_requires_reason: initial?.override_requires_reason ?? boolFromConfig(formula, "override_requires_reason", true),
      federal_dashboard_visible: initial?.federal_dashboard_visible ?? true,
      state_dashboard_visible: initial?.state_dashboard_visible ?? true,
      mandatory: initial?.mandatory ?? true,
    });
    setOperationalSource({
      value_field_id: valueFromConfig(formula, "value_field_id"),
      unicity_field_id: valueFromConfig(formula, "unicity_field_id"),
      date_field_id: valueFromConfig(formula, "date_field_id", "date"),
      scope_field_id: valueFromConfig(formula, "scope_field_id"),
      filter_field: valueFromConfig(formula, "filter_field"),
      filter_value: valueFromConfig(formula, "filter_value"),
    });
    setTargets(targetsFromConfig(formula));
    setDisaggregationRows(
      initial?.disaggregations?.length
        ? initial.disaggregations.map((dimension) => ({
            id: dimension.id,
            field_id: dimension.field_id,
            field_label: dimension.field_label,
          }))
        : [{ id: "dimension-1", field_id: "", field_label: "" }]
    );
  }, [open, initial]);

  const stepCompletion = useMemo(() => {
    const checks = [
      Boolean(form.indicator_name && form.indicator_code && form.description && form.reporting_frequency),
      Boolean(form.input_mode && form.record_input_mode && form.progress_relationship),
      form.input_mode === "manual" || form.link_data_source,
      true,
      Boolean(targets[0]?.date),
      true,
    ];
    const done = checks.filter(Boolean).length;
    return { done, total: checks.length, checks };
  }, [form, targets]);

  const inputModeErrors = useMemo(() => validateIndicatorInputMode({
    recordInputMode: form.record_input_mode,
    progressRelationship: form.progress_relationship,
    allowNegativeProgress: form.allow_negative_progress,
  }), [form.allow_negative_progress, form.progress_relationship, form.record_input_mode]);

  const periodPreview = useMemo<IndicatorPeriod[]>(() => {
    const endDate = targets.find((target) => target.date)?.date || form.target_date;
    return generateIndicatorPeriods({
      frequency: form.reporting_frequency,
      startDate: form.baseline_date,
      endDate,
      currentDate: today,
    }).slice(0, 6);
  }, [form.baseline_date, form.reporting_frequency, form.target_date, targets]);

  const activeEnginePreset = useMemo(() => {
    if (form.data_source === "manual") return null;
    return ENGINE_PRESETS[form.data_source];
  }, [form.data_source]);

  const stepValid = useMemo(() => {
    switch (step) {
      case 0: return Boolean(form.indicator_name && form.indicator_code && form.reporting_frequency);
      case 1: return inputModeErrors.length === 0;
      case 2:
        if (form.input_mode === "manual") return true;
        if (!form.link_data_source) return false;
        if (form.input_mode === "automatic" || form.input_mode === "hybrid") {
          return Boolean(form.calculation_source);
        }
        return true;
      case 3: return true;
      case 4: return true;
      default: return true;
    }
  }, [step, form, inputModeErrors]);

  const mutation = useMutation({
    mutationFn: async (): Promise<MEIndicator> => {
      const payload: Partial<MEIndicator> = {
        policy_version: policyVersionId,
        indicator_name: form.indicator_name,
        indicator_code: form.indicator_code,
        description: form.description,
        kpi_type: form.indicator_type,
        unit_of_measurement: form.unit_of_measurement,
        input_mode: form.input_mode,
        record_input_type: form.record_input_mode,
        progress_cumulative_relationship: form.progress_relationship,
        target_direction: form.target_direction,
        visibility_scope: { scope_type: form.visibility_scope },
        calculation_type: calculationTypeFromMethod(form.calculation_method),
        calculation_source: form.calculation_source,
        policy_standard_code: form.policy_standard_code,
        rule_parameter_key: form.rule_parameter_key,
        allow_manual_override: form.input_mode === "hybrid",
        override_requires_reason: form.input_mode === "hybrid" ? form.override_requires_reason : false,
        numerator_definition: ["percentage", "ratio"].includes(form.calculation_method)
          ? { expression: form.numerator.trim() }
          : {},
        denominator_definition: ["percentage", "ratio"].includes(form.calculation_method)
          ? { expression: form.denominator.trim() }
          : {},
        formula_config: {
          indicator_type: form.indicator_type,
          kpi_type: form.indicator_type,
          short_name: form.short_name,
          unit_of_measurement: form.unit_of_measurement,
          input_mode: form.input_mode,
          record_input_mode: form.record_input_mode,
          record_input_type: form.record_input_mode,
          progress_relationship: form.progress_relationship,
          progress_cumulative_relationship: form.progress_relationship,
          target_direction: form.target_direction,
          visibility_scope: form.visibility_scope,
          calculation_type: calculationTypeFromMethod(form.calculation_method),
          calculation_method: form.calculation_method,
          calculation_source: form.calculation_source,
          builder_data_source: form.data_source,
          policy_standard_code: form.policy_standard_code,
          rule_parameter_key: form.rule_parameter_key,
          value_field_id: operationalSource.value_field_id,
          unicity_field_id: operationalSource.unicity_field_id,
          date_field_id: operationalSource.date_field_id,
          scope_field_id: operationalSource.scope_field_id,
          filter_field: operationalSource.filter_field,
          filter_value: operationalSource.filter_value,
          expression: form.formula_expression,
          numerator: form.numerator,
          denominator: form.denominator,
          numerator_definition: ["percentage", "ratio"].includes(form.calculation_method) ? { expression: form.numerator.trim() } : {},
          denominator_definition: ["percentage", "ratio"].includes(form.calculation_method) ? { expression: form.denominator.trim() } : {},
          baseline_value: form.baseline_value,
          baseline_date: form.baseline_date,
          target_value: form.target_value,
          target_date: form.target_date,
          targets,
          link_data_source: form.link_data_source,
          disaggregation: form.disaggregation,
          disaggregation_dimensions: disaggregationRows,
          allow_negative_progress: form.allow_negative_progress,
          allow_manual_override: form.input_mode === "hybrid",
          override_requires_reason: form.input_mode === "hybrid" ? form.override_requires_reason : false,
        },
        data_source: form.input_mode === "manual" ? "manual" : form.data_source,
        reporting_frequency: form.reporting_frequency,
        target_value: form.target_value ? Number(form.target_value) : null,
        threshold_config: {
          green_min: Number(form.threshold_green) || 0,
          amber_min: Number(form.threshold_amber) || 0,
          red_below: Number(form.threshold_amber) || 0,
        },
        visualization_type: form.visualization_type,
        qualitative_config: form.indicator_type === "qualitative" ? {
          input_type: form.qualitative_input_type,
          scale_min: ["likert_scale", "rubric"].includes(form.qualitative_input_type) ? Number(form.qualitative_scale_min) : null,
          scale_max: ["likert_scale", "rubric"].includes(form.qualitative_input_type) ? Number(form.qualitative_scale_max) : null,
          scale_labels_json: Object.fromEntries(
            form.qualitative_scale_labels
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean)
              .map((item) => {
                const [key, ...label] = item.split(":");
                return [key.trim(), label.join(":").trim()];
              })
              .filter(([key, label]) => key && label)
          ),
          category_options_json: form.qualitative_category_options.split(",").map((item) => item.trim()).filter(Boolean),
          requires_narrative: form.qualitative_requires_narrative,
        } : null,
        federal_dashboard_visible: form.federal_dashboard_visible,
        state_dashboard_visible: form.state_dashboard_visible,
        mandatory: form.mandatory,
      };
      if (mode === "edit" && initial?.id) return updateMEIndicator(initial.id, payload);
      const saved = await createMEIndicator(payload);
      if (form.link_data_source && form.data_source !== "manual") {
        await createMEIndicatorDataSource(saved.id, {
          source_type: form.data_source,
          calculation_method: form.calculation_method === "manual" ? "sum" : form.calculation_method,
          value_field_id: operationalSource.value_field_id,
          unicity_field_id: operationalSource.unicity_field_id,
          filter_config_json: {
            date_field_id: operationalSource.date_field_id,
            scope_field_id: operationalSource.scope_field_id,
            filters: operationalSource.filter_field && operationalSource.filter_value ? [{
              field: operationalSource.filter_field,
              operator: "eq",
              value: operationalSource.filter_value,
            }] : [],
          },
        });
      }
      if (form.disaggregation && mode === "create") {
        await Promise.all(disaggregationRows
          .filter((dimension) => dimension.field_id.trim() && dimension.field_label.trim())
          .map((dimension, index) => createMEIndicatorDisaggregation(saved.id, {
            source_type: form.data_source,
            field_id: dimension.field_id.trim(),
            field_label: dimension.field_label.trim(),
            level: index + 1,
          })));
      }
      return saved;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standards-me-indicators"] });
      queryClient.invalidateQueries({ queryKey: ["standards-policy-versions"] });
      onSuccess();
      onClose();
    },
    onError: (err) => setError(getApiErrorMessage(err, "Failed to save KPI.")),
  });

  function update(field: keyof typeof form, value: string | boolean) {
    setForm((prev) => {
      const next = { ...prev, [field]: value };
      if (field === "record_input_mode" && value === "progress_or_cumulative" && next.progress_relationship === "independent") {
        next.progress_relationship = "dependent";
      }
      if (field === "input_mode" && (value === "manual" || value === "imported")) {
        next.data_source = "manual";
        next.link_data_source = false;
        next.calculation_source = "";
        next.policy_standard_code = "";
        next.rule_parameter_key = "";
      }
      if (field === "input_mode" && value === "hybrid") {
        next.override_requires_reason = true;
      }
      if (field === "data_source" && next.calculation_method === "ratio") {
        next.calculation_method = "percentage";
      }
      if (field === "data_source" && value !== "manual") {
        const preset = ENGINE_PRESETS[value as Exclude<BuilderDataSource, "manual">];
        if (preset) {
          next.calculation_source = preset.calculation_source;
          if (!next.policy_standard_code || next.policy_standard_code === prev.policy_standard_code) {
            next.policy_standard_code = preset.policy_standard_code;
          }
          if (!next.rule_parameter_key || next.rule_parameter_key === prev.rule_parameter_key) {
            next.rule_parameter_key = preset.rule_parameter_key;
          }
        }
      }
      if (field === "link_data_source" && value === false) {
        next.calculation_source = "";
        next.policy_standard_code = "";
        next.rule_parameter_key = "";
      }
      return next;
    });
  }

  function updateTarget(id: string, field: keyof TargetRow, value: string) {
    setTargets((current) => current.map((target) => target.id === id ? { ...target, [field]: value } : target));
  }

  function addTarget() {
    setTargets((current) => [
      ...current,
      { id: `target-${Date.now()}`, label: `Target ${current.length + 1}`, value: "", date: "" },
    ]);
  }

  function updateDisaggregationRow(id: string, field: keyof DisaggregationRow, value: string) {
    setDisaggregationRows((current) => current.map((row) => row.id === id ? { ...row, [field]: value } : row));
  }

  function addDisaggregationRow() {
    setDisaggregationRows((current) => [
      ...current,
      { id: `dimension-${Date.now()}`, field_id: "", field_label: "" },
    ]);
  }

  function removeDisaggregationRow(id: string) {
    setDisaggregationRows((current) => current.length > 1 ? current.filter((row) => row.id !== id) : current);
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (inputModeErrors.length) {
      setError(inputModeErrors[0]);
      return;
    }
    mutation.mutate();
  }

  function goNext() {
    setError("");
    if (step < STEPS.length - 1) setStep(step + 1);
  }

  function goBack() {
    setError("");
    if (step > 0) setStep(step - 1);
  }

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/45" onClick={onClose} />
      <div className="fixed inset-x-0 bottom-0 top-10 z-50 mx-auto flex w-[min(1280px,100vw)] flex-col overflow-hidden rounded-t-2xl bg-white shadow-2xl lg:bottom-8 lg:top-8 lg:rounded-2xl">
        <form onSubmit={handleSubmit} className="flex min-h-0 flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-neutral-200 px-5 py-4">
            <div className="flex min-w-0 items-center gap-3">
              <button type="button" onClick={onClose} className="grid h-8 w-8 place-items-center rounded-full text-neutral-600 hover:bg-neutral-100" aria-label="Back">
                <ChevronLeft size={20} />
              </button>
              <div className="min-w-0">
                <h2 className="truncate text-xl font-semibold text-neutral-950">{mode === "edit" ? "Edit KPI" : "Create KPI"}</h2>
                <p className="text-sm text-slate-400">{form.indicator_code || "New KPI"} &mdash; Step {step + 1} of {STEPS.length}</p>
              </div>
            </div>
            <button type="button" onClick={onClose} className="grid h-9 w-9 place-items-center rounded-full bg-neutral-50 text-slate-400 hover:text-neutral-900" aria-label="Close">
              <X size={18} />
            </button>
          </header>

          <div className="border-b border-neutral-200 bg-neutral-50 px-5 py-4">
            <Stepper steps={STEPS} current={step} />
          </div>

          <div className="grid min-h-0 flex-1 lg:grid-cols-[280px_minmax(0,1fr)]">
            <aside className="hidden border-r border-neutral-200 p-5 lg:flex lg:flex-col">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-bold uppercase text-neutral-500">KPI</p>
                  <p className="mt-1 text-sm font-semibold uppercase text-neutral-900 truncate">{form.indicator_name || "Untitled KPI"}</p>
                </div>
                <span className="mt-1 inline-flex shrink-0 items-center gap-1 text-sm font-medium text-blue-600"><span className="h-2.5 w-2.5 rounded-full bg-blue-600" />Draft</span>
              </div>
              <div className="mt-4 border-t border-neutral-100 pt-4">
                <p className="text-xs text-slate-400">Code</p>
                <p className="mt-1 text-sm font-medium text-neutral-900">{form.indicator_code || "Not set"}</p>
              </div>
              <div className="mt-4">
                <p className="text-xs text-slate-400">Description</p>
                <p className="mt-1 text-sm text-neutral-700">{form.description || "No description provided"}</p>
              </div>
              <div className="mt-4 grid grid-cols-2 overflow-hidden rounded-lg border border-neutral-200 bg-neutral-50 text-center">
                {[
                  ["Type", nice(form.indicator_type)],
                  ["Unit", form.unit_of_measurement],
                  ["Frequency", nice(form.reporting_frequency)],
                  ["Input Mode", nice(form.input_mode)],
                  ["Input Type", nice(form.record_input_mode)],
                  ["Relationship", nice(form.progress_relationship)],
                ].map(([label, value]) => (
                  <div className="border-b border-r border-neutral-200 px-3 py-2.5 last:border-r-0" key={label}>
                    <p className="text-xs text-slate-400">{label}</p>
                    <p className="mt-0.5 text-xs font-medium text-neutral-900">{value}</p>
                  </div>
                ))}
              </div>
              {form.indicator_type === "qualitative" ? (
                <div className="mt-4">
                  <p className="text-xs text-slate-400">Input Format</p>
                  <p className="mt-1 text-sm font-medium text-neutral-900">{nice(form.qualitative_input_type)}</p>
                </div>
              ) : null}
              <div className="mt-4">
                <p className="text-xs text-slate-400">Target Direction</p>
                <p className="mt-1 text-sm font-medium text-neutral-900">{formatStatus(form.target_direction)}</p>
              </div>
              <div className="mt-4">
                <p className="text-xs text-slate-400">Visibility</p>
                <p className="mt-1 text-sm font-medium text-neutral-900">{formatStatus(form.visibility_scope)}</p>
              </div>
              <div className="mt-auto border-t border-neutral-100 pt-4">
                <p className="text-xs text-slate-400">Step Completion</p>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-neutral-200">
                  <div className="h-2 rounded-full bg-brand-500 transition-all" style={{ width: `${Math.round((stepCompletion.done / stepCompletion.total) * 100)}%` }} />
                </div>
                <p className="mt-1 text-xs text-neutral-500">{stepCompletion.done} of {stepCompletion.total} steps complete</p>
              </div>
            </aside>

            <main className="min-h-0 overflow-y-auto p-5">
              {error ? <div className="mb-4 rounded bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</div> : null}
              {inputModeErrors.length > 0 && step === 1 ? <div className="mb-4 rounded border border-warning-100 bg-warning-50 px-3 py-2 text-sm font-semibold text-warning-700">{inputModeErrors[0]}</div> : null}

              {/* STEP 1: Basic Details */}
              {step === 0 && (
                <div className="mx-auto max-w-3xl space-y-5">
                  <div>
                    <h3 className="text-base font-semibold text-neutral-950">Basic Details</h3>
                    <p className="mt-1 text-sm text-neutral-500">Define the KPI name, code, type, and reporting structure.</p>
                  </div>

                  <label className="block text-sm font-semibold text-neutral-700">
                    KPI Name <span className="text-danger-500">*</span>
                    <input required className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" placeholder="e.g. Medical Test Coverage Rate" value={form.indicator_name} onChange={(event) => update("indicator_name", event.target.value)} />
                  </label>

                  <label className="block text-sm font-semibold text-neutral-700">
                    KPI Code <span className="text-danger-500">*</span>
                    <input required className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 px-3 font-mono text-sm uppercase outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" placeholder="e.g. FH_TEST_COVERAGE_RATE" value={form.indicator_code} onChange={(event) => update("indicator_code", event.target.value.toUpperCase())} />
                    <p className="mt-1 text-xs text-neutral-400">Unique short code. Use uppercase with underscores.</p>
                  </label>

                  <label className="block text-sm font-semibold text-neutral-700">
                    Short Name
                    <input className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" placeholder="Optional display label" value={form.short_name} onChange={(event) => update("short_name", event.target.value)} />
                  </label>

                  <label className="block text-sm font-semibold text-neutral-700">
                    Description
                    <textarea className="mt-1.5 min-h-24 w-full rounded-md border border-neutral-200 px-3 py-3 text-sm outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100" placeholder="Explain what this KPI measures and why it matters for Food Handlers programme oversight." value={form.description} onChange={(event) => update("description", event.target.value)} />
                  </label>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <label className="block text-sm font-semibold text-neutral-700">
                      KPI Type
                      <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.indicator_type} onChange={(event) => update("indicator_type", event.target.value)}>
                        <option value="quantitative">Quantitative (numeric)</option>
                        <option value="qualitative">Qualitative (descriptive / rating)</option>
                      </select>
                    </label>
                    <label className="block text-sm font-semibold text-neutral-700">
                      Unit of Measurement
                      <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.unit_of_measurement} onChange={(event) => update("unit_of_measurement", event.target.value)}>
                        {UNITS.map((unit) => <option key={unit} value={unit}>{unit}</option>)}
                      </select>
                    </label>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <label className="block text-sm font-semibold text-neutral-700">
                      Reporting Frequency <span className="text-danger-500">*</span>
                      <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.reporting_frequency} onChange={(event) => update("reporting_frequency", event.target.value)}>
                        {FREQUENCIES.map((frequency) => <option key={frequency} value={frequency}>{nice(frequency)}</option>)}
                      </select>
                    </label>
                    <label className="block text-sm font-semibold text-neutral-700">
                      Visibility Scope
                      <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.visibility_scope} onChange={(event) => update("visibility_scope", event.target.value)}>
                        <option value="federal_only">Federal only</option>
                        <option value="federal_and_state">Federal and state</option>
                        <option value="public_dashboard">Public dashboard</option>
                      </select>
                    </label>
                  </div>

                  <label className="inline-flex items-center gap-3 text-sm font-semibold text-neutral-700">
                    <input className="h-5 w-5 accent-brand-600" checked={form.mandatory} onChange={(event) => update("mandatory", event.target.checked)} type="checkbox" />
                    Mandatory reporting for all jurisdictions
                  </label>
                </div>
              )}

              {/* STEP 2: Input Mode */}
              {step === 1 && (
                <div className="mx-auto max-w-3xl space-y-5">
                  <div>
                    <h3 className="text-base font-semibold text-neutral-950">Input Mode &amp; Record Type</h3>
                    <p className="mt-1 text-sm text-neutral-500">Define how KPI values are entered and how progress relates to cumulative totals.</p>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-3">
                    <label className="block text-sm font-semibold text-neutral-700">
                      Input Mode
                      <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.input_mode} onChange={(event) => update("input_mode", event.target.value)}>
                        <option value="automatic">Automatic</option>
                        <option value="manual">Manual</option>
                        <option value="imported">Imported</option>
                        <option value="hybrid">Hybrid</option>
                      </select>
                    </label>
                    <label className="block text-sm font-semibold text-neutral-700">
                      Target Direction
                      <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.target_direction} onChange={(event) => update("target_direction", event.target.value)}>
                        <option value="higher_better">Higher is better</option>
                        <option value="lower_better">Lower is better</option>
                        <option value="exact">Exact target</option>
                        <option value="range">Target range</option>
                      </select>
                    </label>
                    <label className="block text-sm font-semibold text-neutral-700">
                      Visualization
                      <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.visualization_type} onChange={(event) => update("visualization_type", event.target.value)}>
                        {VISUALIZATIONS.map((type) => <option key={type} value={type}>{nice(type)}</option>)}
                      </select>
                    </label>
                  </div>

                  {form.input_mode === "hybrid" ? (
                    <div className="rounded-lg border border-warning-200 bg-warning-50 p-4">
                      <h4 className="text-sm font-semibold text-warning-900">Hybrid KPI workflow</h4>
                      <p className="mt-1 text-sm text-warning-800">This KPI will auto-calculate from operational records, but federal users can override a reporting period value when necessary.</p>
                      <label className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-warning-900">
                        <input type="checkbox" checked={form.override_requires_reason} onChange={(event) => update("override_requires_reason", event.target.checked)} className="h-4 w-4 accent-brand-600" />
                        Require a reason whenever an override is applied
                      </label>
                    </div>
                  ) : null}

                  {form.indicator_type === "qualitative" ? (
                    <div className="rounded-lg border border-neutral-200 bg-white p-5">
                      <h4 className="text-sm font-semibold text-neutral-950">Qualitative Input Configuration</h4>
                      <div className="mt-4 grid gap-4 sm:grid-cols-2">
                        <label className="block text-sm font-semibold text-neutral-700">
                          Input Format
                          <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.qualitative_input_type} onChange={(event) => update("qualitative_input_type", event.target.value)}>
                            <option value="text">Narrative text</option>
                            <option value="likert_scale">Rating scale</option>
                            <option value="category">Dropdown category</option>
                            <option value="rubric">Rubric</option>
                          </select>
                        </label>
                        <label className="inline-flex items-center gap-3 pt-7 text-sm font-medium text-neutral-700">
                          <input className="h-5 w-5 accent-brand-600" checked={form.qualitative_requires_narrative} onChange={(event) => update("qualitative_requires_narrative", event.target.checked)} type="checkbox" />
                          Narrative required
                        </label>
                      </div>
                      {["likert_scale", "rubric"].includes(form.qualitative_input_type) ? (
                        <div className="mt-3 grid gap-3 sm:grid-cols-3">
                          <input className="h-11 rounded-md border border-neutral-200 px-3 text-sm" placeholder="Scale min" value={form.qualitative_scale_min} onChange={(event) => update("qualitative_scale_min", event.target.value)} />
                          <input className="h-11 rounded-md border border-neutral-200 px-3 text-sm" placeholder="Scale max" value={form.qualitative_scale_max} onChange={(event) => update("qualitative_scale_max", event.target.value)} />
                          <input className="h-11 rounded-md border border-neutral-200 px-3 text-sm" placeholder="Labels, e.g. 1:Low, 5:High" value={form.qualitative_scale_labels} onChange={(event) => update("qualitative_scale_labels", event.target.value)} />
                        </div>
                      ) : null}
                      {["category", "rubric"].includes(form.qualitative_input_type) ? (
                        <input className="mt-3 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="Category options, comma separated" value={form.qualitative_category_options} onChange={(event) => update("qualitative_category_options", event.target.value)} />
                      ) : null}
                    </div>
                  ) : null}

                  <div className="rounded-lg border border-neutral-200 bg-white p-5">
                    <h4 className="text-sm font-semibold text-neutral-950">Record Input Configuration</h4>
                    <div className="mt-4 grid gap-4 sm:grid-cols-2">
                      <label className="block text-sm font-semibold text-neutral-700">
                        Input Type
                        <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.record_input_mode} onChange={(event) => update("record_input_mode", event.target.value)}>
                          <option value="progress_only">Progress Only</option>
                          <option value="cumulative_only">Cumulative Only</option>
                          <option value="progress_or_cumulative">Progress or Cumulative</option>
                        </select>
                      </label>
                      <label className="block text-sm font-semibold text-neutral-700">
                        Relationship
                        <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.progress_relationship} onChange={(event) => update("progress_relationship", event.target.value)}>
                          <option value="dependent">Dependent</option>
                          <option value="same">Same</option>
                          <option value="independent" disabled={form.record_input_mode === "progress_or_cumulative"}>Independent</option>
                        </select>
                      </label>
                    </div>
                    <div className="mt-4 rounded-md bg-neutral-50 px-4 py-3 text-sm text-neutral-600">
                      {form.record_input_mode === "progress_only" && (
                        <p><span className="font-semibold">Progress Only:</span> Users enter progress values for each reporting period. Cumulative values are derived based on the selected relationship.</p>
                      )}
                      {form.record_input_mode === "cumulative_only" && (
                        <p><span className="font-semibold">Cumulative Only:</span> Users enter cumulative totals for each period. Progress values are derived from the difference with the previous period.</p>
                      )}
                      {form.record_input_mode === "progress_or_cumulative" && (
                        <p><span className="font-semibold">Progress or Cumulative:</span> Users may enter either value. The engine derives the other where possible. Independent relationship is unavailable in this mode.</p>
                      )}
                    </div>
                    {form.record_input_mode === "progress_or_cumulative" && (
                      <label className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-neutral-700">
                        <input type="checkbox" checked={form.allow_negative_progress} onChange={(event) => update("allow_negative_progress", event.target.checked)} />
                        Allow reversals / corrections (negative period values)
                      </label>
                    )}
                  </div>

                  <div className="rounded-lg border border-neutral-200 bg-white p-5">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <h4 className="text-sm font-semibold text-neutral-950">Reporting Period Preview</h4>
                        <p className="mt-1 text-xs text-neutral-500">Generated from baseline date, reporting frequency, and target end date.</p>
                      </div>
                    </div>
                    <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                      {periodPreview.length ? periodPreview.map((period) => (
                        <div className="rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2" key={`${period.startDate}-${period.endDate}`}>
                          <div className="flex items-center justify-between gap-2">
                            <p className="text-sm font-semibold text-neutral-900">{period.label}</p>
                            <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ${
                              period.status === "current" ? "bg-brand-50 text-brand-700" :
                              period.status === "future" ? "bg-warning-50 text-warning-700" :
                              "bg-neutral-100 text-neutral-500"
                            }`}>{period.status}</span>
                          </div>
                          <p className="mt-1 text-xs text-neutral-500">{period.startDate} to {period.endDate}</p>
                        </div>
                      )) : (
                        <p className="text-sm text-neutral-500">Set valid baseline and target dates in Step 5 to preview reporting periods.</p>
                      )}
                    </div>
                  </div>

                  <div className="rounded-lg border border-neutral-200 bg-white p-5">
                    <h4 className="text-sm font-semibold text-neutral-950">Dashboard Visibility</h4>
                    <div className="mt-3 grid gap-3 sm:grid-cols-2">
                      <label className="inline-flex items-center gap-2 text-sm font-medium text-neutral-700">
                        <input type="checkbox" checked={form.federal_dashboard_visible} onChange={(event) => update("federal_dashboard_visible", event.target.checked)} className="h-5 w-5 accent-brand-600" />
                        Federal dashboard
                      </label>
                      <label className="inline-flex items-center gap-2 text-sm font-medium text-neutral-700">
                        <input type="checkbox" checked={form.state_dashboard_visible} onChange={(event) => update("state_dashboard_visible", event.target.checked)} className="h-5 w-5 accent-brand-600" />
                        State dashboard
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 3: Data Source and Calculation */}
              {step === 2 && (
                <div className="mx-auto max-w-3xl space-y-5">
                  <div>
                    <h3 className="text-base font-semibold text-neutral-950">Data Source &amp; Calculation</h3>
                    <p className="mt-1 text-sm text-neutral-500">Link the KPI to a Food Handlers operational data source or to other KPIs for formula calculations.</p>
                  </div>

                  {form.input_mode === "manual" ? (
                    <div className="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-8 text-center">
                      <p className="text-sm font-semibold text-neutral-700">Manual KPI</p>
                      <p className="mt-2 text-sm text-neutral-500">This KPI uses manual data entry only. Switch Input Mode to Automatic or Hybrid in Step 2 to link a data source.</p>
                    </div>
                  ) : form.input_mode === "imported" ? (
                    <div className="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-8 text-center">
                      <p className="text-sm font-semibold text-neutral-700">Imported KPI</p>
                      <p className="mt-2 text-sm text-neutral-500">This KPI is populated through CSV or historical imports. Automatic source linking is optional and usually not required.</p>
                    </div>
                  ) : (
                    <>
                      <label className="flex items-center gap-4 text-sm font-semibold text-neutral-700">
                        <input className="h-5 w-5 accent-brand-600" checked={form.link_data_source} onChange={(event) => update("link_data_source", event.target.checked)} type="checkbox" />
                        Link Food Handlers data source
                      </label>

                      {form.link_data_source ? (
                        <div className="space-y-5 rounded-lg border border-neutral-200 bg-white p-5">
                          <div className="grid gap-4 sm:grid-cols-3">
                            <label className="block text-sm font-semibold text-neutral-700">
                              Data Source
                              <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.data_source} onChange={(event) => update("data_source", event.target.value)}>
                                {DATA_SOURCES.map((source) => <option key={source} value={source}>{nice(source)}</option>)}
                              </select>
                            </label>
                            <label className="block text-sm font-semibold text-neutral-700">
                              Calculation Method
                              <select className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 bg-white px-3 text-sm" value={form.calculation_method} onChange={(event) => update("calculation_method", event.target.value)}>
                                <option value="manual">Manual</option>
                                <option value="sum">Sum</option>
                                <option value="average">Average</option>
                                <option value="count">Count</option>
                                <option value="unique_count">Unique Count</option>
                                <option value="percentage">Percentage</option>
                                <option value="formula">Formula</option>
                              </select>
                            </label>
                            <label className="block text-sm font-semibold text-neutral-700">
                              Formula Expression
                              <input className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 px-3 font-mono text-sm" placeholder="e.g. A / B * 100" value={form.formula_expression} onChange={(event) => update("formula_expression", event.target.value)} />
                            </label>
                          </div>

                          <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-4">
                            <div className="grid gap-4 sm:grid-cols-3">
                              <label className="block text-sm font-semibold text-neutral-700">
                                Engine source
                                <input
                                  className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm"
                                  placeholder="e.g. certificates"
                                  value={form.calculation_source}
                                  onChange={(event) => update("calculation_source", event.target.value)}
                                />
                              </label>
                              <label className="block text-sm font-semibold text-neutral-700">
                                Policy standard code
                                <input
                                  className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 px-3 font-mono text-sm"
                                  placeholder="e.g. FH-VALIDITY-2024-001"
                                  value={form.policy_standard_code}
                                  onChange={(event) => update("policy_standard_code", event.target.value)}
                                />
                              </label>
                              <label className="block text-sm font-semibold text-neutral-700">
                                Rule parameter key
                                <input
                                  className="mt-1.5 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm"
                                  placeholder="e.g. certificate_validity_months"
                                  value={form.rule_parameter_key}
                                  onChange={(event) => update("rule_parameter_key", event.target.value)}
                                />
                              </label>
                            </div>
                            <p className="mt-3 text-xs text-neutral-500">
                              {activeEnginePreset?.helper || "Use these fields to bind the KPI to an active federal policy rule and to the automatic KPI engine."}
                            </p>
                            <p className="mt-1 text-xs text-neutral-500">
                              Automatic and hybrid KPIs must use a Food Handlers operational source. KPI-to-KPI dependency is not available in this workflow.
                            </p>
                          </div>

                          <div className="space-y-4 rounded-lg border border-brand-100 bg-brand-50/30 p-5">
                            <p className="text-sm font-semibold text-brand-800">Operational Data Source Fields</p>
                            <div className="grid gap-4 sm:grid-cols-2">
                              <label className="block text-sm font-medium text-neutral-700">
                                Value field key
                                <input className="mt-1 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="e.g. completed_tests" value={operationalSource.value_field_id} onChange={(event) => setOperationalSource((current) => ({ ...current, value_field_id: event.target.value }))} />
                              </label>
                              <label className="block text-sm font-medium text-neutral-700">
                                Unicity field key
                                <input className="mt-1 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="e.g. handler_id" value={operationalSource.unicity_field_id} onChange={(event) => setOperationalSource((current) => ({ ...current, unicity_field_id: event.target.value }))} />
                              </label>
                              <label className="block text-sm font-medium text-neutral-700">
                                Date field key
                                <input className="mt-1 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="e.g. issued_at" value={operationalSource.date_field_id} onChange={(event) => setOperationalSource((current) => ({ ...current, date_field_id: event.target.value }))} />
                              </label>
                              <label className="block text-sm font-medium text-neutral-700">
                                Scope field key
                                <input className="mt-1 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="e.g. state_code" value={operationalSource.scope_field_id} onChange={(event) => setOperationalSource((current) => ({ ...current, scope_field_id: event.target.value }))} />
                              </label>
                            </div>
                            <div className="grid gap-4 sm:grid-cols-2">
                              <label className="block text-sm font-medium text-neutral-700">
                                Filter field
                                <input className="mt-1 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="Field to filter by" value={operationalSource.filter_field} onChange={(event) => setOperationalSource((current) => ({ ...current, filter_field: event.target.value }))} />
                              </label>
                              <label className="block text-sm font-medium text-neutral-700">
                                Filter value
                                <input className="mt-1 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="Expected value" value={operationalSource.filter_value} onChange={(event) => setOperationalSource((current) => ({ ...current, filter_value: event.target.value }))} />
                              </label>
                            </div>
                            {["percentage", "ratio"].includes(form.calculation_method) ? (
                              <div className="grid gap-4 sm:grid-cols-2">
                                <label className="block text-sm font-medium text-neutral-700">
                                  Numerator
                                  <input className="mt-1 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="Numerator expression or field" value={form.numerator} onChange={(event) => update("numerator", event.target.value)} />
                                </label>
                                <label className="block text-sm font-medium text-neutral-700">
                                  Denominator
                                  <input className="mt-1 h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="Denominator expression or field" value={form.denominator} onChange={(event) => update("denominator", event.target.value)} />
                                </label>
                              </div>
                            ) : null}
                            <p className="text-xs text-neutral-500">Use field keys from Food Handler operational records (e.g. handler_id, certificate_status, facility_state, test_result).</p>
                          </div>
                        </div>
                      ) : (
                        <div className="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-8 text-center">
                          <p className="text-sm font-semibold text-neutral-700">No data source linked</p>
                          <p className="mt-2 text-sm text-neutral-500">Check the box above to link a Food Handlers operational data source or KPI dependency.</p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* STEP 4: Disaggregation */}
              {step === 3 && (
                <div className="mx-auto max-w-3xl space-y-5">
                  <div>
                    <h3 className="text-base font-semibold text-neutral-950">Disaggregation</h3>
                    <p className="mt-1 text-sm text-neutral-500">Break down KPI values by demographic, geographic, or operational dimensions for deeper analysis.</p>
                  </div>

                  <label className="flex items-center gap-4 text-sm font-semibold text-neutral-700">
                    <input className="h-5 w-5 accent-brand-600" checked={form.disaggregation} onChange={(event) => update("disaggregation", event.target.checked)} type="checkbox" />
                    Enable disaggregation
                  </label>

                  {form.disaggregation ? (
                    <div className="rounded-lg border border-neutral-200 bg-white p-5">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <h4 className="text-sm font-semibold text-neutral-950">Disaggregation Dimensions</h4>
                          <p className="mt-1 text-xs text-neutral-500">Use field keys from the linked source records (e.g. gender, state, region, age_group).</p>
                        </div>
                        <button type="button" onClick={addDisaggregationRow} className="inline-flex items-center gap-2 text-sm font-semibold text-brand-700"><Plus size={16} />Add dimension</button>
                      </div>
                      <div className="mt-4 space-y-2">
                        {disaggregationRows.map((dimension, index) => (
                          <div className="grid gap-2 sm:grid-cols-[80px_minmax(0,1fr)_minmax(0,1fr)_44px]" key={dimension.id}>
                            <div className="grid h-11 place-items-center rounded-md bg-neutral-50 text-sm font-semibold text-neutral-500">L{index + 1}</div>
                            <input className="h-11 rounded-md border border-neutral-200 px-3 text-sm" placeholder="Field key (e.g. state)" value={dimension.field_id} onChange={(event) => updateDisaggregationRow(dimension.id, "field_id", event.target.value)} />
                            <input className="h-11 rounded-md border border-neutral-200 px-3 text-sm" placeholder="Display label (e.g. State)" value={dimension.field_label} onChange={(event) => updateDisaggregationRow(dimension.id, "field_label", event.target.value)} />
                            <button type="button" onClick={() => removeDisaggregationRow(dimension.id)} className="grid h-11 place-items-center rounded-md border border-neutral-200 text-neutral-500 hover:bg-neutral-50" aria-label="Remove dimension">
                              <X size={16} />
                            </button>
                          </div>
                        ))}
                      </div>
                      {mode === "edit" ? <p className="mt-4 text-xs text-warning-700">Existing dimensions are shown for reference. Dimension editing will be managed from the indicator detail workspace.</p> : null}

                      <div className="mt-5 rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-4">
                        <h4 className="text-sm font-semibold text-neutral-950">Suggested Dimensions</h4>
                        <div className="mt-3 grid gap-2 sm:grid-cols-2">
                          {[
                            ["Geography", "state, lga, ward, location"],
                            ["Facility", "facility_type, business_category"],
                            ["Person", "gender, age_group, occupation"],
                            ["Testing", "test_type, test_status, result"],
                            ["Certification", "certificate_status, expiry_status"],
                            ["Operations", "registration_channel, approval_status"],
                          ].map(([category, fields]) => (
                            <div key={category} className="rounded-md border border-neutral-200 bg-white px-3 py-2">
                              <p className="text-xs font-semibold text-neutral-700">{category}</p>
                              <p className="mt-0.5 text-xs text-neutral-500">{fields}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-8 text-center">
                      <p className="text-sm font-semibold text-neutral-700">No disaggregation configured</p>
                      <p className="mt-2 text-sm text-neutral-500">Enable disaggregation to break down KPI values by key operational dimensions for deeper insights.</p>
                    </div>
                  )}
                </div>
              )}

              {/* STEP 5: Targets and Thresholds */}
              {step === 4 && (
                <div className="mx-auto max-w-3xl space-y-5">
                  <div>
                    <h3 className="text-base font-semibold text-neutral-950">Targets &amp; Thresholds</h3>
                    <p className="mt-1 text-sm text-neutral-500">Define performance targets and threshold ranges for on-track, watch, and off-track status evaluation.</p>
                  </div>

                  <div className="rounded-lg border border-neutral-200 bg-white p-5">
                    <h4 className="text-sm font-semibold text-neutral-950">Baseline &amp; Target(s)</h4>
                    <div className="mt-4 overflow-hidden rounded-md border border-neutral-200">
                      <div className="grid grid-cols-[minmax(120px,1fr)_minmax(120px,180px)_minmax(150px,220px)] bg-neutral-50 px-3 py-2 text-xs font-medium text-slate-400">
                        <span />
                        <span>Target</span>
                        <span>Date</span>
                      </div>
                      <div className="grid grid-cols-[minmax(120px,1fr)_minmax(120px,180px)_minmax(150px,220px)] items-center gap-2 px-3 py-3">
                        <span className="text-sm font-medium text-neutral-900">Baseline</span>
                        <input className="h-9 rounded border border-neutral-200 px-3 text-sm" placeholder="Starting value" value={form.baseline_value} onChange={(event) => update("baseline_value", event.target.value)} />
                        <div className="relative">
                          <input className="h-9 w-full rounded border border-neutral-200 px-3 pr-9 text-sm" type="date" value={form.baseline_date} onChange={(event) => update("baseline_date", event.target.value)} />
                          <Calendar className="pointer-events-none absolute right-3 top-2.5 text-slate-400" size={15} />
                        </div>
                      </div>
                      {targets.map((target) => (
                        <div className="grid grid-cols-[minmax(120px,1fr)_minmax(120px,180px)_minmax(150px,220px)] items-center gap-2 px-3 py-2" key={target.id}>
                          <input className="h-9 rounded border border-transparent px-0 text-sm font-medium text-neutral-900 outline-none focus:border-neutral-200 focus:px-3" value={target.label} onChange={(event) => updateTarget(target.id, "label", event.target.value)} />
                          <input className="h-9 rounded border border-neutral-200 px-3 text-sm" placeholder="Target value" value={target.value} onChange={(event) => { updateTarget(target.id, "value", event.target.value); if (target.id === targets[0]?.id) update("target_value", event.target.value); }} />
                          <div className="relative">
                            <input className="h-9 w-full rounded border border-neutral-200 px-3 pr-9 text-sm" type="date" value={target.date} onChange={(event) => { updateTarget(target.id, "date", event.target.value); if (target.id === targets[0]?.id) update("target_date", event.target.value); }} />
                            <Calendar className="pointer-events-none absolute right-3 top-2.5 text-slate-400" size={15} />
                          </div>
                        </div>
                      ))}
                      <div className="flex justify-end px-3 py-3">
                        <button type="button" onClick={addTarget} className="inline-flex items-center gap-2 text-sm font-semibold text-brand-700"><Plus size={16} />Add target</button>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-lg border border-neutral-200 bg-white p-5">
                    <h4 className="text-sm font-semibold text-neutral-950">Performance Thresholds</h4>
                    <p className="mt-1 text-xs text-neutral-500">Set green (on-track), amber (watch), and red (off-track) boundaries. Values below the amber threshold are considered off-track.</p>
                    <div className="mt-4 grid gap-4 sm:grid-cols-2">
                      <label className="block text-sm font-semibold text-neutral-700">
                        <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-brand-500" />Green (on-track) at or above</span>
                        <div className="mt-1.5 flex items-center gap-2">
                          <input className="h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="80" value={form.threshold_green} onChange={(event) => update("threshold_green", event.target.value)} />
                          <span className="text-sm text-neutral-500">%</span>
                        </div>
                      </label>
                      <label className="block text-sm font-semibold text-neutral-700">
                        <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-warning-500" />Amber (watch) at or above</span>
                        <div className="mt-1.5 flex items-center gap-2">
                          <input className="h-11 w-full rounded-md border border-neutral-200 px-3 text-sm" placeholder="60" value={form.threshold_amber} onChange={(event) => update("threshold_amber", event.target.value)} />
                          <span className="text-sm text-neutral-500">%</span>
                        </div>
                      </label>
                    </div>
                    <div className="mt-4 grid grid-cols-3 gap-2 rounded-md bg-neutral-50 p-3 text-center text-xs">
                      <div className="rounded bg-danger-50 px-2 py-1.5 font-semibold text-danger-700">Off Track &lt; {form.threshold_amber || "?"}%</div>
                      <div className="rounded bg-warning-50 px-2 py-1.5 font-semibold text-warning-700">Watch {form.threshold_amber || "?"}–{form.threshold_green || "?"}%</div>
                      <div className="rounded bg-brand-50 px-2 py-1.5 font-semibold text-brand-700">On Track &ge; {form.threshold_green || "?"}%</div>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 6: Review and Activate */}
              {step === 5 && (
                <div className="mx-auto max-w-3xl space-y-5">
                  <div>
                    <h3 className="text-base font-semibold text-neutral-950">Review &amp; Activate</h3>
                    <p className="mt-1 text-sm text-neutral-500">Review the complete KPI configuration before saving or activating.</p>
                  </div>

                  {!stepValid && stepCompletion.done < 5 ? (
                    <div className="rounded-lg border border-warning-100 bg-warning-50 p-4 text-sm text-warning-700">
                      <span className="font-semibold">Incomplete configuration:</span> {stepCompletion.done} of {stepCompletion.total} sections complete. Go back to complete missing fields before activating.
                    </div>
                  ) : null}

                  <div className="rounded-lg border border-neutral-200 bg-white">
                    <div className="border-b border-neutral-200 bg-neutral-50 px-5 py-3">
                      <h4 className="text-sm font-semibold text-neutral-950">Configuration Summary</h4>
                    </div>
                    <div className="divide-y divide-neutral-100">
                      <div className="grid gap-2 px-5 py-4 sm:grid-cols-[180px_minmax(0,1fr)]">
                        <span className="text-sm font-semibold text-neutral-500">Basic Details</span>
                        <div className="space-y-1 text-sm">
                          <p><span className="font-medium text-neutral-700">Name:</span> {form.indicator_name || <span className="text-neutral-400">Not set</span>}</p>
                          <p><span className="font-medium text-neutral-700">Code:</span> <code className="text-brand-700">{form.indicator_code || "—"}</code></p>
                          <p><span className="font-medium text-neutral-700">Type:</span> {nice(form.indicator_type)}</p>
                          <p><span className="font-medium text-neutral-700">Unit:</span> {form.unit_of_measurement}</p>
                          <p><span className="font-medium text-neutral-700">Frequency:</span> {nice(form.reporting_frequency)}</p>
                          <p><span className="font-medium text-neutral-700">Visibility:</span> {formatStatus(form.visibility_scope)}</p>
                        </div>
                      </div>
                      <div className="grid gap-2 px-5 py-4 sm:grid-cols-[180px_minmax(0,1fr)]">
                        <span className="text-sm font-semibold text-neutral-500">Input Mode</span>
                        <div className="space-y-1 text-sm">
                          <p><span className="font-medium text-neutral-700">Mode:</span> {nice(form.input_mode)}</p>
                          <p><span className="font-medium text-neutral-700">Input Type:</span> {nice(form.record_input_mode)}</p>
                          <p><span className="font-medium text-neutral-700">Relationship:</span> {nice(form.progress_relationship)}</p>
                          <p><span className="font-medium text-neutral-700">Target Direction:</span> {formatStatus(form.target_direction)}</p>
                          {form.input_mode === "hybrid" ? <p><span className="font-medium text-neutral-700">Override reason required:</span> {form.override_requires_reason ? "Yes" : "No"}</p> : null}
                          {form.indicator_type === "qualitative" ? <p><span className="font-medium text-neutral-700">Format:</span> {nice(form.qualitative_input_type)}</p> : null}
                        </div>
                      </div>
                      <div className="grid gap-2 px-5 py-4 sm:grid-cols-[180px_minmax(0,1fr)]">
                        <span className="text-sm font-semibold text-neutral-500">Data Source</span>
                        <div className="space-y-1 text-sm">
                          {form.link_data_source ? (
                            <>
                              <p><span className="font-medium text-neutral-700">Source:</span> {nice(form.data_source)}</p>
                              <p><span className="font-medium text-neutral-700">Method:</span> {nice(form.calculation_method)}</p>
                              {form.calculation_source ? <p><span className="font-medium text-neutral-700">Engine source:</span> {form.calculation_source}</p> : null}
                              {form.policy_standard_code ? <p><span className="font-medium text-neutral-700">Policy standard:</span> {form.policy_standard_code}</p> : null}
                              {form.rule_parameter_key ? <p><span className="font-medium text-neutral-700">Rule parameter:</span> {form.rule_parameter_key}</p> : null}
                              {form.data_source !== "manual" && operationalSource.value_field_id ? <p><span className="font-medium text-neutral-700">Value field:</span> {operationalSource.value_field_id}</p> : null}
                            </>
                          ) : (
                            <p className="text-neutral-400">No data source linked (manual entry)</p>
                          )}
                        </div>
                      </div>
                      <div className="grid gap-2 px-5 py-4 sm:grid-cols-[180px_minmax(0,1fr)]">
                        <span className="text-sm font-semibold text-neutral-500">Disaggregation</span>
                        <div className="space-y-1 text-sm">
                          {form.disaggregation ? (
                            <p>{disaggregationRows.filter((d) => d.field_id).length} dimension(s) configured</p>
                          ) : (
                            <p className="text-neutral-400">Not enabled</p>
                          )}
                        </div>
                      </div>
                      <div className="grid gap-2 px-5 py-4 sm:grid-cols-[180px_minmax(0,1fr)]">
                        <span className="text-sm font-semibold text-neutral-500">Targets</span>
                        <div className="space-y-1 text-sm">
                          <p><span className="font-medium text-neutral-700">Baseline:</span> {form.baseline_value} ({form.baseline_date})</p>
                          {targets.filter((t) => t.value).map((t) => (
                            <p key={t.id}><span className="font-medium text-neutral-700">{t.label}:</span> {t.value} by {t.date}</p>
                          ))}
                          {!targets.some((t) => t.value) ? <p className="text-neutral-400">No targets set</p> : null}
                        </div>
                      </div>
                      <div className="grid gap-2 px-5 py-4 sm:grid-cols-[180px_minmax(0,1fr)]">
                        <span className="text-sm font-semibold text-neutral-500">Thresholds</span>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="inline-flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-brand-500" /> Green &ge; {form.threshold_green}%</span>
                          <span className="inline-flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-warning-500" /> Amber &ge; {form.threshold_amber}%</span>
                          <span className="inline-flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-danger-500" /> Red &lt; {form.threshold_amber}%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {form.description ? (
                    <div className="rounded-lg border border-neutral-200 bg-white p-5">
                      <h4 className="text-sm font-semibold text-neutral-950">Description</h4>
                      <p className="mt-2 text-sm text-neutral-700">{form.description}</p>
                    </div>
                  ) : null}
                </div>
              )}
            </main>
          </div>

          <footer className="flex items-center justify-between gap-3 border-t border-neutral-200 px-5 py-4">
            <button type="button" onClick={onClose} className="h-10 rounded-full border border-neutral-200 px-6 text-sm font-medium text-neutral-700 hover:bg-neutral-50">
              Cancel
            </button>
            <div className="flex items-center gap-3">
              {step > 0 && (
                <button type="button" onClick={goBack} className="inline-flex h-10 items-center gap-1.5 rounded-full border border-neutral-200 px-5 text-sm font-medium text-neutral-700 hover:bg-neutral-50">
                  <ChevronLeft size={16} /> Back
                </button>
              )}
              {step < STEPS.length - 1 ? (
                <button type="button" onClick={goNext} disabled={!stepValid} className="inline-flex h-10 items-center gap-1.5 rounded-full bg-brand-600 px-5 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50">
                  Next <ChevronRight size={16} />
                </button>
              ) : (
                <button
                  disabled={mutation.isPending || !form.indicator_name || !form.indicator_code || inputModeErrors.length > 0}
                  type="submit"
                  className="h-10 rounded-full bg-brand-600 px-6 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60"
                >
                  {mutation.isPending ? "Saving..." : mode === "edit" ? "Save Changes" : "Save KPI"}
                </button>
              )}
            </div>
          </footer>
        </form>
      </div>
    </>
  );
}
