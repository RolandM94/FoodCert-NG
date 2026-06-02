import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json"
  }
});

export type ApiEnvelope<T> = {
  success: boolean;
  data: T;
  message: string;
  meta?: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
};

type ApiErrorEnvelope = {
  error?: string;
  details?: {
    detail?: string;
  };
};

export function unwrap<T>(envelope: ApiEnvelope<T>): T {
  return envelope.data;
}

export function getApiErrorMessage(error: unknown, fallback: string) {
  if (!axios.isAxiosError<ApiErrorEnvelope>(error)) {
    return error instanceof Error ? error.message : fallback;
  }
  return error.response?.data?.error ?? error.response?.data?.details?.detail ?? fallback;
}

function clearAuthStorage() {
  window.localStorage.removeItem("foodcert_access_token");
  window.localStorage.removeItem("foodcert_refresh_token");
  window.localStorage.removeItem("foodcert_user_role");
  window.localStorage.removeItem("foodcert_user_meta");
}

function redirectToLogin() {
  if (window.location.pathname === "/login") return;
  const next = `${window.location.pathname}${window.location.search}`;
  window.location.assign(`/login?next=${encodeURIComponent(next)}`);
}

apiClient.interceptors.request.use((config) => {
  if (typeof window === "undefined") {
    return config;
  }

  const token = window.localStorage.getItem("foodcert_access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

let refreshRequest: Promise<string> | null = null;

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (typeof window === "undefined" || error.response?.status !== 401) {
      return Promise.reject(error);
    }

    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const requestUrl = original?.url ?? "";
    const isAuthRequest = requestUrl.includes("/auth/login/") || requestUrl.includes("/auth/token/refresh/");
    const refresh = window.localStorage.getItem("foodcert_refresh_token");

    if (!original || original._retry || isAuthRequest || !refresh) {
      clearAuthStorage();
      if (!isAuthRequest) redirectToLogin();
      return Promise.reject(error);
    }

    original._retry = true;
    try {
      refreshRequest ??= axios
        .post<ApiEnvelope<{ access: string }>>(`${apiClient.defaults.baseURL}/auth/token/refresh/`, { refresh })
        .then((response) => unwrap(response.data).access)
        .finally(() => {
          refreshRequest = null;
        });

      const access = await refreshRequest;
      window.localStorage.setItem("foodcert_access_token", access);
      original.headers.Authorization = `Bearer ${access}`;
      return apiClient(original);
    } catch (refreshError) {
      clearAuthStorage();
      redirectToLogin();
      return Promise.reject(refreshError);
    }
  }
);
