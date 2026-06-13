"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, RefreshCw, Save, Send, WifiOff } from "lucide-react";
import { PortalShell } from "@/components/layout/portal-shell";
import { StatusBadge } from "@/components/status/status-badge";
import {
  KoboFormRenderer,
  type KoboMediaUploadContext,
  type KoboMediaUploadStatus,
  type KoboQuestion,
  type KoboSchema,
} from "@/components/forms/kobo-form-renderer";
import { fetchFormResponse, fetchOfflineAssignmentPackage, saveFormResponseDraft, submitFormResponse, syncOfflineFormResponse, uploadFormResponseAttachment, type FormResponse } from "@/lib/api/forms";
import { getApiErrorMessage } from "@/lib/api/client";
import { validateKoboResponse, type KoboValidationError } from "@/lib/forms/kobo-validation";
import type { KoboLogic } from "@/lib/forms/kobo-logic";
import {
  getOfflineDraft,
  getOfflinePackage,
  getOfflineSyncPayloadForResponse,
  makeLocalResponseId,
  queueOfflineSync,
  removeOfflineSyncPayload,
  saveOfflineDraft,
  saveOfflinePackage,
  type OfflineSyncPayload,
} from "@/lib/forms/offline-store";

function schemaFromResponse(value?: Record<string, unknown>): KoboSchema {
  return {
    sections: Array.isArray(value?.sections) ? value.sections as KoboSchema["sections"] : [],
  };
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [values, setValues] = useState<Record<string, unknown>>({});
  const [error, setError] = useState("");
  const [validationErrors, setValidationErrors] = useState<KoboValidationError[]>([]);
  const [success, setSuccess] = useState("");
  const [mediaUploadStatuses, setMediaUploadStatuses] = useState<Record<string, KoboMediaUploadStatus>>({});
  const [cachedResponse, setCachedResponse] = useState<FormResponse | null>(null);
  const [offlineDraftStatus, setOfflineDraftStatus] = useState("");
  const [syncPayload, setSyncPayload] = useState<OfflineSyncPayload | null>(null);
  const [isOnline, setIsOnline] = useState(true);

  const responseQuery = useQuery({
    queryKey: ["form-response", params.id],
    queryFn: async () => fetchFormResponse(params.id),
  });

  useEffect(() => {
    setIsOnline(typeof navigator === "undefined" ? true : navigator.onLine);
    const updateOnline = () => setIsOnline(true);
    const updateOffline = () => setIsOnline(false);
    window.addEventListener("online", updateOnline);
    window.addEventListener("offline", updateOffline);
    return () => {
      window.removeEventListener("online", updateOnline);
      window.removeEventListener("offline", updateOffline);
    };
  }, []);

  useEffect(() => {
    let active = true;
    async function loadOfflineState() {
      const [draft, formPackage, queued] = await Promise.all([getOfflineDraft(params.id), getOfflinePackage(params.id), getOfflineSyncPayloadForResponse(params.id)]);
      if (!active) return;
      if (draft) {
        setValues((current) => Object.keys(current).length ? current : draft.values);
        setOfflineDraftStatus(`Local draft saved ${new Date(draft.updatedAt).toLocaleString()}`);
      }
      if (formPackage?.response) setCachedResponse(formPackage.response);
      if (queued) setSyncPayload(queued);
    }
    loadOfflineState().catch(() => undefined);
    return () => {
      active = false;
    };
  }, [params.id]);

  const response = responseQuery.data || cachedResponse;
  const schema = schemaFromResponse(response?.template_schema);
  const logic = (response?.template_logic || {}) as KoboLogic;
  const currentValues = Object.keys(values).length ? values : response?.response_json || {};
  const readOnly = Boolean(response && ["submitted", "reviewed", "approved", "rejected", "cancelled"].includes(response.status));

  const saveMut = useMutation({
    mutationFn: async () => saveFormResponseDraft(params.id, { response_json: currentValues }),
    onSuccess: () => {
      setError("");
      setSuccess("Draft saved.");
      queryClient.invalidateQueries({ queryKey: ["form-response", params.id] });
    },
    onError: (err) => {
      setSuccess("");
      setError(getApiErrorMessage(err, "Could not save draft."));
    },
  });

  const downloadOfflineMut = useMutation({
    mutationFn: async () => {
      if (!response?.assignment) throw new Error("Load the form before downloading it offline.");
      return fetchOfflineAssignmentPackage(response.assignment);
    },
    onSuccess: async (formPackage) => {
      if (formPackage.response) {
        await saveOfflinePackage(formPackage.response.id, formPackage);
        setCachedResponse(formPackage.response);
      }
      setError("");
      setSuccess("Form is available offline on this device.");
    },
    onError: (err) => {
      setSuccess("");
      setError(getApiErrorMessage(err, "Could not download this form for offline use."));
    },
  });

  const submitMut = useMutation({
    mutationFn: async () => submitFormResponse(params.id, { response_json: currentValues }),
    onSuccess: () => {
      setError("");
      setValidationErrors([]);
      setSuccess("Response submitted.");
      queryClient.invalidateQueries({ queryKey: ["form-response", params.id] });
    },
    onError: (err: unknown) => {
      setSuccess("");
      const apiErrors = typeof err === "object" && err && "response" in err
        ? (err as { response?: { data?: { errors?: KoboValidationError[] } } }).response?.data?.errors
        : undefined;
      if (Array.isArray(apiErrors)) setValidationErrors(apiErrors);
      setError(getApiErrorMessage(err, "Could not submit response."));
    },
  });

  async function saveLocalDraft(nextValues = currentValues, status: "draft_saved_locally" | "ready_to_sync" | "sync_failed" | "synced" = "draft_saved_locally", lastError?: string) {
    if (!response) return;
    const updatedAt = new Date().toISOString();
    await saveOfflineDraft({
      responseId: response.id,
      assignmentId: response.assignment,
      values: nextValues,
      updatedAt,
      status,
      lastError,
    });
    setOfflineDraftStatus(status === "sync_failed" ? lastError || "Sync failed. Local copy is still saved." : `Local draft saved ${new Date(updatedAt).toLocaleString()}`);
  }

  async function handleSaveDraft() {
    if (!isOnline) {
      await saveLocalDraft();
      setSuccess("Draft saved locally. It will stay on this device until you sync.");
      setError("");
      return;
    }
    try {
      await saveMut.mutateAsync();
      await saveLocalDraft(currentValues, "synced");
    } catch {
      await saveLocalDraft();
    }
  }

  async function queueSubmitForSync(reason = "Offline submission queued. Retry sync when connection returns.") {
    if (!response) return;
    const localResponseId = makeLocalResponseId(response.id);
    const now = new Date().toISOString();
    const payload: OfflineSyncPayload = {
      localResponseId,
      responseId: response.id,
      assignmentId: response.assignment,
      operationType: "submit_response",
      values: currentValues,
      createdAt: now,
      updatedAt: now,
      status: "ready_to_sync",
    };
    await queueOfflineSync(payload);
    setSyncPayload(payload);
    setSuccess(reason);
    setError("");
  }

  async function handleSubmitWithOffline() {
    const errors = validateKoboResponse(schema, currentValues, logic);
    setValidationErrors(errors);
    setSuccess("");
    if (errors.length) {
      setError("Please fix the highlighted fields before submitting.");
      return;
    }
    if (!isOnline) {
      await queueSubmitForSync();
      return;
    }
    try {
      await submitMut.mutateAsync();
    } catch (err) {
      const hasServerResponse = typeof err === "object" && err && "response" in err;
      if (!hasServerResponse) {
        await queueSubmitForSync("Connection dropped. Submission saved locally for retry.");
      }
    }
  }

  async function retrySync() {
    const queued = syncPayload || await getOfflineSyncPayloadForResponse(params.id);
    if (!queued) return;
    setSyncPayload({ ...queued, status: "syncing" });
    try {
      const result = await syncOfflineFormResponse({
        local_response_id: queued.localResponseId,
        operation_type: queued.operationType,
        payload_json: {
          assignment_id: queued.assignmentId,
          response_id: queued.responseId,
          response_json: queued.values,
          offline_created_at: queued.createdAt,
        },
      });
      if (result.status === "synced") {
        await removeOfflineSyncPayload(queued.localResponseId, queued.responseId);
        setSyncPayload(null);
        setSuccess("Offline response synced.");
        setError("");
        queryClient.invalidateQueries({ queryKey: ["form-response", params.id] });
      } else {
        const failed = { ...queued, status: "sync_failed" as const, lastError: result.error || "Sync failed." };
        await queueOfflineSync(failed);
        setSyncPayload(failed);
        setError(failed.lastError || "Sync failed.");
      }
    } catch (err) {
      const failed = { ...queued, status: "sync_failed" as const, lastError: getApiErrorMessage(err, "Sync failed. Try again.") };
      await queueOfflineSync(failed);
      setSyncPayload(failed);
      setError(failed.lastError || "Sync failed. Try again.");
    }
  }

  async function handleMediaUpload(_question: KoboQuestion, file: File, context: KoboMediaUploadContext) {
    setMediaUploadStatuses((current) => ({ ...current, [context.fieldKey]: { state: "uploading" } }));
    if (!isOnline) {
      setMediaUploadStatuses((current) => ({ ...current, [context.fieldKey]: { state: "uploaded", message: "Stored locally" } }));
      return {
        file_name: file.name,
        file_size: file.size,
        mime_type: file.type,
        file_type: file.type.split("/")[0] || "file",
        sync_status: "local_pending",
        metadata_json: { field_key: context.fieldKey, local_only: true },
      };
    }
    try {
      const attachment = await uploadFormResponseAttachment(params.id, {
        question_key: context.questionKey,
        repeat_group_key: context.repeatGroupKey,
        repeat_item_id: context.repeatItemId,
        file,
        metadata_json: {
          source: "online_response",
          field_key: context.fieldKey,
          captured_at: new Date().toISOString(),
        },
      });
      setMediaUploadStatuses((current) => ({ ...current, [context.fieldKey]: { state: "uploaded", message: attachment.file_name } }));
      return {
        id: attachment.id,
        file_name: attachment.file_name,
        file_size: attachment.file_size,
        mime_type: attachment.mime_type,
        file_type: attachment.file_type,
        file_url: attachment.file_url || attachment.file,
        sync_status: attachment.sync_status,
        uploaded_at: attachment.created_at,
      };
    } catch (err) {
      setMediaUploadStatuses((current) => ({
        ...current,
        [context.fieldKey]: { state: "failed", message: getApiErrorMessage(err, "Upload failed. Try again.") },
      }));
      throw err;
    }
  }

  return (
    <PortalShell role="state_admin" title={response?.template_title || "Assigned form"} description={response?.assignment_title || "Complete assigned FoodCert form."}>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
          <div>
            <p className="text-xs font-bold uppercase text-neutral-500">Response status</p>
            <div className="mt-2"><StatusBadge status={response?.status || "loading"} /></div>
          </div>
          <div className="flex gap-2">
            <button className="inline-flex h-10 items-center gap-2 rounded border border-neutral-200 px-4 text-sm font-bold text-neutral-700 disabled:opacity-50" disabled={!response || downloadOfflineMut.isPending} type="button" onClick={() => downloadOfflineMut.mutate()}><Download size={16} /> Offline</button>
            <button className="inline-flex h-10 items-center gap-2 rounded border border-brand-200 px-4 text-sm font-bold text-brand-700 disabled:opacity-50" disabled={!response || readOnly || saveMut.isPending} type="button" onClick={handleSaveDraft}><Save size={16} /> Save draft</button>
            <button className="inline-flex h-10 items-center gap-2 rounded bg-brand-600 px-4 text-sm font-bold text-white disabled:opacity-50" disabled={!response || readOnly || submitMut.isPending} type="button" onClick={handleSubmitWithOffline}><Send size={16} /> Submit</button>
          </div>
        </div>

        {!isOnline ? <p className="rounded border border-warning-100 bg-warning-50 px-3 py-2 text-sm font-semibold text-warning-800"><WifiOff className="mr-2 inline" size={15} />You are offline. Drafts and submissions will be kept on this device until synced.</p> : null}
        {offlineDraftStatus ? <p className="rounded border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-600">{offlineDraftStatus}</p> : null}
        {syncPayload ? (
          <div className="flex flex-wrap items-center justify-between gap-3 rounded border border-warning-100 bg-white p-3">
            <p className="text-sm font-semibold text-warning-800">A local submission is waiting to sync.</p>
            <button className="inline-flex h-9 items-center gap-2 rounded border border-warning-200 px-3 text-xs font-bold text-warning-800 disabled:opacity-50" disabled={!isOnline || syncPayload.status === "syncing"} onClick={retrySync} type="button"><RefreshCw size={14} /> Retry sync</button>
          </div>
        ) : null}
        {error ? <p className="rounded border border-danger-100 bg-danger-50 px-3 py-2 text-sm font-semibold text-danger-700">{error}</p> : null}
        {validationErrors.length ? (
          <div className="rounded border border-danger-100 bg-white p-4">
            <p className="text-sm font-bold text-danger-700">Validation errors</p>
            <ul className="mt-2 space-y-1 text-sm text-danger-700">
              {validationErrors.map((item) => <li key={`${item.key}-${item.message}`}>{item.label}: {item.message}</li>)}
            </ul>
          </div>
        ) : null}
        {success ? <p className="rounded border border-brand-100 bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-800">{success}</p> : null}

        {responseQuery.isLoading ? <p className="rounded border border-neutral-200 bg-white p-6 text-sm text-neutral-500">Loading form...</p> : null}
        {!responseQuery.isLoading && !schema.sections.length ? <p className="rounded border border-neutral-200 bg-white p-6 text-sm text-neutral-500">This form does not have a published schema yet.</p> : null}
        {schema.sections.length ? <KoboFormRenderer schema={schema} values={currentValues} onChange={(nextValues) => { setValues(nextValues); saveLocalDraft(nextValues).catch(() => undefined); }} readOnly={readOnly} errors={validationErrors} logic={logic} onMediaUpload={handleMediaUpload} mediaUploadStatuses={mediaUploadStatuses} /> : null}
      </div>
    </PortalShell>
  );
}
