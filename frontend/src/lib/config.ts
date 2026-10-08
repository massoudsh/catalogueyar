const rawBase = import.meta.env.VITE_API_BASE_URL?.trim();

/** API origin. Empty string uses same-origin / Vite proxy. */
export const API_BASE_URL =
  rawBase === undefined || rawBase === ""
    ? "http://127.0.0.1:8000"
    : rawBase.replace(/\/$/, "");

export const API_KEY = import.meta.env.VITE_API_KEY?.trim() || "";

export const LOW_CONFIDENCE = 0.7;
