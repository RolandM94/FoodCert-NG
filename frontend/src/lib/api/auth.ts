import { apiClient, unwrap, type ApiEnvelope } from "@/lib/api/client";
import type { AuthenticatedUser, AuthTokens, UserRole } from "@/types/auth";

type RegisterPayload = {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  role?: Extract<UserRole, "food_handler" | "employer">;
};

export async function register(payload: RegisterPayload) {
  const response = await apiClient.post<ApiEnvelope<AuthenticatedUser>>("/auth/register/", payload);
  return unwrap(response.data);
}

export async function login(username: string, password: string): Promise<AuthTokens> {
  const response = await apiClient.post<ApiEnvelope<AuthTokens>>("/auth/login/", {
    username,
    password
  });
  return unwrap(response.data);
}

export async function logout(refresh: string) {
  await apiClient.post("/auth/logout/", { refresh });
}

export async function getCurrentUser() {
  const response = await apiClient.get<ApiEnvelope<AuthenticatedUser>>("/users/me/");
  return unwrap(response.data);
}
