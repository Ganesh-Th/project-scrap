// frontend/src/lib/api.ts
import {
  ScrapeRequest,
  TaskStatusResponse,
  PrioritizationRequest,
  PrioritizationResponse,
  ScrapeStartResponse,
} from "@/types/api";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

const API_V1 = `${API_BASE}/api/v1`;

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_V1}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function startScrape(payload: ScrapeRequest): Promise<ScrapeStartResponse> {
  return request<ScrapeStartResponse>("/scrape", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  return request<TaskStatusResponse>(`/task/${taskId}`, { method: "GET" });
}

export async function prioritize(
  payload: PrioritizationRequest
): Promise<PrioritizationResponse> {
  return request<PrioritizationResponse>("/prioritize", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}