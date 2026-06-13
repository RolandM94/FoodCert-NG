import type { KoboQuestion, KoboSchema } from "@/components/forms/kobo-form-renderer";
import { evaluateKoboLogic, type KoboLogic } from "@/lib/forms/kobo-logic";

export type KoboValidationError = {
  key: string;
  label: string;
  message: string;
};

function blank(value: unknown) {
  if (value === null || value === undefined) return true;
  if (typeof value === "string") return value.trim() === "";
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") return Object.keys(value as Record<string, unknown>).length === 0;
  return false;
}

function numberValue(value: unknown) {
  if (value === "" || value === null || value === undefined) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function fieldError(question: KoboQuestion, message: string): KoboValidationError {
  const validation = question.validation || {};
  return {
    key: question.key,
    label: question.label || question.key,
    message: typeof validation.message === "string" ? validation.message : message,
  };
}

function csvRule(value: unknown) {
  if (typeof value === "string") return value.split(",").map((item) => item.trim().toLowerCase().replace(/^\./, "")).filter(Boolean);
  if (Array.isArray(value)) return value.map((item) => String(item).trim().toLowerCase().replace(/^\./, "")).filter(Boolean);
  return [];
}

function mediaMetadata(item: unknown) {
  if (item && typeof item === "object") {
    const record = item as Record<string, unknown>;
    return {
      fileName: String(record.file_name || record.name || ""),
      mimeType: String(record.mime_type || record.type || ""),
      fileSize: typeof record.file_size === "number" ? record.file_size : typeof record.size === "number" ? record.size : null,
    };
  }
  return { fileName: String(item || ""), mimeType: "", fileSize: null };
}

function extensionFor(fileName: string) {
  const parts = fileName.split(".");
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : "";
}

export function validateQuestion(question: KoboQuestion, value: unknown): KoboValidationError[] {
  const errors: KoboValidationError[] = [];
  const validation = question.validation || {};

  if (["instruction", "section_header", "hidden", "calculated_field", "calculated_number"].includes(question.type)) return errors;
  if (question.required && blank(value)) return [fieldError(question, "This field is required.")];
  if (blank(value)) return errors;

  if (question.type === "repeat_group") {
    const items = Array.isArray(value) ? value : [];
    if (question.required && items.length === 0) errors.push(fieldError(question, "At least one item is required."));
    if (typeof validation.min_repeats === "number" && items.length < validation.min_repeats) errors.push(fieldError(question, `At least ${validation.min_repeats} item(s) are required.`));
    if (typeof validation.max_repeats === "number" && items.length > validation.max_repeats) errors.push(fieldError(question, `No more than ${validation.max_repeats} item(s) are allowed.`));
    items.forEach((item, itemIndex) => {
      if (!item || typeof item !== "object") {
        errors.push(fieldError(question, `Repeat item ${itemIndex + 1} is invalid.`));
        return;
      }
      for (const nested of question.questions || []) {
        for (const nestedError of validateQuestion(nested, (item as Record<string, unknown>)[nested.key])) {
          errors.push({
            ...nestedError,
            key: `${question.key}.${itemIndex}.${nestedError.key}`,
            label: `${question.label} item ${itemIndex + 1}: ${nestedError.label}`,
          });
        }
      }
    });
    return errors;
  }

  if (question.type === "email" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(value))) errors.push(fieldError(question, "Enter a valid email address."));
  if (question.type === "phone" && !/^\+?[0-9][0-9\s().-]{6,}$/.test(String(value))) errors.push(fieldError(question, "Enter a valid phone number."));
  if (question.type === "url") {
    try {
      const parsed = new URL(String(value));
      if (!["http:", "https:"].includes(parsed.protocol)) errors.push(fieldError(question, "Enter a valid URL."));
    } catch {
      errors.push(fieldError(question, "Enter a valid URL."));
    }
  }

  if (["number", "decimal", "currency", "percentage", "compliance_score"].includes(question.type)) {
    const numeric = numberValue(value);
    if (numeric === null) errors.push(fieldError(question, "Enter a valid number."));
    if (numeric !== null && typeof validation.min_value === "number" && numeric < validation.min_value) errors.push(fieldError(question, `Value must be at least ${validation.min_value}.`));
    if (numeric !== null && typeof validation.max_value === "number" && numeric > validation.max_value) errors.push(fieldError(question, `Value must be no more than ${validation.max_value}.`));
  }

  if (typeof value === "string") {
    if (typeof validation.min_length === "number" && value.length < validation.min_length) errors.push(fieldError(question, `Enter at least ${validation.min_length} characters.`));
    if (typeof validation.max_length === "number" && value.length > validation.max_length) errors.push(fieldError(question, `Enter no more than ${validation.max_length} characters.`));
    if (typeof validation.regex === "string" && !new RegExp(validation.regex).test(value)) errors.push(fieldError(question, "Value does not match the required format."));
  }

  if (["single_choice", "dropdown", "likert", "rating", "risk_rating"].includes(question.type)) {
    const options = question.options?.length ? question.options : question.type === "risk_rating" ? ["Low", "Medium", "High", "Critical"] : [];
    if (options.length && !options.includes(String(value))) errors.push(fieldError(question, "Select one of the allowed options."));
  }
  if (question.type === "multiple_choice") {
    const selected = Array.isArray(value) ? value.map(String) : [];
    if (!Array.isArray(value)) errors.push(fieldError(question, "Select one or more options."));
    if (question.options?.length && selected.some((item) => !question.options?.includes(item))) errors.push(fieldError(question, "One or more selected options are not allowed."));
    if (typeof validation.min_selected === "number" && selected.length < validation.min_selected) errors.push(fieldError(question, `Select at least ${validation.min_selected} option(s).`));
    if (typeof validation.max_selected === "number" && selected.length > validation.max_selected) errors.push(fieldError(question, `Select no more than ${validation.max_selected} option(s).`));
  }

  if (question.type === "gps") {
    const coords = value && typeof value === "object" ? value as { latitude?: unknown; longitude?: unknown } : {};
    if (blank(coords.latitude) || blank(coords.longitude)) errors.push(fieldError(question, "Capture latitude and longitude."));
  }
  if (question.type === "signature" && blank(value)) errors.push(fieldError(question, "Signature is required."));
  if (["image_upload", "file_upload", "video_upload", "audio_upload"].includes(question.type)) {
    const files = Array.isArray(value) ? value : [];
    if (question.required && files.length === 0) errors.push(fieldError(question, "Upload at least one file."));
    if (typeof validation.min_files === "number" && files.length < validation.min_files) errors.push(fieldError(question, `Upload at least ${validation.min_files} file(s).`));
    if (typeof validation.max_files === "number" && files.length > validation.max_files) errors.push(fieldError(question, `Upload no more than ${validation.max_files} file(s).`));
    const allowedExtensions = csvRule(validation.allowed_file_types || validation.allowed_extensions);
    const allowedMimeTypes = csvRule(validation.allowed_mime_types);
    const maxFileSize = typeof validation.max_file_size === "number"
      ? validation.max_file_size
      : typeof validation.max_file_size_mb === "number"
        ? validation.max_file_size_mb * 1024 * 1024
        : null;
    files.forEach((file) => {
      const media = mediaMetadata(file);
      const extension = extensionFor(media.fileName);
      if (allowedExtensions.length && extension && !allowedExtensions.includes(extension)) errors.push(fieldError(question, `${media.fileName} is not an allowed file type.`));
      if (allowedMimeTypes.length && media.mimeType && !allowedMimeTypes.includes(media.mimeType.toLowerCase())) errors.push(fieldError(question, `${media.fileName} is not an allowed media type.`));
      if (maxFileSize !== null && media.fileSize !== null && media.fileSize > maxFileSize) errors.push(fieldError(question, `${media.fileName} exceeds the maximum file size.`));
    });
  }

  return errors;
}

export function validateKoboResponse(schema: KoboSchema, values: Record<string, unknown>, logic?: KoboLogic) {
  const errors: KoboValidationError[] = [];
  const logicState = evaluateKoboLogic(logic, values);
  for (const section of schema.sections || []) {
    if (logicState.hiddenSections.has(section.key)) continue;
    for (const question of section.questions || []) {
      if (logicState.hiddenQuestions.has(question.key)) continue;
      errors.push(...validateQuestion({ ...question, required: question.required || logicState.requiredQuestions.has(question.key) }, values[question.key]));
    }
  }
  return errors;
}
