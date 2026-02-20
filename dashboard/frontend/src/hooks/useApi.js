/**
 * Shared API fetch wrapper.
 * All calls go to the Flask backend (proxied by Vite in dev, same-origin in prod).
 */

const BASE = '';  // same origin — Vite proxy handles /api in dev

export async function apiFetch(path, options = {}) {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export function apiGet(path) {
  return apiFetch(path);
}

export function apiPut(path, body) {
  return apiFetch(path, { method: 'PUT', body: JSON.stringify(body) });
}

export function apiPost(path, body = {}) {
  return apiFetch(path, { method: 'POST', body: JSON.stringify(body) });
}
