'use client';

import { useEffect } from 'react';

/**
 * Fire-and-forget backend warm-up ping, mounted once in the root layout.
 * Pings our own /api/warmup route (server-side, avoids CORS) which in turn
 * pings the backend's health endpoint. See route.ts for the full rationale
 * (Render free-tier services spin down and wake up independently).
 *
 * Renders nothing. Never surfaces errors to the user — a slow or failed
 * warm-up ping must never affect the page.
 */
export function BackendWarmup() {
  useEffect(() => {
    fetch('/api/warmup', { cache: 'no-store' }).catch(() => {
      // Intentionally swallowed — warm-up is best-effort only.
    });
  }, []);

  return null;
}
