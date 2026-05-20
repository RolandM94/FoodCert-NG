import axios from "axios";

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

export function unwrap<T>(envelope: ApiEnvelope<T>): T {
  return envelope.data;
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
