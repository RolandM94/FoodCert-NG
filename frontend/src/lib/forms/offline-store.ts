import type { OfflineFormPackage } from "@/lib/api/forms";

type OfflineDraft = {
  responseId: string;
  assignmentId?: string;
  values: Record<string, unknown>;
  updatedAt: string;
  status: "draft_saved_locally" | "ready_to_sync" | "sync_failed" | "synced";
  lastError?: string;
};

export type OfflineSyncPayload = {
  localResponseId: string;
  responseId: string;
  assignmentId?: string;
  operationType: "save_draft" | "submit_response";
  values: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  status: "ready_to_sync" | "syncing" | "sync_failed" | "synced";
  lastError?: string;
};

const DB_NAME = "foodcert_forms_offline";
const DB_VERSION = 1;
const PACKAGE_STORE = "packages";
const DRAFT_STORE = "drafts";
const SYNC_STORE = "sync_queue";
const SYNC_RESPONSE_PREFIX = "response:";

function canUseIndexedDb() {
  return typeof window !== "undefined" && "indexedDB" in window;
}

function fallbackKey(store: string, key: string) {
  return `${DB_NAME}:${store}:${key}`;
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = window.indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(PACKAGE_STORE)) db.createObjectStore(PACKAGE_STORE);
      if (!db.objectStoreNames.contains(DRAFT_STORE)) db.createObjectStore(DRAFT_STORE);
      if (!db.objectStoreNames.contains(SYNC_STORE)) db.createObjectStore(SYNC_STORE);
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function idbGet<T>(store: string, key: string): Promise<T | null> {
  if (!canUseIndexedDb()) {
    const raw = window.localStorage.getItem(fallbackKey(store, key));
    return raw ? JSON.parse(raw) as T : null;
  }
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, "readonly");
    const request = tx.objectStore(store).get(key);
    request.onsuccess = () => resolve((request.result as T | undefined) ?? null);
    request.onerror = () => reject(request.error);
    tx.oncomplete = () => db.close();
  });
}

async function idbSet<T>(store: string, key: string, value: T) {
  if (!canUseIndexedDb()) {
    window.localStorage.setItem(fallbackKey(store, key), JSON.stringify(value));
    return;
  }
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(store, "readwrite");
    tx.objectStore(store).put(value, key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

async function idbDelete(store: string, key: string) {
  if (!canUseIndexedDb()) {
    window.localStorage.removeItem(fallbackKey(store, key));
    return;
  }
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(store, "readwrite");
    tx.objectStore(store).delete(key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

export async function saveOfflinePackage(responseId: string, formPackage: OfflineFormPackage) {
  await idbSet(PACKAGE_STORE, responseId, formPackage);
}

export async function getOfflinePackage(responseId: string) {
  return idbGet<OfflineFormPackage>(PACKAGE_STORE, responseId);
}

export async function saveOfflineDraft(draft: OfflineDraft) {
  await idbSet(DRAFT_STORE, draft.responseId, draft);
}

export async function getOfflineDraft(responseId: string) {
  return idbGet<OfflineDraft>(DRAFT_STORE, responseId);
}

export async function queueOfflineSync(payload: OfflineSyncPayload) {
  await idbSet(SYNC_STORE, payload.localResponseId, payload);
  await idbSet(SYNC_STORE, `${SYNC_RESPONSE_PREFIX}${payload.responseId}`, payload);
  await saveOfflineDraft({
    responseId: payload.responseId,
    assignmentId: payload.assignmentId,
    values: payload.values,
    updatedAt: payload.updatedAt,
    status: payload.status === "sync_failed" ? "sync_failed" : "ready_to_sync",
    lastError: payload.lastError,
  });
}

export async function getOfflineSyncPayload(localResponseId: string) {
  return idbGet<OfflineSyncPayload>(SYNC_STORE, localResponseId);
}

export async function getOfflineSyncPayloadForResponse(responseId: string) {
  return idbGet<OfflineSyncPayload>(SYNC_STORE, `${SYNC_RESPONSE_PREFIX}${responseId}`);
}

export async function removeOfflineSyncPayload(localResponseId: string, responseId?: string) {
  await idbDelete(SYNC_STORE, localResponseId);
  if (responseId) await idbDelete(SYNC_STORE, `${SYNC_RESPONSE_PREFIX}${responseId}`);
}

export function makeLocalResponseId(responseId: string) {
  return `${responseId}-${Date.now()}`;
}
