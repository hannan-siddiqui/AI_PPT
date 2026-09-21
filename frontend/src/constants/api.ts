export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

export function getApiUrl(path: string): string {
  if (!path) return API_BASE;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${cleanPath}`;
}
