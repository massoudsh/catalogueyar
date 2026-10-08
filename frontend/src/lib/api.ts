import { API_BASE_URL, API_KEY } from "./config";
import {
  CatalogDraftSchema,
  CatalogGenerateResponseSchema,
  HealthSchema,
  type CatalogDraft,
  type CatalogGenerateResponse,
  type CatalogUpdate,
} from "./schemas";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function authHeaders(json = false): HeadersInit {
  const headers: Record<string, string> = {};
  if (json) headers["Content-Type"] = "application/json";
  if (API_KEY) headers.Authorization = `Bearer ${API_KEY}`;
  return headers;
}

async function parseDetail(response: Response): Promise<string> {
  try {
    const data: unknown = await response.json();
    if (
      data &&
      typeof data === "object" &&
      "detail" in data &&
      (typeof (data as { detail: unknown }).detail === "string" ||
        Array.isArray((data as { detail: unknown }).detail))
    ) {
      const detail = (data as { detail: string | Array<{ msg?: string }> }).detail;
      if (typeof detail === "string") return detail;
      return detail.map((item) => item.msg ?? "خطای اعتبارسنجی").join("؛ ");
    }
  } catch {
    /* ignore */
  }
  return `خطای سرور (${response.status})`;
}

async function request<T>(
  path: string,
  init: RequestInit,
  parse: (data: unknown) => T,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    throw new ApiError(await parseDetail(response), response.status);
  }
  const data: unknown = await response.json();
  return parse(data);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const data = await request("/health", { method: "GET" }, (raw) =>
      HealthSchema.parse(raw),
    );
    return data.status === "ok";
  } catch {
    return false;
  }
}

export type GeneratePayload = {
  images: File[];
  voiceNote?: File | null;
  sellerHint?: string;
  storeCategories?: string[];
};

export async function generateCatalog(
  payload: GeneratePayload,
): Promise<CatalogGenerateResponse> {
  const body = new FormData();
  payload.images.forEach((file) => body.append("images", file));
  if (payload.voiceNote) body.append("voice_note", payload.voiceNote);
  if (payload.sellerHint?.trim()) body.append("seller_hint", payload.sellerHint.trim());
  payload.storeCategories?.forEach((category) => {
    if (category.trim()) body.append("store_category_list", category.trim());
  });

  return request(
    "/catalog/generate",
    { method: "POST", headers: authHeaders(false), body },
    (raw) => CatalogGenerateResponseSchema.parse(raw),
  );
}

export async function listHistory(): Promise<CatalogDraft[]> {
  return request("/catalog/history", { method: "GET", headers: authHeaders() }, (raw) =>
    CatalogDraftSchema.array().parse(raw),
  );
}

export async function getDraft(draftId: string): Promise<CatalogDraft> {
  return request(
    `/catalog/${draftId}`,
    { method: "GET", headers: authHeaders() },
    (raw) => CatalogDraftSchema.parse(raw),
  );
}

export async function updateDraft(
  draftId: string,
  update: CatalogUpdate,
): Promise<CatalogDraft> {
  return request(
    `/catalog/${draftId}`,
    {
      method: "PATCH",
      headers: authHeaders(true),
      body: JSON.stringify(update),
    },
    (raw) => CatalogDraftSchema.parse(raw),
  );
}
