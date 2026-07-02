export type KpiCardAggregation = "count" | "sum" | "avg" | "latest";
export type KpiCardFormat = "number" | "percent" | "currency";
export type KpiCardSourceType = "dataset" | "snapshot";
export type KpiCardStatus = "good" | "warning" | "critical" | null;

export type KpiCardFilter = { field: string; operator: string; value: unknown };

export type KpiCardTrendConfig = {
  compare_to?: "prev_period";
  window?: "7d" | "30d" | "90d" | "365d";
  date_field?: string;
};

export type KpiCardTargetConfig = {
  operator?: "gt" | "gte" | "lt" | "lte";
  warning?: number;
  critical?: number;
};

/** A KPI card described as data, not JSX. */
export type KpiCard = {
  id: string;
  code: string;
  title: string;
  description: string;
  category: string;
  icon: string;
  source_type: KpiCardSourceType;
  dataset_code: string;
  metric: string;
  aggregation: KpiCardAggregation;
  filters: KpiCardFilter[];
  snapshot_key: string;
  format: KpiCardFormat;
  trend: KpiCardTrendConfig;
  target: KpiCardTargetConfig;
  detail: string;
  allowed_account_types: string[];
  is_system: boolean;
  is_active: boolean;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
};

export type KpiCardResolved = {
  value: number | string | null;
  formatted: string;
  trend: {
    delta: number;
    direction: "up" | "down" | "flat";
    label: string;
    current: number;
    previous: number;
  } | null;
  status: KpiCardStatus;
};

export type KpiCardDraftConfig = Partial<KpiCard> & { requires_review?: boolean };
