/**
 * Proxy: /api/v1/* → backend:8000/api/v1/*
 * Handles long-running requests (up to 3 min) without the timeout
 * issues of Next.js rewrites.
 */
import { NextRequest, NextResponse } from 'next/server';

const BACKEND = process.env.BACKEND_URL ?? 'http://backend:8000';

async function proxy(req: NextRequest, path: string): Promise<NextResponse> {
  const url = `${BACKEND}/api/v1/${path}`;
  const init: RequestInit = {
    method: req.method,
    headers: { 'Content-Type': 'application/json' },
    signal: AbortSignal.timeout(200_000), // 200 s — well within 3-min SLA
  };

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    init.body = await req.text();
  }

  const res = await fetch(url, init);
  const body = await res.text();

  return new NextResponse(body, {
    status: res.status,
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
