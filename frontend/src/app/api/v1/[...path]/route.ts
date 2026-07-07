/**
 * Proxy: /api/v1/* → backend/api/v1/*
 * Handles auth token exchange automatically — frontend never exposes API_KEY to the browser.
 */
import { NextRequest, NextResponse } from 'next/server';

const BACKEND = (process.env.BACKEND_URL ?? 'http://backend:8000').replace(/\/$/, '');
const BACKEND_API_KEY = process.env.BACKEND_API_KEY ?? '';

// In-memory JWT cache — refreshed when expired or on 401
let cachedToken: string | null = null;
let tokenExpiresAt = 0;

async function getToken(): Promise<string | null> {
  if (!BACKEND_API_KEY) return null;
  if (cachedToken && Date.now() < tokenExpiresAt) return cachedToken;

  try {
    const res = await fetch(`${BACKEND}/api/v1/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: BACKEND_API_KEY }),
      signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) {
      console.error('[proxy] auth/token failed:', res.status, await res.text());
      return null;
    }
    const data = await res.json();
    cachedToken = data.access_token;
    tokenExpiresAt = Date.now() + 23 * 60 * 60 * 1000; // re-fetch 1h before 24h expiry
    return cachedToken;
  } catch (err) {
    console.error('[proxy] token exchange error:', err);
    return null;
  }
}

async function proxy(req: NextRequest, path: string): Promise<NextResponse> {
  const token = await getToken();

  const url = `${BACKEND}/api/v1/${path}`;
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const init: RequestInit = {
    method: req.method,
    headers,
    signal: AbortSignal.timeout(200_000),
  };

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    init.body = await req.text();
  }

  const res = await fetch(url, init);

  // If 401, clear cached token and retry once with a fresh one
  if (res.status === 401 && token) {
    cachedToken = null;
    tokenExpiresAt = 0;
    const freshToken = await getToken();
    if (freshToken) {
      headers['Authorization'] = `Bearer ${freshToken}`;
      const retry = await fetch(url, { ...init, headers });
      return buildResponse(retry);
    }
  }

  return buildResponse(res);
}

// 204/304 (and other no-body statuses) must not carry a Content-Type/body —
// the Fetch spec forbids it, and Next.js's NextResponse constructor throws
// "Invalid response status code 204" if you try. This bit the DELETE
// endpoints specifically (backend returns 204 on successful deletion),
// which is why the frontend never had a working delete flow to begin with
// — found while adding the delete-assessment UI, 2026-07-07.
async function buildResponse(upstream: Response): Promise<NextResponse> {
  if (upstream.status === 204 || upstream.status === 304) {
    return new NextResponse(null, { status: upstream.status });
  }
  const body = await upstream.text();
  return new NextResponse(body, {
    status: upstream.status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  return proxy(req, path.join('/'));
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  return proxy(req, path.join('/'));
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  return proxy(req, path.join('/'));
}
