const rawBase = import.meta.env.VITE_API_BASE_URL?.trim();

/** API origin. Empty string uses the deployed backend on the same origin or Vite's local proxy. */
export const API_BASE_URL = rawBase?.replace(/\/$/, "") ?? "";

export const API_KEY = import.meta.env.VITE_API_KEY?.trim() || "";

export const LOW_CONFIDENCE = 0.7;
